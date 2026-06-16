from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from app.models import Product, Category, ProductVariant, Order

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/home')
def home():
    # Show featured products (latest 4 products)
    featured_products = Product.query.limit(4).all()
    return render_template('home.html', featured_products=featured_products)

@main.route('/shop')
def shop():
    # Get filters from URL
    category_id = request.args.get('category', type=int)
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    search = request.args.get('search', '')
    
    # Base query
    query = Product.query
    
    # Apply filters
    if category_id:
        query = query.filter_by(category_id=category_id)
    if min_price:
        query = query.filter(Product.regular_price >= min_price)
    if max_price:
        query = query.filter(Product.regular_price <= max_price)
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))
    
    products = query.all()
    categories = Category.query.all()
    
    return render_template('shop.html', products=products, categories=categories,
                         selected_category=category_id, search_term=search)

@main.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    variants = ProductVariant.query.filter_by(product_id=product_id).all()
    
    # Get available sizes and colors from variants
    sizes = set(v.size for v in variants if v.stock_quantity > 0)
    colors = set(v.color for v in variants if v.stock_quantity > 0)
    
    return render_template('product_detail.html', product=product, 
                         variants=variants, sizes=sizes, colors=colors)

@main.route('/category/<int:category_id>')
def category_products(category_id):
    category = Category.query.get_or_404(category_id)
    products = Product.query.filter_by(category_id=category_id).all()
    return render_template('category.html', category=category, products=products)

@main.route('/my-orders')
@login_required
def my_orders():
    orders = Order.query.filter_by(user_id=current_user.user_id).order_by(Order.order_date.desc()).all()
    return render_template('my_orders.html', orders=orders)

@main.route('/order/<int:order_id>/track')
@login_required
def track_order(order_id):
    order = Order.query.get_or_404(order_id)
    # Make sure user can only see their own orders
    if order.user_id != current_user.user_id:
        return "Unauthorized", 403
    return render_template('track_order.html', order=order)