import os
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import Product, Category, ProductVariant, ProductImage, Order, User, Collection
from app.auth import admin_required
from collections import defaultdict
from app.data_science import get_rfm_segmentation, forecast_sales

admin = Blueprint('admin', __name__, url_prefix='/admin')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@admin.route('/')
@login_required
@admin_required
def dashboard():
    total_products = Product.query.count()
    total_categories = Category.query.count()
    total_orders = Order.query.count()
    low_stock_variants = ProductVariant.query.filter(ProductVariant.stock_quantity < 10).count()
    recent_orders = Order.query.order_by(Order.order_date.desc()).limit(10).all()
    return render_template('admin/dashboard.html', total_products=total_products, total_categories=total_categories, 
                           low_stock_variants=low_stock_variants, total_orders=total_orders, recent_orders=recent_orders)

@admin.route('/products')
@login_required
@admin_required
def products():
    products = Product.query.all()
    return render_template('admin/products.html', products=products)

@admin.route('/product/add', methods=['GET', 'POST'])
@admin.route('/product/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def add_product(product_id=None):
    categories = Category.query.all()
    product = None
    if product_id:
        product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        category_id = request.form.get('category_id')
        description = request.form.get('description')
        regular_price = request.form.get('regular_price')
        sale_price = request.form.get('sale_price') or None
        product_color = request.form.get('product_color')
        
        if product:
            product.name = name
            product.category_id = category_id
            product.description = description
            product.regular_price = regular_price
            product.sale_price = sale_price
            flash('Product updated successfully!', 'success')
        else:
            product = Product(name=name, category_id=category_id, description=description, 
                              regular_price=regular_price, sale_price=sale_price)
            db.session.add(product)
            db.session.flush()
            flash('Product added successfully!', 'success')
            
        db.session.commit()

        variant_ids = request.form.getlist('variant_ids')
        sizes = request.form.getlist('sizes')
        stocks = request.form.getlist('stocks')
        
        processed_variant_ids = []
        
        for i in range(len(sizes)):
            size = sizes[i]
            stock = int(stocks[i]) if stocks[i] else 0
            vid = variant_ids[i] if i < len(variant_ids) else None
            
            sku = f"{product.product_id}-{size}-{product_color}".upper().replace(" ", "")
            
            if vid:
                variant = ProductVariant.query.get(vid)
                if variant and variant.product_id == product.product_id:
                    variant.size = size
                    variant.color = product_color
                    variant.stock_quantity = stock
                    variant.sku = sku
                    processed_variant_ids.append(variant.variant_id)
            else:
                if not ProductVariant.query.filter_by(sku=sku).first():
                    new_variant = ProductVariant(
                        product_id=product.product_id, sku=sku, 
                        size=size, color=product_color, stock_quantity=stock
                    )
                    db.session.add(new_variant)
                    db.session.flush()
                    processed_variant_ids.append(new_variant.variant_id)
                    
        if product:
            for v in product.variants:
                if v.variant_id not in processed_variant_ids:
                    db.session.delete(v)
        db.session.commit()

        files = request.files.getlist('images')
        if files:
            for index, file in enumerate(files):
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    existing = ProductImage.query.filter_by(product_id=product.product_id, image_url=filename).first()
                    if not existing:
                        is_primary = (index == 0) if not product.images else False
                        img = ProductImage(product_id=product.product_id, image_url=filename, is_primary=is_primary)
                        db.session.add(img)
            db.session.commit()

        remove_ids = request.form.getlist('remove_images')
        if remove_ids:
            for img_id in remove_ids:
                img = ProductImage.query.get(img_id)
                if img:
                    try: os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], img.image_url))
                    except: pass
                    db.session.delete(img)
            db.session.commit()

        return redirect(url_for('admin.products'))
        
    return render_template('admin/add_product.html', categories=categories, product=product)

@admin.route('/product/delete/<int:product_id>', methods=['POST'])
@login_required
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    has_orders = any(item for v in product.variants for item in v.order_items)
    if has_orders:
        flash('Cannot delete: Product has existing orders. Set stock to 0 instead.', 'danger')
    else:
        for img in product.images:
            try: os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], img.image_url))
            except: pass
        db.session.delete(product)
        db.session.commit()
        flash('Product deleted successfully.', 'success')
    return redirect(url_for('admin.products'))

@admin.route('/product/image/reorder', methods=['POST'])
@login_required
@admin_required
def reorder_images():
    data = request.json
    image_ids = data.get('image_ids', [])
    for index, image_id in enumerate(image_ids):
        img = ProductImage.query.get(image_id)
        if img:
            img.display_order = index
            img.is_primary = (index == 0)
    db.session.commit()
    return jsonify({'status': 'success'})

@admin.route('/category/add', methods=['POST'])
@login_required
@admin_required
def add_category():
    name = request.form.get('name')
    slug = name.lower().replace(' ', '-')
    new_cat = Category(name=name, slug=slug)
    db.session.add(new_cat)
    db.session.commit()
    flash('Category added!', 'success')
    return redirect(url_for('admin.add_product'))

@admin.route('/orders')
@login_required
@admin_required
def orders():
    orders = Order.query.order_by(Order.order_date.desc()).all()
    return render_template('admin/orders.html', orders=orders)

@admin.route('/order/<int:order_id>')
@login_required
@admin_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('admin/order_detail.html', order=order)

@admin.route('/order/<int:order_id>/update-status', methods=['POST'])
@login_required
@admin_required
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    order.status = request.form.get('status')
    db.session.commit()
    flash(f'Order #{order_id} status updated', 'success')
    return redirect(url_for('admin.order_detail', order_id=order_id))

@admin.route('/inventory')
@login_required
@admin_required
def inventory():
    return render_template('admin/inventory.html', low_stock=ProductVariant.query.filter(ProductVariant.stock_quantity < 10).all(), all_variants=ProductVariant.query.all())

@admin.route('/analytics')
@login_required
@admin_required
def analytics():
    orders = Order.query.all()
    total_revenue = sum(float(o.total_amount) for o in orders)
    revenue_by_date = defaultdict(float)
    for o in orders: revenue_by_date[o.order_date.strftime('%Y-%m-%d')] += float(o.total_amount)
    sorted_dates = sorted(revenue_by_date.keys())
    product_sales = defaultdict(int)
    for o in orders:
        for item in o.items: product_sales[item.variant.product.name] += item.quantity
    top_products = sorted(product_sales.items(), key=lambda x: x[1], reverse=True)[:5]
    return render_template('admin/analytics.html', total_revenue=total_revenue, total_orders=len(orders),
                           chart_labels=sorted_dates, chart_data=[revenue_by_date[d] for d in sorted_dates],
                           top_product_labels=[p[0] for p in top_products], top_product_data=[p[1] for p in top_products])

@admin.route('/data-science')
@login_required
@admin_required
def data_science():
    rfm_data = get_rfm_segmentation(Order.query.all(), User.query.all())
    forecast_dates, forecast_values = forecast_sales(Order.query.all())
    return render_template('admin/data_science.html', rfm_data=rfm_data, 
                           forecast_dates=forecast_dates or [], 
                           forecast_values=[round(v[0], 2) for v in forecast_values] if forecast_values else [])

# --- COLLECTION MANAGEMENT ---
@admin.route('/collections')
@login_required
@admin_required
def manage_collections():
    collections = Collection.query.order_by(Collection.display_order, Collection.name).all()
    return render_template('admin/collections.html', collections=collections)

@admin.route('/collection/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_collection():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        slug = name.lower().replace(' ', '-')
        
        collection = Collection(name=name, slug=slug, description=description)
        db.session.add(collection)
        db.session.commit()
        
        flash('Collection created successfully!', 'success')
        return redirect(url_for('admin.manage_collections'))
    
    return render_template('admin/collection_form.html', collection=None, all_products=[])

@admin.route('/collection/edit/<int:collection_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_collection(collection_id):
    collection = Collection.query.get_or_404(collection_id)
    
    if request.method == 'POST':
        collection.name = request.form.get('name')
        collection.slug = request.form.get('slug', collection.name.lower().replace(' ', '-'))
        collection.description = request.form.get('description')
        collection.display_order = int(request.form.get('display_order', 0))
        
        product_ids = request.form.getlist('products')
        collection.products = Product.query.filter(Product.product_id.in_(product_ids)).all() if product_ids else []
        
        db.session.commit()
        flash('Collection updated successfully!', 'success')
        return redirect(url_for('admin.manage_collections'))
    
    all_products = Product.query.all()
    return render_template('admin/collection_form.html', collection=collection, all_products=all_products)

@admin.route('/collection/delete/<int:collection_id>', methods=['POST'])
@login_required
@admin_required
def delete_collection(collection_id):
    collection = Collection.query.get_or_404(collection_id)
    db.session.delete(collection)
    db.session.commit()
    flash('Collection deleted successfully!', 'success')
    return redirect(url_for('admin.manage_collections'))