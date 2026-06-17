from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from app.models import Product, Category, ProductVariant, Order, Wishlist

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/home')
def home():
    featured_products = Product.query.limit(4).all()
    return render_template('home.html', featured_products=featured_products)

@main.route('/shop')
def shop():
    category_id = request.args.get('category', type=int)
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    search = request.args.get('search', '')
    
    query = Product.query
    
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

@main.route('/collections')
def collections():
    # Get products for the Summer Floral Collection
    # You can adjust this to filter by category or specific product IDs
    summer_collection = Product.query.filter(
        Product.name.ilike('%floral%') | Product.name.ilike('%summer%')
    ).all()
    
    # If no products match, get the first 6 products as fallback
    if not summer_collection:
        summer_collection = Product.query.limit(6).all()
    
    return render_template('collections.html', products=summer_collection)

@main.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    variants = ProductVariant.query.filter_by(product_id=product_id).all()
    
    # Check wishlist status
    in_wishlist = False
    if current_user.is_authenticated:
        in_wishlist = Wishlist.query.filter_by(user_id=current_user.user_id, product_id=product_id).first() is not None
    
    # Calculate Stock for Progress Bar
    total_stock = sum(v.stock_quantity for v in variants)
    max_stock_for_bar = 20
    stock_percentage = min((total_stock / max_stock_for_bar) * 100, 100)
    
    # FIX: Prepare UNIQUE available sizes in Python to avoid Jinja2 errors
    seen_sizes = set()
    unique_sizes = []
    for v in variants:
        if v.stock_quantity > 0 and v.size not in seen_sizes:
            unique_sizes.append({'size': v.size, 'variant_id': v.variant_id, 'stock': v.stock_quantity})
            seen_sizes.add(v.size)

    # Mock Size Chart Data
    size_chart = [
        {'measurement': 'Length (inches)', 'XS': 42.5, 'S': 43, 'M': 43.5, 'L': 44, 'XL': 44.5, 'XXL': 45},
        {'measurement': 'Chest (inches)', 'XS': 33.5, 'S': 35, 'M': 37, 'L': 39, 'XL': 41, 'XXL': 43},
        {'measurement': 'Waist (inches)', 'XS': 29, 'S': 30.5, 'M': 32.5, 'L': 34.5, 'XL': 36.5, 'XXL': 38.5},
        {'measurement': 'Shoulders (inches)', 'XS': 12.6, 'S': 13, 'M': 13.5, 'L': 14, 'XL': 14.5, 'XXL': 15},
    ]

    return render_template('product_detail.html', 
                         product=product, 
                         variants=variants, 
                         unique_sizes=unique_sizes,
                         total_stock=total_stock,
                         stock_percentage=stock_percentage,
                         size_chart=size_chart,
                         in_wishlist=in_wishlist)

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
    if order.user_id != current_user.user_id:
        return "Unauthorized", 403
    return render_template('track_order.html', order=order)