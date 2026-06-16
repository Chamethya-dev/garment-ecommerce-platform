from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_required, current_user
from decimal import Decimal
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
            items.append({
                'variant': variant,
                'quantity': qty,
                'price': price,
                'subtotal': subtotal
            })
            
    return render_template('cart.html', items=items, total=total)

@cart.route('/cart/add', methods=['POST'])
def add_to_cart():
    variant_id = str(request.form.get('variant_id'))
    quantity = int(request.form.get('quantity', 1))
    
    user_cart = session.get('cart', {})
    if variant_id in user_cart:
        user_cart[variant_id] += quantity
    else:
        user_cart[variant_id] = quantity
    session['cart'] = user_cart
    
    flash('Item added to cart!', 'success')
    return redirect(url_for('cart.view_cart'))

@cart.route('/cart/update', methods=['POST'])
def update_cart():
    variant_id = str(request.form.get('variant_id'))
    quantity = int(request.form.get('quantity'))
    
    user_cart = session.get('cart', {})
    if quantity > 0:
        user_cart[variant_id] = quantity
    else:
        user_cart.pop(variant_id, None)
    session['cart'] = user_cart
    
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
        
    # FIX: Use Decimal instead of float for financial calculations
    delivery_fee = Decimal(request.form.get('delivery_fee', 0))
    shipping_district = request.form.get('shipping_district', 'Unknown')
    shipping_address = request.form.get('shipping_address', '')
    
    subtotal = Decimal(0)
    order_items_data = []
    
    for variant_id, qty in cart_items.items():
        variant = ProductVariant.query.get(variant_id)
        if not variant:
            continue
        if variant.stock_quantity < qty:
            flash(f'Not enough stock for {variant.product.name}.', 'danger')
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
        shipping_address=shipping_address
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
    
    flash('Order placed successfully!', 'success')
    return render_template('order_success.html', order_id=new_order.order_id)