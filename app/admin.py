import os
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import Product, Category, ProductVariant, ProductImage
from app.auth import admin_required

admin = Blueprint('admin', __name__, url_prefix='/admin')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@admin.route('/')
@login_required
@admin_required
def dashboard():
    total_products = Product.query.count()
    total_categories = Category.query.count()
    low_stock_variants = ProductVariant.query.filter(ProductVariant.stock_quantity < 10).count()
    return render_template('admin/dashboard.html', 
                           total_products=total_products, 
                           total_categories=total_categories, 
                           low_stock_variants=low_stock_variants)

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
        
        new_product = Product(
            name=name, category_id=category_id, description=description,
            regular_price=regular_price, sale_price=sale_price
        )
        db.session.add(new_product)
        db.session.commit()

        # Handle Image Upload
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