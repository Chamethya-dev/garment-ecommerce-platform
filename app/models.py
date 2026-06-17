from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# --- USER MODEL ---
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    default_district = db.Column(db.String(50), nullable=True)
    role = db.Column(db.String(20), default='customer') # 'customer' or 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    orders = db.relationship('Order', backref='customer', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        return str(self.user_id)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- CATEGORY MODEL ---
class Category(db.Model):
    __tablename__ = 'categories'
    category_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)

    products = db.relationship('Product', backref='category', lazy=True)

# --- COLLECTION MODEL ---
product_collections = db.Table('product_collections',
    db.Column('product_id', db.Integer, db.ForeignKey('products.product_id'), primary_key=True),
    db.Column('collection_id', db.Integer, db.ForeignKey('collections.collection_id'), primary_key=True)
)

class Collection(db.Model):
    __tablename__ = 'collections'
    collection_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    slug = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with products
    products = db.relationship('Product', secondary=product_collections, 
                              backref=db.backref('collections', lazy='dynamic'))
    
# --- PRODUCT MODEL ---
class Product(db.Model):
    __tablename__ = 'products'
    product_id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id'), nullable=False, index=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    regular_price = db.Column(db.Numeric(10, 2), nullable=False)
    sale_price = db.Column(db.Numeric(10, 2), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    variants = db.relationship('ProductVariant', backref='product', lazy=True, cascade="all, delete-orphan")
    images = db.relationship('ProductImage', backref='product', lazy=True, cascade="all, delete-orphan")

# --- PRODUCT VARIANT MODEL (Crucial for Garments) ---
class ProductVariant(db.Model):
    __tablename__ = 'product_variants'
    variant_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False, index=True)
    sku = db.Column(db.String(50), unique=True, nullable=False, index=True)
    size = db.Column(db.String(10), nullable=False)
    color = db.Column(db.String(50), nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False, default=0)

    order_items = db.relationship('OrderItem', backref='variant', lazy=True)

# --- PRODUCT IMAGE MODEL ---
class ProductImage(db.Model):
    __tablename__ = 'product_images'
    image_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    is_primary = db.Column(db.Boolean, default=False)
    display_order = db.Column(db.Integer, default=0)

# --- SHIPPING ZONE MODEL ---
class ShippingZone(db.Model):
    __tablename__ = 'shipping_zones'
    zone_id = db.Column(db.Integer, primary_key=True)
    zone_name = db.Column(db.String(50), nullable=False)
    delivery_fee = db.Column(db.Numeric(10, 2), nullable=False)
    districts = db.Column(db.String(255), nullable=False) # Comma-separated list

# --- ORDER MODEL ---
class Order(db.Model):
    __tablename__ = 'orders'
    order_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False, index=True)
    order_date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    status = db.Column(db.String(20), default='Pending', index=True) 
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    delivery_fee = db.Column(db.Numeric(10, 2), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    shipping_district = db.Column(db.String(50), nullable=False)
    shipping_address = db.Column(db.Text, nullable=False)

    items = db.relationship('OrderItem', backref='order', lazy=True, cascade="all, delete-orphan")

# --- WISHLIST MODEL ---
class Wishlist(db.Model):
    __tablename__ = 'wishlist'
    wishlist_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
    added_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='wishlist_items')
    product = db.relationship('Product', backref='wishlisted_by')
    
    # Prevent duplicate wishlist entries
    __table_args__ = (db.UniqueConstraint('user_id', 'product_id', name='unique_wishlist_item'),)

# --- ORDER ITEM MODEL ---
class OrderItem(db.Model):
    __tablename__ = 'order_items'
    order_item_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'), nullable=False)
    variant_id = db.Column(db.Integer, db.ForeignKey('product_variants.variant_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)