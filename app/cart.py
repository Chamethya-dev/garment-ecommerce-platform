from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_required, current_user
from decimal import Decimal
import urllib.parse
from app import db
from app.models import ProductVariant, Order, OrderItem, ShippingZone

cart = Blueprint('cart', __name__)

@cart.route('/cart')
def view_cart():
    cart_items = session.get('cart', {})
    items = []
    total = Decimal(0)
    
    for variant_id, qty in cart_items.items():
        variant = ProductVariant.query.get(variant_id)
        if variant:
            price = Decimal(variant.product.sale_price or variant.product.regular_price)
            subtotal = price * qty
            total += subtotal
            
            stock_status = 'in_stock'
            if variant.stock_quantity < qty:
                stock_status = 'low_stock' if variant.stock_quantity > 0 else 'out_of_stock'
            
            items.append({
                'variant': variant,
                'quantity': qty,
                'price': price,
                'subtotal': subtotal,
                'stock_available': variant.stock_quantity,
                'stock_status': stock_status
            })
            
    return render_template('cart.html', items=items, total=total)

@cart.route('/cart/add', methods=['POST'])
def add_to_cart():
    variant_id = str(request.form.get('variant_id'))
    quantity = int(request.form.get('quantity', 1))
    
    variant = ProductVariant.query.get(variant_id)
    if not variant:
        flash('Product variant not found!', 'danger')
        return redirect(url_for('main.shop'))
    
    if variant.stock_quantity < quantity:
        flash(f'Sorry, we only have {variant.stock_quantity} unit(s) in stock for {variant.product.name}.', 'warning')
        return redirect(url_for('main.product_detail', product_id=variant.product_id))
    
    user_cart = session.get('cart', {})
    current_qty_in_cart = user_cart.get(variant_id, 0)
    
    if current_qty_in_cart + quantity > variant.stock_quantity:
        available = variant.stock_quantity - current_qty_in_cart
        if available <= 0:
            flash(f'Sorry, {variant.product.name} is already at maximum quantity in your cart.', 'warning')
        else:
            flash(f'Only {available} more unit(s) can be added. Stock limit reached.', 'warning')
        return redirect(url_for('main.product_detail', product_id=variant.product_id))
    
    if variant_id in user_cart:
        user_cart[variant_id] += quantity
    else:
        user_cart[variant_id] = quantity
    
    session['cart'] = user_cart
    flash(f'{variant.product.name} added to cart!', 'success')
    return redirect(url_for('cart.view_cart'))

@cart.route('/cart/update', methods=['POST'])
def update_cart():
    variant_id = str(request.form.get('variant_id'))
    quantity = int(request.form.get('quantity'))
    
    variant = ProductVariant.query.get(variant_id)
    
    if quantity <= 0:
        user_cart = session.get('cart', {})
        user_cart.pop(variant_id, None)
        session['cart'] = user_cart
        flash('Item removed from cart.', 'info')
    elif variant:
        if quantity > variant.stock_quantity:
            flash(f'Sorry, we only have {variant.stock_quantity} unit(s) in stock for {variant.product.name}.', 'warning')
            quantity = variant.stock_quantity
        
        user_cart = session.get('cart', {})
        user_cart[variant_id] = quantity
        session['cart'] = user_cart
        flash('Cart updated!', 'success')
    else:
        flash('Product variant not found!', 'danger')
    
    return redirect(url_for('cart.view_cart'))

@cart.route('/cart/remove/<variant_id>')
def remove_from_cart(variant_id):
    user_cart = session.get('cart', {})
    user_cart.pop(variant_id, None)
    session['cart'] = user_cart
    flash('Item removed from cart.', 'info')
    return redirect(url_for('cart.view_cart'))

@cart.route('/checkout')
@login_required
def checkout():
    cart_items = session.get('cart', {})
    if not cart_items:
        flash('Your cart is empty!', 'warning')
        return redirect(url_for('main.shop'))
    
    for variant_id, qty in cart_items.items():
        variant = ProductVariant.query.get(variant_id)
        if not variant or variant.stock_quantity < qty:
            flash(f'Stock updated for {variant.product.name if variant else "an item"}. Please review your cart.', 'warning')
            return redirect(url_for('cart.view_cart'))
        
    total = Decimal(0)
    for variant_id, qty in cart_items.items():
        variant = ProductVariant.query.get(variant_id)
        if variant:
            price = Decimal(variant.product.sale_price or variant.product.regular_price)
            total += price * qty
            
    zones = ShippingZone.query.all()
    return render_template('checkout.html', total=total, zones=zones)

@cart.route('/order/place', methods=['POST'])
@login_required
def place_order():
    cart_items = session.get('cart', {})
    if not cart_items:
        return redirect(url_for('main.shop'))
        
    delivery_fee = Decimal(request.form.get('delivery_fee', 0))
    shipping_district = request.form.get('shipping_district', 'Unknown')
    shipping_address = request.form.get('shipping_address', '')
    payment_method = request.form.get('payment_method', 'Cash on Delivery')
    
    if payment_method == 'Bank Deposit':
        order_status = 'Awaiting Payment'
    else:
        order_status = 'Pending'
    
    subtotal = Decimal(0)
    order_items_data = []
    
    for variant_id, qty in cart_items.items():
        variant = ProductVariant.query.get(variant_id)
        if not variant:
            flash(f'Product variant not found!', 'danger')
            return redirect(url_for('cart.view_cart'))
            
        if variant.stock_quantity < qty:
            flash(f'Sorry, {variant.product.name} is now out of stock or has limited availability. Please update your cart.', 'danger')
            return redirect(url_for('cart.view_cart'))
            
        price = Decimal(variant.product.sale_price or variant.product.regular_price)
        subtotal += price * qty
        order_items_data.append({'variant': variant, 'qty': qty, 'price': price})
        
    total_amount = subtotal + delivery_fee
    
    new_order = Order(
        user_id=current_user.user_id,
        subtotal=subtotal,
        delivery_fee=delivery_fee,
        total_amount=total_amount,
        shipping_district=shipping_district,
        shipping_address=shipping_address,
        payment_method=payment_method,
        status=order_status
    )
    db.session.add(new_order)
    db.session.flush() 
    
    for item in order_items_data:
        order_item = OrderItem(
            order_id=new_order.order_id,
            variant_id=item['variant'].variant_id,
            quantity=item['qty'],
            unit_price=item['price']
        )
        db.session.add(order_item)
        item['variant'].stock_quantity -= item['qty']
        
    db.session.commit()
    session['cart'] = {}
    
    # --- WHATSAPP MESSAGE GENERATION ---
    saved_order = Order.query.get(new_order.order_id)
    items_list = "\n".join([f"- {item.variant.product.name} ({item.variant.size}) x{item.quantity}" for item in saved_order.items])
    
    message = f"🌸 *NEW ORDER - MANSA Clothing*\n\n"
    message += f"*Order ID:* #{saved_order.order_id}\n"
    message += f"*Customer:* {current_user.name}\n"
    message += f"*Phone:* {current_user.phone}\n\n"
    message += f" *Items:*\n{items_list}\n\n"
    message += f"💰 *Subtotal:* Rs. {saved_order.subtotal}\n"
    message += f"🚚 *Delivery ({saved_order.shipping_district}):* Rs. {saved_order.delivery_fee}\n"
    message += f" *TOTAL:* Rs. {saved_order.total_amount}\n\n"
    message += f"📍 *Delivery Address:*\n{saved_order.shipping_address}\n\n"
    
    if saved_order.payment_method == 'Bank Deposit':
        message += f" *Payment:* Bank Deposit\n"
        message += f"🏦 Bank: BOC Akuressa\n"
        message += f"📎 *I will send the payment slip in the next message.*\n\n"
    else:
        message += f"💳 *Payment:* Cash on Delivery\n"
        message += f"💵 *Amount to Pay:* Rs. {saved_order.total_amount} (in cash)\n\n"
        
    message += "Please confirm my order. Thank you!"

    encoded_message = urllib.parse.quote(message.encode('utf-8'))
    whatsapp_number = "94771391827" # <--- CHANGE THIS TO YOUR NUMBER
    whatsapp_url = f"https://wa.me/{whatsapp_number}?text={encoded_message}"
    
    flash('Order placed successfully!', 'success')
    return render_template('order_success.html', order_id=new_order.order_id, whatsapp_url=whatsapp_url)