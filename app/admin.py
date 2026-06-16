import os
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import Product, Category, ProductVariant, ProductImage, Order, User
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
    
    return render_template('admin/dashboard.html', 
                           total_products=total_products, 
                           total_categories=total_categories, 
                           low_stock_variants=low_stock_variants,
                           total_orders=total_orders,
                           recent_orders=recent_orders)

@admin.route('/products')
@login_required
@admin_required
def products():
    products = Product.query.all()
    return render_template('admin/products.html', products=products)

@admin.route('/product/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_product():
    categories = Category.query.all()
    if request.method == 'POST':
        name = request.form.get('name')
        category_id = request.form.get('category_id')
        description = request.form.get('description')
        regular_price = request.form.get('regular_price')
        sale_price = request.form.get('sale_price') or None
        
        new_product = Product(name=name, category_id=category_id, description=description, regular_price=regular_price, sale_price=sale_price)
        db.session.add(new_product)
        db.session.commit()

        file = request.files.get('image')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            img = ProductImage(product_id=new_product.product_id, image_url=filename, is_primary=True)
            db.session.add(img)
            db.session.commit()

        flash('Product added successfully!', 'success')
        return redirect(url_for('admin.products'))
    return render_template('admin/add_product.html', categories=categories)

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
    new_status = request.form.get('status')
    order.status = new_status
    db.session.commit()
    flash(f'Order #{order_id} status updated to {new_status}', 'success')
    return redirect(url_for('admin.order_detail', order_id=order_id))

@admin.route('/inventory')
@login_required
@admin_required
def inventory():
    low_stock = ProductVariant.query.filter(ProductVariant.stock_quantity < 10).all()
    all_variants = ProductVariant.query.all()
    return render_template('admin/inventory.html', low_stock=low_stock, all_variants=all_variants)

# --- NEW: ANALYTICS ROUTE ---
@admin.route('/analytics')
@login_required
@admin_required
def analytics():
    # Get all orders (you can filter by status='Delivered' if you only want completed sales)
    orders = Order.query.all()
    
    total_revenue = sum(float(order.total_amount) for order in orders)
    total_orders = len(orders)
    
    # Calculate Revenue over time (grouped by date)
    revenue_by_date = defaultdict(float)
    for order in orders:
        date_str = order.order_date.strftime('%Y-%m-%d')
        revenue_by_date[date_str] += float(order.total_amount)
        
    # Sort by date
    sorted_dates = sorted(revenue_by_date.keys())
    chart_labels = sorted_dates
    chart_data = [revenue_by_date[date] for date in sorted_dates]

    # Calculate Top Selling Products
    product_sales = defaultdict(int)
    for order in orders:
        for item in order.items:
            product_sales[item.variant.product.name] += item.quantity
            
    # Sort and get top 5
    sorted_products = sorted(product_sales.items(), key=lambda x: x[1], reverse=True)[:5]
    top_product_labels = [p[0] for p in sorted_products]
    top_product_data = [p[1] for p in sorted_products]

    return render_template('admin/analytics.html', 
                           total_revenue=total_revenue, 
                           total_orders=total_orders,
                           chart_labels=chart_labels,
                           chart_data=chart_data,
                           top_product_labels=top_product_labels,
                           top_product_data=top_product_data)

@admin.route('/data-science')
@login_required
@admin_required
def data_science():
    orders = Order.query.all()
    users = User.query.all()
    
    # 1. Get RFM Segmentation
    rfm_data = get_rfm_segmentation(orders, users)
    
    # 2. Get Sales Forecast
    forecast_dates, forecast_values = forecast_sales(orders)
    
    # Prepare data for Chart.js
    chart_labels = []
    chart_data = []
    if forecast_dates:
        chart_labels = forecast_dates
        chart_data = [round(val[0], 2) for val in forecast_values]

    return render_template('admin/data_science.html', 
                           rfm_data=rfm_data, 
                           forecast_dates=chart_labels, 
                           forecast_values=chart_data)