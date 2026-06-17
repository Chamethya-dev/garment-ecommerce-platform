from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Wishlist, Product

wishlist = Blueprint('wishlist', __name__)

@wishlist.route('/wishlist')
@login_required
def view_wishlist():
    wishlist_items = Wishlist.query.filter_by(user_id=current_user.user_id).all()
    products = [item.product for item in wishlist_items]
    return render_template('wishlist.html', products=products)

@wishlist.route('/wishlist/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_wishlist(product_id):
    # Check if already in wishlist
    existing = Wishlist.query.filter_by(
        user_id=current_user.user_id, 
        product_id=product_id
    ).first()
    
    if existing:
        flash('Product already in wishlist!', 'info')
    else:
        new_wishlist_item = Wishlist(user_id=current_user.user_id, product_id=product_id)
        db.session.add(new_wishlist_item)
        db.session.commit()
        flash('Added to wishlist!', 'success')
    
    # Redirect back to the page they came from
    return redirect(request.referrer or url_for('main.shop'))

@wishlist.route('/wishlist/remove/<int:product_id>', methods=['POST'])
@login_required
def remove_from_wishlist(product_id):
    item = Wishlist.query.filter_by(
        user_id=current_user.user_id, 
        product_id=product_id
    ).first()
    
    if item:
        db.session.delete(item)
        db.session.commit()
        flash('Removed from wishlist', 'info')
    
    return redirect(url_for('wishlist.view_wishlist'))