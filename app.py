from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import random
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import openai  # Added for chatbot
from textblob import TextBlob  # For sentiment analysis
import re  # For regular expressions
import requests
import json
from bs4 import BeautifulSoup
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

# Configure logging
if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Application startup')

# Use PostgreSQL for production
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///dueltech.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Ensure the DATABASE_URL is in the correct format for SQLAlchemy
if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgres://'):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace('postgres://', 'postgresql://', 1)

try:
    db = SQLAlchemy(app)
    # Test database connection
    with app.app_context():
        db.engine.connect()
    app.logger.info('Database connection successful')
except Exception as e:
    app.logger.error(f'Database connection failed: {str(e)}')
    raise

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Database Models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'

class Product(db.Model):
    id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.String(20), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    brand = db.Column(db.String(50), nullable=False)
    category_id = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Product {self.name}>'

class ProductSpec(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(20), db.ForeignKey('product.id'), nullable=False)
    spec_key = db.Column(db.String(50), nullable=False)
    spec_value = db.Column(db.String(100), nullable=False)
    
    def __repr__(self):
        return f'<ProductSpec {self.spec_key}: {self.spec_value}>'

class PriceAlert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.String(20), db.ForeignKey('product.id'), nullable=False)
    target_price = db.Column(db.Float, nullable=False)
    current_price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_checked = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    notified = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<PriceAlert for Product {self.product_id} at {self.target_price}>'

class PriceHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(20), db.ForeignKey('product.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PriceHistory for Product {self.product_id} at {self.price}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Product categories
categories = {
    'laptops': {
        'name': 'Laptops',
        'icon': 'fas fa-laptop',
        'description': 'High-performance laptops for work and gaming'
    },
    'smartphones': {
        'name': 'Smartphones',
        'icon': 'fas fa-mobile-alt',
        'description': 'Latest smartphones with cutting-edge features'
    },
    'tablets': {
        'name': 'Tablets',
        'icon': 'fas fa-tablet-alt',
        'description': 'Versatile tablets for productivity and entertainment'
    },
    'cpus': {
        'name': 'CPUs & Processors',
        'icon': 'fas fa-microchip',
        'description': 'High-performance processors for gaming and workstations'
    },
    'gpus': {
        'name': 'Graphics Cards',
        'icon': 'fas fa-tv',
        'description': 'Powerful GPUs for gaming and content creation'
    },
    'storage': {
        'name': 'Storage Devices',
        'icon': 'fas fa-hdd',
        'description': 'SSDs, HDDs and portable storage solutions'
    },
    'monitors': {
        'name': 'Monitors & Displays',
        'icon': 'fas fa-desktop',
        'description': 'High-resolution monitors for productivity and gaming'
    },
    'peripherals': {
        'name': 'Peripherals',
        'icon': 'fas fa-keyboard',
        'description': 'Keyboards, mice, and other input devices'
    },
    'audio': {
        'name': 'Audio',
        'icon': 'fas fa-headphones',
        'description': 'Premium headphones, speakers and audio equipment'
    },
    'networking': {
        'name': 'Networking',
        'icon': 'fas fa-network-wired',
        'description': 'Routers, switches and networking equipment'
    },
    'components': {
        'name': 'PC Components',
        'icon': 'fas fa-memory',
        'description': 'Motherboards, RAM, and other PC components'
    },
    'accessories': {
        'name': 'Accessories',
        'icon': 'fas fa-plug',
        'description': 'Cables, adapters, and other tech accessories'
    }
}

# Function to convert db Product to the format used in templates
def product_to_dict(product):
    # Get all specs for this product
    specs_query = ProductSpec.query.filter_by(product_id=product.id).all()
    specs = {spec.spec_key: spec.spec_value for spec in specs_query}
    
    return {
        'id': product.id,
        'name': product.name,
        'price': product.price,
        'rating': product.rating,
        'brand': product.brand,
        'specs': specs
    }

# Get all products for a category from database
def get_category_products(category_id):
    db_products = Product.query.filter_by(category_id=category_id).all()
    return [product_to_dict(product) for product in db_products]

# Authentication routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Form validation
        if not username or not email or not password or not confirm_password:
            flash('Please fill all fields', 'warning')
            return redirect(url_for('register'))
            
        if password != confirm_password:
            flash('Passwords do not match', 'warning')
            return redirect(url_for('register'))
            
        # Check if username or email already exists
        user_exists = User.query.filter((User.username == username) | (User.email == email)).first()
        if user_exists:
            flash('Username or email already exists', 'warning')
            return redirect(url_for('register'))
            
        # Create new user
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please enter both username and password', 'warning')
            return redirect(url_for('login'))
            
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.username}!', 'success')
            
            # Redirect admin users to admin dashboard
            if user.is_admin:
                return redirect(next_page or url_for('admin_dashboard'))
            else:
                return redirect(next_page or url_for('index'))
        else:
            flash('Invalid username or password', 'warning')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('index'))

# Admin routes
@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'warning')
        return redirect(url_for('index'))
        
    product_count = Product.query.count()
    return render_template('admin/dashboard.html', product_count=product_count, categories=categories)

@app.route('/admin/products')
@login_required
def admin_products():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'warning')
        return redirect(url_for('index'))
    
    products = Product.query.all()
    product_list = [product_to_dict(product) for product in products]
    
    return render_template('admin/products.html', products=product_list, categories=categories)

@app.route('/admin/products/add', methods=['GET', 'POST'])
@login_required
def admin_add_product():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'warning')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        category_id = request.form.get('category')
        name = request.form.get('name')
        price = request.form.get('price')
        rating = float(request.form.get('rating'))
        brand = request.form.get('brand')
        
        # Generate a unique product ID
        product_id = f"{category_id}{Product.query.filter_by(category_id=category_id).count() + 1}"
        
        # Create new product
        new_product = Product(
            id=product_id,
            name=name,
            price=price,
            rating=rating,
            brand=brand,
            category_id=category_id
        )
        
        db.session.add(new_product)
        
        # Add product specifications
        for key, value in request.form.items():
            if key.startswith('spec_') and value:
                spec_key = key.replace('spec_', '')
                new_spec = ProductSpec(
                    product_id=product_id,
                    spec_key=spec_key,
                    spec_value=value
                )
                db.session.add(new_spec)
        
        db.session.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('admin_products'))
    
    return render_template('admin/add_product.html', categories=categories)

@app.route('/admin/products/edit/<product_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_product(product_id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'warning')
        return redirect(url_for('index'))
    
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.price = request.form.get('price')
        product.rating = float(request.form.get('rating'))
        product.brand = request.form.get('brand')
        product.category_id = request.form.get('category')
        
        # Update product specifications
        # First, delete existing specs
        ProductSpec.query.filter_by(product_id=product_id).delete()
        
        # Then add new specs
        for key, value in request.form.items():
            if key.startswith('spec_') and value:
                spec_key = key.replace('spec_', '')
                new_spec = ProductSpec(
                    product_id=product_id,
                    spec_key=spec_key,
                    spec_value=value
                )
                db.session.add(new_spec)
        
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('admin_products'))
    
    # Get all specs for this product
    specs = {spec.spec_key: spec.spec_value for spec in 
             ProductSpec.query.filter_by(product_id=product_id).all()}
    
    return render_template('admin/edit_product.html', 
                          product=product, 
                          specs=specs, 
                          categories=categories)

@app.route('/admin/products/delete/<product_id>', methods=['POST'])
@login_required
def admin_delete_product(product_id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'warning')
        return redirect(url_for('index'))
    
    product = Product.query.get_or_404(product_id)
    
    # Delete all specs first (foreign key constraint)
    ProductSpec.query.filter_by(product_id=product_id).delete()
    
    # Then delete the product
    db.session.delete(product)
    db.session.commit()
    
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('admin_products'))

@app.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'warning')
        return redirect(url_for('index'))
    
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/ai-product-fetch', methods=['GET', 'POST'])
@login_required
def admin_ai_fetch_product():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'warning')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        product_name = request.form.get('product_name')
        category_id = request.form.get('category')
        fetch_source = request.form.get('fetch_source', 'auto')
        
        try:
            # Fetch product data using AI and web scraping
            product_data = fetch_product_data(product_name, category_id, fetch_source)
            
            if product_data:
                category_name = categories[category_id]['name'] if category_id in categories else ''
                return jsonify({
                    'success': True,
                    'product': product_data,
                    'category_name': category_name
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Could not find product information. Please try a more specific product name.'
                })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error fetching product data: {str(e)}'
            })
    
    return render_template('admin/ai_product_fetch.html', categories=categories)

@app.route('/admin/ai-save-product', methods=['POST'])
@login_required
def admin_ai_save_product():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'warning')
        return redirect(url_for('index'))
    
    try:
        product_data = json.loads(request.form.get('product_data'))
        
        # Generate a unique product ID
        category_id = product_data['category_id']
        product_id = f"{category_id}{Product.query.filter_by(category_id=category_id).count() + 1}"
        
        # Create new product
        new_product = Product(
            id=product_id,
            name=product_data['name'],
            price=product_data['price'],
            rating=product_data['rating'],
            brand=product_data['brand'],
            category_id=category_id
        )
        
        db.session.add(new_product)
        
        # Add product specifications
        for key, value in product_data['specs'].items():
            new_spec = ProductSpec(
                product_id=product_id,
                spec_key=key,
                spec_value=str(value)
            )
            db.session.add(new_spec)
        
        db.session.commit()
        flash('Product successfully added to the database!', 'success')
    except Exception as e:
        flash(f'Error saving product: {str(e)}', 'danger')
    
    return redirect(url_for('admin_products'))

@app.route('/admin/create-admin', methods=['GET', 'POST'])
@login_required
def create_admin():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'warning')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if username or email already exists
        user_exists = User.query.filter((User.username == username) | (User.email == email)).first()
        if user_exists:
            flash('Username or email already exists', 'warning')
            return redirect(url_for('create_admin'))
        
        # Create new admin user
        hashed_password = generate_password_hash(password)
        new_admin = User(
            username=username,
            email=email,
            password=hashed_password,
            is_admin=True
        )
        
        db.session.add(new_admin)
        db.session.commit()
        
        flash('Admin user created successfully!', 'success')
        return redirect(url_for('admin_users'))
    
    return render_template('admin/create_admin.html')

# Update existing routes to use the database

@app.route('/')
def index():
    all_products = {}
    for category_id in categories:
        products_db = Product.query.filter_by(category_id=category_id).limit(10).all()
        all_products[category_id] = [product_to_dict(product) for product in products_db]
    
    return render_template('index.html', categories=categories, products=all_products)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        if name and email and subject and message:
            try:
                # Import needed packages for email
                import smtplib
                from email.mime.text import MIMEText
                from email.mime.multipart import MIMEMultipart
                
                # Email details
                sender_email = os.environ.get('EMAIL_USER', 'no-reply@dueltech.com')
                receiver_email = 'work.aniket4@gmail.com'
                password = os.environ.get('EMAIL_PASSWORD', '')
                
                # Create message
                msg = MIMEMultipart()
                msg['From'] = sender_email
                msg['To'] = receiver_email
                msg['Subject'] = f'DuelTech Contact: {subject}'
                
                # Email body
                body = f"""
                Name: {name}
                Email: {email}
                Subject: {subject}
                
                Message:
                {message}
                """
                msg.attach(MIMEText(body, 'plain'))
                
                # For local development, just log the message
                if not os.environ.get('VERCEL_ENV'):
                    print("Email would be sent with the following content:")
                    print(body)
                else:
                    # When on Vercel, attempt to send email if credentials are configured
                    if password:
                        with smtplib.SMTP('smtp.gmail.com', 587) as server:
                            server.starttls()
                            server.login(sender_email, password)
                            text = msg.as_string()
                            server.sendmail(sender_email, receiver_email, text)
                
                flash('Thank you for your message! We will get back to you soon.', 'success')
            except Exception as e:
                print(f"Error sending email: {e}")
                flash('Your message was received, but there was an issue with our email service. Please try again later.', 'warning')
            
            return redirect(url_for('contact'))
        
        flash('Please fill out all fields.', 'warning')
    
    return render_template('contact.html')

@app.route('/products')
def products_page():
    all_products = {}
    for category_id in categories:
        products_db = Product.query.filter_by(category_id=category_id).all()
        all_products[category_id] = [product_to_dict(product) for product in products_db]
    
    return render_template('products.html', categories=categories, all_products=all_products)

@app.route('/category/<category_id>')
def category(category_id):
    if category_id in categories:
        products_db = Product.query.filter_by(category_id=category_id).all()
        product_list = [product_to_dict(product) for product in products_db]
        
        return render_template('category.html', 
                             category=categories[category_id],
                             products=product_list)
    return redirect(url_for('index'))

@app.route('/product/<product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Get price history for this product
    price_history = PriceHistory.query.filter_by(product_id=product_id).order_by(PriceHistory.recorded_at.desc()).limit(10).all()
    
    # Format price history for chart
    history_dates = [h.recorded_at.strftime('%Y-%m-%d') for h in price_history][::-1]  # Reverse to get chronological order
    history_prices = [float(h.price.replace('$', '').replace(',', '')) if isinstance(h.price, str) else float(h.price) for h in price_history][::-1]
    
    # Get user's price alert for this product if logged in
    user_alert = None
    if current_user.is_authenticated:
        user_alert = PriceAlert.query.filter_by(user_id=current_user.id, product_id=product_id, is_active=True).first()
    
    return render_template('product_detail.html', 
                           product=product_to_dict(product), 
                           categories=categories,
                           price_history=price_history,
                           history_dates=history_dates,
                           history_prices=history_prices,
                           user_alert=user_alert)

@app.route('/compare')
def compare():
    product_ids = request.args.getlist('product_id')
    selected_category = request.args.get('category', 'laptops')
    view_mode = request.args.get('view', 'standard')  # New parameter for view mode
    highlight_diffs = request.args.get('highlight', 'on')  # New parameter for highlighting differences
    
    # Validate selected category
    if selected_category not in categories:
        selected_category = 'laptops'
    
    # Get products from database
    products_to_compare = []
    for pid in product_ids:
        product = Product.query.get(pid)
        if product:
            products_to_compare.append(product_to_dict(product))
    
    # Get all unique spec keys from these products
    all_specs_keys = set()
    for product in products_to_compare:
        for key in product['specs'].keys():
            all_specs_keys.add(key)
    
    # Get similar products for recommendations
    similar_products = []
    if products_to_compare:
        try:
            # Get the first product's category and find other products in the same category
            # Use safe dictionary access with .get() to avoid KeyError
            first_product = products_to_compare[0]
            category_id = first_product.get('category_id')
            
            # Only proceed if we have a valid category_id
            if category_id:
                similar_products = Product.query.filter_by(category_id=category_id).limit(6).all()
                similar_products = [product_to_dict(p) for p in similar_products if p.id not in product_ids]
            else:
                # Fallback to selected category if category_id is not found in the product
                similar_products = Product.query.filter_by(category_id=selected_category).limit(6).all()
                similar_products = [product_to_dict(p) for p in similar_products if p.id not in product_ids]
        except Exception as e:
            print(f"Error getting similar products: {str(e)}")
            # Fallback to selected category
            try:
                similar_products = Product.query.filter_by(category_id=selected_category).limit(6).all()
                similar_products = [product_to_dict(p) for p in similar_products if p.id not in product_ids]
            except:
                # If all else fails, just get some random products
                similar_products = Product.query.limit(6).all()
                similar_products = [product_to_dict(p) for p in similar_products if p.id not in product_ids]
    
    # Analyze differences between products
    differences = {}
    if len(products_to_compare) > 1 and highlight_diffs == 'on':
        differences = analyze_product_differences(products_to_compare)
    
    return render_template('compare.html', 
                         products=products_to_compare,
                         all_specs_keys=sorted(all_specs_keys),
                         categories=categories,
                         selected_category=selected_category,
                         view_mode=view_mode,
                         highlight_diffs=highlight_diffs,
                         differences=differences,
                         similar_products=similar_products[:3])  # Limit to 3 similar products


def analyze_product_differences(products):
    """Analyze and highlight key differences between products"""
    if not products or len(products) < 2:
        return {}
    
    differences = {}
    
    # Compare basic properties
    for prop in ['price', 'rating']:
        values = [p.get(prop) for p in products]
        if len(set(values)) > 1:  # If there are different values
            differences[prop] = {
                'values': values,
                'best_index': values.index(max(values)) if prop == 'rating' else values.index(min(values))
            }
    
    # Compare specs
    all_specs = set()
    for product in products:
        all_specs.update(product.get('specs', {}).keys())
    
    important_specs = [
        'processor', 'cpu', 'ram', 'memory', 'storage', 'display', 'screen', 'battery',
        'camera', 'graphics', 'gpu', 'resolution', 'refresh_rate', 'weight'
    ]
    
    # Prioritize important specs
    for spec in all_specs:
        # Check if this spec is important and exists in at least 2 products
        is_important = any(imp_spec in spec.lower() for imp_spec in important_specs)
        
        if not is_important:
            continue
            
        # Get values for this spec from all products
        spec_values = []
        for product in products:
            spec_values.append(product.get('specs', {}).get(spec, 'N/A'))
        
        # If there are different values and not just N/A
        if len(set(spec_values)) > 1 and not all(val == 'N/A' for val in spec_values):
            # Determine which is better (simplified logic)
            best_index = 0
            
            # For numeric specs, try to determine which is better
            numeric_values = []
            for val in spec_values:
                if isinstance(val, str):
                    # Extract numbers from strings like "16GB" or "512GB SSD"
                    matches = re.findall(r'\d+\.?\d*', val)
                    if matches:
                        numeric_values.append(float(matches[0]))
                    else:
                        numeric_values.append(0)
                else:
                    numeric_values.append(float(val) if val != 'N/A' else 0)
            
            if numeric_values and len(set(numeric_values)) > 1:
                # For most specs, higher is better
                if any(term in spec.lower() for term in ['ram', 'memory', 'storage', 'battery', 'processor', 'core', 'resolution', 'refresh']):
                    best_index = numeric_values.index(max(numeric_values))
                # For some specs, lower is better
                elif any(term in spec.lower() for term in ['weight', 'thickness']):
                    best_index = numeric_values.index(min(numeric_values))
            
            differences[spec] = {
                'values': spec_values,
                'best_index': best_index
            }
    
    return differences

@app.route('/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return redirect(url_for('products_page'))
    
    # Search for products that match the query in name, brand, or specs
    products_by_name = Product.query.filter(Product.name.like(f'%{query}%')).all()
    products_by_brand = Product.query.filter(Product.brand.like(f'%{query}%')).all()
    
    # Search in specifications
    spec_results = db.session.query(Product).join(ProductSpec).filter(
        ProductSpec.spec_value.like(f'%{query}%')
    ).all()
    
    # Combine results and remove duplicates
    all_products = list(set(products_by_name + products_by_brand + spec_results))
    search_results = [product_to_dict(product) for product in all_products]
    
    return render_template('search_results.html', 
                           query=query, 
                           products=search_results, 
                           categories=categories)

# Price Alert Routes
@app.route('/price-alerts')
@login_required
def price_alerts():
    # Get all active price alerts for the current user
    alerts = PriceAlert.query.filter_by(user_id=current_user.id, is_active=True).all()
    
    # Get product details for each alert
    alert_details = []
    for alert in alerts:
        product = Product.query.get(alert.product_id)
        if product:
            product_dict = product_to_dict(product)
            alert_details.append({
                'alert': alert,
                'product': product_dict
            })
    
    return render_template('price_alerts.html', alerts=alert_details)

@app.route('/set-price-alert/<product_id>', methods=['POST'])
@login_required
def set_price_alert(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Get target price from form
    try:
        target_price = float(request.form.get('target_price', 0))
        
        # Validate target price
        if target_price <= 0:
            flash('Please enter a valid target price', 'danger')
            return redirect(url_for('product_detail', product_id=product_id))
        
        # Check if user already has an alert for this product
        existing_alert = PriceAlert.query.filter_by(user_id=current_user.id, product_id=product_id, is_active=True).first()
        
        if existing_alert:
            # Update existing alert
            existing_alert.target_price = target_price
            existing_alert.notified = False
            existing_alert.last_checked = datetime.utcnow()
            db.session.commit()
            flash('Price alert updated successfully!', 'success')
        else:
            # Create new alert
            # Convert product price to float
            current_price = product.price
            if isinstance(current_price, str):
                current_price = float(current_price.replace('$', '').replace(',', ''))
            
            new_alert = PriceAlert(
                user_id=current_user.id,
                product_id=product_id,
                target_price=target_price,
                current_price=current_price
            )
            db.session.add(new_alert)
            db.session.commit()
            flash('Price alert set successfully!', 'success')
        
        # Record price in history if it doesn't exist for today
        today = datetime.utcnow().date()
        existing_history = PriceHistory.query.filter(
            PriceHistory.product_id == product_id,
            db.func.date(PriceHistory.recorded_at) == today
        ).first()
        
        if not existing_history:
            price_history = PriceHistory(
                product_id=product_id,
                price=current_price
            )
            db.session.add(price_history)
            db.session.commit()
        
    except ValueError:
        flash('Please enter a valid price', 'danger')
    
    return redirect(url_for('product_detail', product_id=product_id))

@app.route('/delete-price-alert/<alert_id>', methods=['POST'])
@login_required
def delete_price_alert(alert_id):
    alert = PriceAlert.query.get_or_404(alert_id)
    
    # Ensure the alert belongs to the current user
    if alert.user_id != current_user.id:
        flash('You do not have permission to delete this alert', 'danger')
        return redirect(url_for('price_alerts'))
    
    # Deactivate the alert instead of deleting it
    alert.is_active = False
    db.session.commit()
    
    flash('Price alert removed successfully', 'success')
    return redirect(url_for('price_alerts'))

# Chatbot route
@app.route('/chatbot')
def chatbot_page():
    return render_template('chatbot.html', categories=categories)

# AI Product Data Fetching Function
def fetch_product_data(product_name, category_id, fetch_source='auto'):
    """Fetch product data using AI and web scraping"""
    try:
        print(f"\n=== Starting product data fetch for: {product_name} ===\nCategory: {category_id}, Source: {fetch_source}")
        
        # Input validation
        if not product_name or not product_name.strip():
            print("Error: Empty product name provided")
            return create_mock_product_data("Generic Tech Product")
            
        if not category_id or category_id not in categories:
            print(f"Warning: Invalid category ID: {category_id}. Using default category.")
            category_id = 'laptops'  # Default to laptops if category is invalid
        
        # Use OpenAI to enhance the product search query
        enhanced_query = enhance_search_query(product_name, category_id)
        print(f"Enhanced search query: {enhanced_query}")
        
        # Determine the best source based on the category if set to auto
        if fetch_source == 'auto':
            if category_id in ['smartphones', 'tablets']:
                fetch_source = 'gsmarena'
            elif category_id in ['laptops', 'cpus', 'gpus']:
                fetch_source = 'newegg'
            else:
                fetch_source = 'amazon'
            print(f"Auto-selected source: {fetch_source}")
        
        # Fetch data from the appropriate source
        product_data = None
        
        # Try primary source
        try:
            print(f"Attempting to fetch data from primary source: {fetch_source}")
            if fetch_source == 'amazon':
                product_data = fetch_from_amazon(enhanced_query)
            elif fetch_source == 'flipkart':
                product_data = fetch_from_flipkart(enhanced_query)
            elif fetch_source == 'newegg':
                product_data = fetch_from_newegg(enhanced_query)
            elif fetch_source == 'gsmarena':
                product_data = fetch_from_gsmarena(enhanced_query)
            else:
                # Default to Amazon
                product_data = fetch_from_amazon(enhanced_query)
        except Exception as source_error:
            print(f"Error fetching from {fetch_source}: {str(source_error)}")
            product_data = None
        
        # If primary source failed, try fallback to Amazon
        if not product_data and fetch_source != 'amazon':
            print(f"Primary source failed. Trying fallback to Amazon.")
            try:
                product_data = fetch_from_amazon(enhanced_query)
            except Exception as fallback_error:
                print(f"Fallback to Amazon also failed: {str(fallback_error)}")
        
        # If all web scraping failed, use mock data
        if not product_data:
            print("All web scraping attempts failed. Using mock data.")
            product_data = create_mock_product_data(product_name)
        
        # Add the category_id
        product_data['category_id'] = category_id
        
        # Use OpenAI to enhance and standardize the product specs
        try:
            enhanced_data = enhance_product_specs(product_data, category_id)
            if enhanced_data:
                product_data = enhanced_data
        except Exception as enhance_error:
            print(f"Error enhancing product specs: {str(enhance_error)}")
            # Continue with unenhanced data
        
        print(f"=== Successfully completed product data fetch for: {product_data['name']} ===\n")
        return product_data
    except Exception as e:
        print(f"Critical error in fetch_product_data: {str(e)}")
        # Always return something, even if everything fails
        return create_mock_product_data(product_name)

def enhance_search_query(product_name, category_id):
    """Use OpenAI to enhance the product search query with precise details"""
    try:
        # Only use OpenAI if API key is available
        if not os.getenv('OPENAI_API_KEY'):
            return product_name
            
        openai.api_key = os.getenv('OPENAI_API_KEY')
        
        category_name = categories[category_id]['name'] if category_id in categories else ''
        
        # Create a more detailed prompt with specific instructions for accuracy
        prompt = f"""I need to search for precise information about a tech product: '{product_name}' in the category '{category_name}'.
        
        Please provide an extremely accurate and detailed search query that would help find the exact product information.
        Your response should include:
        1. The complete and correct model number with proper capitalization and spacing
        2. The exact product generation or year of release
        3. Any specific variant identifiers (e.g., processor type, memory configuration)
        4. The manufacturer's official product name
        5. Any unique identifiers that distinguish this exact model from similar ones
        
        For example, instead of "MacBook Pro", provide "Apple MacBook Pro 16-inch 2023 M3 Max 32GB RAM 1TB SSD Space Black".
        
        Return only the enhanced search query text without any additional explanation or notes."""
        
        # Use the more advanced ChatCompletion API instead of Completion
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a precise tech product identification specialist. Your job is to create exact search queries for finding specific tech products with all identifying details."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.3  # Lower temperature for more precise responses
        )
        
        enhanced_query = response.choices[0].message.content.strip()
        print(f"Original query: '{product_name}' → Enhanced query: '{enhanced_query}'")
        return enhanced_query if enhanced_query else product_name
    except Exception as e:
        print(f"Error enhancing search query: {str(e)}")
        return product_name

def enhance_product_specs(product_data, category_id):
    """Use OpenAI to enhance and standardize the product specifications with highly accurate details"""
    try:
        # Only use OpenAI if API key is available
        if not os.getenv('OPENAI_API_KEY'):
            return product_data
            
        openai.api_key = os.getenv('OPENAI_API_KEY')
        
        category_name = categories[category_id]['name'] if category_id in categories else ''
        
        # Convert product data to JSON string for the prompt
        product_json = json.dumps(product_data, indent=2)
        
        # Create category-specific guidance for the AI
        category_guidance = ""
        if category_id == 'laptops':
            category_guidance = """
            For laptops, ensure you include: exact processor model with generation, RAM amount and type, 
            storage capacity and type, display size with resolution and panel type, graphics card details, 
            battery capacity in Wh, port specifications, dimensions, weight, and any special features like 
            fingerprint readers or backlit keyboards.
            """
        elif category_id in ['smartphones', 'tablets']:
            category_guidance = """
            For mobile devices, ensure you include: exact processor/chipset model, RAM and storage configurations, 
            display specifications (size, resolution, panel type, refresh rate), camera details (MP, aperture, features), 
            battery capacity in mAh, charging capabilities, connectivity options, dimensions, weight, IP rating, 
            and special features like fingerprint sensors or facial recognition.
            """
        elif category_id in ['cpus', 'gpus']:
            category_guidance = """
            For processors/GPUs, ensure you include: architecture, manufacturing process, core/thread count, 
            base and boost clock speeds, cache sizes, TDP, socket type (for CPUs) or interface (for GPUs), 
            memory specifications, supported technologies, and benchmark scores if available.
            """
        elif category_id == 'monitors':
            category_guidance = """
            For monitors, ensure you include: panel type, resolution, refresh rate, response time, 
            color gamut coverage, HDR support, brightness levels, contrast ratio, adaptive sync technology, 
            connectivity options, ergonomic features, and dimensions.
            """
        
        # Create a detailed prompt with specific instructions for accuracy
        prompt = f"""I have the following tech product information for a {category_name} product:
        {product_json}
        
        {category_guidance}
        
        Please analyze this information and enhance it by:
        1. Adding any missing important specifications that are standard for this type of product
        2. Standardizing the specification names and formats (use snake_case for keys)
        3. Ensuring all values are accurate, precise, and in the correct format with proper units
        4. Adding any additional useful information for consumers
        5. Correcting any inaccurate information based on the product name and known specifications
        6. Researching the exact specifications for this model if the information seems incomplete
        7. Ensuring all technical specifications match the actual product capabilities
        
        The product specifications should be extremely detailed, accurate, and comprehensive - similar to what would be found on the manufacturer's official website.
        
        Return the enhanced product data as a valid JSON object with the same structure, but with improved and expanded specifications.
        The JSON should have these fields: name, price, rating, brand, category_id, and specs (a nested object of key-value pairs).
        
        Ensure the JSON is properly formatted and can be parsed by Python's json.loads() function.
        """
        
        # Use the more advanced ChatCompletion API instead of Completion
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",  # Using a model with larger context window
            messages=[
                {"role": "system", "content": "You are a technical product specification expert with deep knowledge of all tech products. You provide extremely accurate, detailed, and comprehensive product specifications. You always verify information for accuracy and ensure all specs match the actual product capabilities."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,  # Allow for more detailed responses
            temperature=0.2   # Lower temperature for more precise and factual responses
        )
        
        enhanced_data_text = response.choices[0].message.content.strip()
        
        # Extract JSON from the response (in case there's additional text)
        json_match = re.search(r'\{.*\}', enhanced_data_text, re.DOTALL)
        if json_match:
            enhanced_data_text = json_match.group(0)
            
        try:
            enhanced_data = json.loads(enhanced_data_text)
            
            # Verify that required fields exist
            required_fields = ['name', 'price', 'rating', 'brand', 'specs']
            for field in required_fields:
                if field not in enhanced_data:
                    print(f"Missing required field in enhanced data: {field}")
                    enhanced_data[field] = product_data.get(field, '')
            
            # Ensure category_id is preserved
            enhanced_data['category_id'] = category_id
            
            # Log the enhancement results
            original_specs_count = len(product_data.get('specs', {}))
            enhanced_specs_count = len(enhanced_data.get('specs', {}))
            print(f"Enhanced product specs: {original_specs_count} original specs → {enhanced_specs_count} enhanced specs")
            
            return enhanced_data
        except json.JSONDecodeError as e:
            print(f"Error parsing enhanced product data JSON: {str(e)}")
            print(f"Problematic JSON: {enhanced_data_text[:100]}...")
            return product_data
    except Exception as e:
        print(f"Error enhancing product specs: {str(e)}")
        return product_data

def fetch_from_amazon(query):
    """Fetch product data from Amazon"""
    try:
        # Format the search query for the URL
        search_query = query.replace(' ', '+')
        # Try both amazon.in and amazon.com to increase chances of success
        urls = [
            f"https://www.amazon.in/s?k={search_query}",
            f"https://www.amazon.com/s?k={search_query}"
        ]
        
        # Set headers to mimic a browser request with a more recent Chrome version
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.160 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'sec-ch-ua': '"Chromium";v="121", "Google Chrome";v="121"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1'
        }
        
        print(f"Searching Amazon for: {query}")
        
        response = None
        successful_url = None
        
        # Try each URL until we get a successful response
        for url in urls:
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    successful_url = url
                    break
                else:
                    print(f"Error: Amazon returned status code {response.status_code} for {url}")
            except Exception as url_error:
                print(f"Error accessing {url}: {str(url_error)}")
        
        if not response or response.status_code != 200:
            print(f"Error: Failed to get valid response from any Amazon URL")
            # Use mock data for testing when Amazon blocks requests
            return create_mock_product_data(query)
            
        # Use a more robust parsing approach with multiple fallbacks
        soup = None
        try:
            soup = BeautifulSoup(response.content, 'html.parser')  # Using html.parser instead of lxml
            
            # Save the HTML for debugging if needed
            try:
                with open('amazon_response.html', 'w', encoding='utf-8') as f:
                    f.write(str(soup))
            except Exception as file_error:
                print(f"Warning: Could not save debug HTML: {str(file_error)}")
        except Exception as parse_error:
            print(f"Error parsing HTML: {str(parse_error)}")
            return create_mock_product_data(query)
        
        # Try multiple selectors for product results
        product_div = None
        selectors = [
            'div[data-component-type="s-search-result"]',
            '.s-result-item[data-asin]:not(.AdHolder)',
            '.sg-col-inner .a-section.a-spacing-medium',
            '.s-result-list .s-result-item',
            '.s-search-results .s-card-container'
        ]
        
        for selector in selectors:
            try:
                results = soup.select(selector)
                if results:
                    # Filter out sponsored results and empty items
                    valid_results = [r for r in results if r.get('data-asin') or r.select_one('a[href*="/dp/"]')]
                    if valid_results:
                        product_div = valid_results[0]
                        break
            except Exception as selector_error:
                print(f"Error with selector '{selector}': {str(selector_error)}")
                continue
            
        if not product_div:
            print("No product results found on Amazon search page")
            return create_mock_product_data(query)
        
        # Extract product URL - try multiple selectors
        product_url = None
        url_selectors = [
            'a.a-link-normal[href*="/dp/"]', 
            'a[href*="/dp/"]',
            '.a-text-normal[href*="/dp/"]',
            'h2 a[href]'
        ]
        
        for selector in url_selectors:
            try:
                url_elem = product_div.select_one(selector)
                if url_elem and 'href' in url_elem.attrs:
                    product_url = url_elem['href']
                    break
            except Exception as url_error:
                print(f"Error with URL selector '{selector}': {str(url_error)}")
                continue
        
        if not product_url:
            print("Could not find product URL")
            return create_mock_product_data(query)
        
        # Normalize the URL
        try:
            if not product_url.startswith('http'):
                base_url = successful_url.split('/s?')[0] if successful_url else 'https://www.amazon.com'
                product_url = base_url + product_url
        except Exception as url_error:
            print(f"Error normalizing URL: {str(url_error)}")
            # Use the URL as is or create mock data if URL is invalid
            if not product_url or len(product_url) < 10:
                return create_mock_product_data(query)
        
        # Extract product name with better error handling
        product_name = query  # Default to the search query if extraction fails
        try:
            # Try different selectors for product name
            name_selectors = [
                'span.a-size-medium',
                'h2 a span',
                '.a-text-normal',
                'h2.a-size-mini a span',
                '.a-link-normal .a-text-normal',
                '.a-size-base-plus',
                'h2 .a-link-normal'
            ]
            
            for selector in name_selectors:
                product_name_elem = product_div.select_one(selector)
                if product_name_elem and product_name_elem.text.strip():
                    product_name = product_name_elem.text.strip()
                    break
        except Exception as name_error:
            print(f"Error extracting product name: {str(name_error)}")
        
        # Extract price with better error handling
        price = "$99.99"  # Default price if extraction fails
        try:
            # Get price - try different selectors
            price_selectors = [
                'span.a-price-whole',
                '.a-price .a-offscreen',
                '.a-price',
                '.a-color-price',
                '.a-price-symbol + .a-price-whole',
                'span[data-a-color="price"]'
            ]
            
            for selector in price_selectors:
                price_element = product_div.select_one(selector)
                if price_element and price_element.text.strip():
                    price_text = price_element.text.strip()
                    # Extract numeric part from price
                    price_match = re.search(r'([\d,]+\.?\d*)', price_text)
                    if price_match:
                        # Determine currency symbol based on the URL
                        currency = "$" if "amazon.com" in successful_url else "₹"
                        price = f"{currency}{price_match.group(1)}"
                        break
        except Exception as price_error:
            print(f"Error extracting price: {str(price_error)}")
        
        # Extract rating with better error handling
        rating = 4.0  # Default rating if extraction fails
        try:
            # Get rating - try different selectors
            rating_selectors = [
                'span.a-icon-alt',
                '.a-star-medium-4',
                '[aria-label*="stars"]',
                '.a-icon-star-small .a-icon-alt',
                'i.a-icon-star .a-icon-alt',
                'i.a-icon-star-small span'
            ]
            
            for selector in rating_selectors:
                rating_element = product_div.select_one(selector)
                if rating_element:
                    rating_text = rating_element.text if hasattr(rating_element, 'text') else rating_element.get('aria-label', '')
                    rating_match = re.search(r'([\d.]+)', rating_text)
                    if rating_match:
                        try:
                            rating = float(rating_match.group(1))
                            # Ensure rating is within valid range
                            if rating > 5.0:
                                rating = rating / 2  # Sometimes ratings are out of 10
                            if rating > 5.0 or rating < 1.0:
                                rating = 4.0  # Default to 4.0 if out of expected range
                            break
                        except ValueError:
                            continue
        except Exception as rating_error:
            print(f"Error extracting rating: {str(rating_error)}")
            # Keep default rating
        
        # Get brand
        brand = ''
        if product_name:
            brand = product_name.split(' ')[0]
        
        # Create basic specs even before fetching product page
        specs = {
            'product_type': query.split(' ')[0],
            'model': product_name
        }
        
        try:
            # Now fetch the product page to get more details
            print(f"Fetching product details from: {product_url}")
            product_response = requests.get(product_url, headers=headers, timeout=10)
            
            if product_response.status_code == 200:
                product_soup = BeautifulSoup(product_response.content, 'html.parser')
                
                # Extract specifications - try multiple approaches
                # Approach 1: Product details table
                details_section = product_soup.select('#productDetails_techSpec_section_1, #productDetails_detailBullets_sections1, .a-section.a-spacing-small.a-spacing-top-small')
                if details_section:
                    for section in details_section:
                        rows = section.select('tr') or section.select('li')
                        for row in rows:
                            key_elem = row.select_one('th, .a-text-bold')
                            value_elem = row.select_one('td, span:not(.a-text-bold)')
                            
                            if key_elem and value_elem:
                                key = key_elem.text.strip().lower().replace(' ', '_')
                                value = value_elem.text.strip()
                                specs[key] = value
                
                # Approach 2: Bullet points
                if len(specs) <= 2:  # If we only have the basic specs
                    bullet_points = product_soup.select('#feature-bullets li, #productDescription p')
                    for i, bullet in enumerate(bullet_points):
                        bullet_text = bullet.text.strip()
                        if bullet_text and not bullet_text.startswith('P.when'):
                            specs[f'feature_{i+1}'] = bullet_text
                
                # Approach 3: Product description
                description = product_soup.select_one('#productDescription')
                if description:
                    specs['description'] = description.text.strip()
        except Exception as e:
            print(f"Error fetching product details: {str(e)}")
            # Continue with the basic specs we already have
        
        # Ensure we have at least some specs
        if len(specs) <= 2:
            specs.update({
                'display': 'High-resolution display',
                'processor': 'High-performance processor',
                'memory': '8GB RAM',
                'storage': '256GB SSD',
                'battery': 'Long-lasting battery'
            })
        
        result = {
            'name': product_name,
            'price': price,
            'rating': rating,
            'brand': brand,
            'specs': specs
        }
        
        print(f"Successfully fetched product data for: {product_name}")
        return result
    except Exception as e:
        print(f"Error fetching from Amazon: {str(e)}")
        # Return mock data as fallback
        return create_mock_product_data(query)

def create_mock_product_data(query):
    """Create mock product data when web scraping fails"""
    print(f"Creating mock data for: {query}")
    
    # Extract brand and model from query if possible
    parts = query.split(' ')
    brand = parts[0] if parts else 'Tech'
    model = ' '.join(parts[1:3]) if len(parts) > 1 else 'Pro Model'
    
    # Determine product type based on query keywords
    product_type = 'laptop'
    if any(keyword in query.lower() for keyword in ['phone', 'smartphone', 'mobile']):
        product_type = 'smartphone'
    elif any(keyword in query.lower() for keyword in ['tablet', 'ipad', 'tab']):
        product_type = 'tablet'
    elif any(keyword in query.lower() for keyword in ['gpu', 'graphics', 'rtx', 'gtx']):
        product_type = 'graphics card'
    elif any(keyword in query.lower() for keyword in ['cpu', 'processor', 'ryzen', 'intel']):
        product_type = 'processor'
    
    # Generate specs based on product type
    specs = {
        'product_type': product_type,
        'brand': brand,
        'model': model
    }
    
    if product_type == 'laptop':
        specs.update({
            'processor': 'Intel Core i7-12700H / AMD Ryzen 7 5800H',
            'memory': '16GB DDR4 RAM',
            'storage': '512GB NVMe SSD',
            'display': '15.6-inch Full HD (1920 x 1080) IPS',
            'graphics': 'NVIDIA GeForce RTX 3060 6GB GDDR6',
            'battery': '70Wh Li-ion battery, up to 8 hours',
            'operating_system': 'Windows 11 Home',
            'ports': 'USB-C, HDMI, USB 3.0, Audio jack',
            'weight': '2.1 kg'
        })
    elif product_type == 'smartphone':
        specs.update({
            'display': '6.5-inch AMOLED, 120Hz, HDR10+',
            'processor': 'Snapdragon 8 Gen 1 / MediaTek Dimensity 9000',
            'memory': '8GB LPDDR5 RAM',
            'storage': '128GB UFS 3.1 storage',
            'main_camera': '50MP wide + 12MP ultrawide + 8MP telephoto',
            'selfie_camera': '32MP',
            'battery': '5000mAh, 65W fast charging',
            'operating_system': 'Android 12',
            'connectivity': '5G, Wi-Fi 6, Bluetooth 5.2, NFC'
        })
    elif product_type == 'graphics card':
        specs.update({
            'gpu': 'NVIDIA GeForce RTX 3080 / AMD Radeon RX 6800 XT',
            'memory': '12GB GDDR6X',
            'memory_bus': '384-bit',
            'cuda_cores': '8704',
            'boost_clock': '1.71 GHz',
            'tdp': '320W',
            'interface': 'PCI Express 4.0 x16',
            'outputs': 'HDMI 2.1, 3x DisplayPort 1.4a',
            'power_connector': '2x 8-pin'
        })
    
    return {
        'name': f"{brand} {model} {product_type.title()}",
        'price': '₹49,999',
        'rating': 4.5,
        'brand': brand,
        'specs': specs
    }

def fetch_from_flipkart(query):
    """Fetch product data from Flipkart"""
    try:
        # Format the search query for the URL
        search_query = query.replace(' ', '+')
        url = f"https://www.flipkart.com/search?q={search_query}"
        
        # Set headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        print(f"Searching Flipkart for: {query}")
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"Error: Flipkart returned status code {response.status_code}")
            return create_mock_product_data(query)
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try different selectors for product cards
        product_div = (soup.select_one('div._1AtVbE') or 
                      soup.select_one('div[data-id]') or
                      soup.select_one('div._4ddWXP'))
                      
        if not product_div:
            print("No product results found on Flipkart search page")
            return create_mock_product_data(query)
            
        # Try different selectors for product URL
        product_url_elem = (product_div.select_one('a._1fQZEK') or 
                           product_div.select_one('a[href*="/p/"]') or
                           product_div.select_one('a'))
                           
        if not product_url_elem or 'href' not in product_url_elem.attrs:
            print("Could not find product URL on Flipkart")
            return create_mock_product_data(query)
            
        product_url = product_url_elem['href']
        if not product_url.startswith('http'):
            product_url = 'https://www.flipkart.com' + product_url
        
        # Try different selectors for product name
        product_name_elem = (product_div.select_one('div._4rR01T') or 
                           product_div.select_one('a.s1Q9rs') or
                           product_div.select_one('div.CXW8mj'))
                           
        product_name = product_name_elem.text.strip() if product_name_elem else query
        
        # Try different selectors for price
        price_element = (product_div.select_one('div._30jeq3') or 
                        product_div.select_one('div._1_WHN1') or
                        product_div.select_one('div[class*="price"]'))
                        
        price = price_element.text.strip() if price_element else '₹35,999'
        
        # Try different selectors for rating
        rating_element = (product_div.select_one('div._3LWZlK') or 
                         product_div.select_one('div[class*="rating"]'))
                         
        rating = 4.0  # Default rating
        if rating_element:
            try:
                rating = float(rating_element.text.strip())
            except ValueError:
                # If we can't convert to float, use default
                pass
        
        # Get brand
        brand = ''
        if product_name:
            brand = product_name.split(' ')[0]
        
        # Create basic specs even before fetching product page
        specs = {
            'product_type': query.split(' ')[0],
            'model': product_name
        }
        
        try:
            # Now fetch the product page to get more details
            print(f"Fetching product details from Flipkart: {product_url}")
            product_response = requests.get(product_url, headers=headers, timeout=10)
            
            if product_response.status_code == 200:
                product_soup = BeautifulSoup(product_response.content, 'html.parser')
                
                # Try multiple approaches to get specifications
                # Approach 1: Standard specs table
                specs_table = product_soup.select('div._14cfVK, table.SpecsTable')
                for spec in specs_table:
                    key_elem = spec.select_one('div._2H87wv, td.label')
                    value_elem = spec.select_one('div._2vZqPX, td.value')
                    
                    if key_elem and value_elem:
                        key = key_elem.text.strip().lower().replace(' ', '_')
                        value = value_elem.text.strip()
                        specs[key] = value
                
                # Approach 2: Feature sections
                if len(specs) <= 2:  # If we only have the basic specs
                    feature_sections = product_soup.select('div._2418kt, div.specSection')
                    for section in feature_sections:
                        title_elem = section.select_one('div._2lzn0o, div.specHead')
                        if title_elem:
                            section_title = title_elem.text.strip().lower().replace(' ', '_')
                            features = section.select('li._21lJbe, div.specValue')
                            for i, feature in enumerate(features):
                                specs[f"{section_title}_{i+1}"] = feature.text.strip()
                
                # Approach 3: Product description
                description = product_soup.select_one('div._1mXcCf, div.readMore')
                if description:
                    specs['description'] = description.text.strip()
        except Exception as e:
            print(f"Error fetching product details from Flipkart: {str(e)}")
            # Continue with the basic specs we already have
        
        # Ensure we have at least some specs
        if len(specs) <= 2:
            specs.update({
                'display': 'High-quality display',
                'processor': 'Fast processor',
                'memory': '6GB RAM',
                'storage': '128GB',
                'battery': 'Long-lasting battery'
            })
        
        result = {
            'name': product_name,
            'price': price,
            'rating': rating,
            'brand': brand,
            'specs': specs
        }
        
        print(f"Successfully fetched product data from Flipkart for: {product_name}")
        return result
    except Exception as e:
        print(f"Error fetching from Flipkart: {str(e)}")
        return create_mock_product_data(query)

def fetch_from_newegg(query):
    """Fetch product data from Newegg"""
    try:
        # Format the search query for the URL
        search_query = query.replace(' ', '+')
        url = f"https://www.newegg.com/p/pl?d={search_query}"
        
        # Set headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Find the first product result
        product_div = soup.select_one('div.item-cell')
        if not product_div:
            return None
            
        # Extract product details
        product_url_elem = product_div.select_one('a.item-title')
        if not product_url_elem:
            return None
            
        product_url = product_url_elem['href']
        product_name = product_url_elem.text.strip()
        
        # Get price
        price_element = product_div.select_one('li.price-current')
        price = f"₹{price_element.text.strip().replace('$', '').replace(',', '')}" if price_element else ''
        
        # Get rating
        rating_element = product_div.select_one('i.rating')
        rating = 0
        if rating_element:
            rating_style = rating_element.get('style', '')
            rating_match = re.search(r'width:(\d+)%', rating_style)
            if rating_match:
                rating_percent = int(rating_match.group(1))
                rating = round(rating_percent / 20, 1)  # Convert percentage to 5-star scale
        
        # Get brand
        brand_element = product_div.select_one('div.item-branding img')
        brand = brand_element.get('title', '') if brand_element else ''
        if not brand and product_name:
            brand = product_name.split(' ')[0]
        
        # Now fetch the product page to get more details
        product_response = requests.get(product_url, headers=headers)
        product_soup = BeautifulSoup(product_response.content, 'lxml')
        
        # Extract specifications
        specs = {}
        
        # Try to get specs from the product details section
        specs_table = product_soup.select('div.product-specs table tr')
        for row in specs_table:
            cells = row.select('td, th')
            if len(cells) >= 2:
                key = cells[0].text.strip().lower().replace(' ', '_')
                value = cells[1].text.strip()
                specs[key] = value
        
        # If no specs found, try another approach
        if not specs:
            feature_bullets = product_soup.select('div.product-bullets li')
            for i, bullet in enumerate(feature_bullets):
                specs[f'feature_{i+1}'] = bullet.text.strip()
        
        return {
            'name': product_name,
            'price': price,
            'rating': rating,
            'brand': brand,
            'specs': specs
        }
    except Exception as e:
        print(f"Error fetching from Newegg: {str(e)}")
        return None

def fetch_from_gsmarena(query):
    """Fetch product data from GSMArena (specialized for smartphones)"""
    try:
        # Format the search query for the URL
        search_query = query.replace(' ', '+')
        url = f"https://www.gsmarena.com/res.php3?sSearch={search_query}"
        
        # Set headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Find the first product result
        product_div = soup.select_one('div.makers li')
        if not product_div:
            return None
            
        # Extract product details
        product_url_elem = product_div.select_one('a')
        if not product_url_elem:
            return None
            
        product_url = 'https://www.gsmarena.com/' + product_url_elem['href']
        product_name = product_url_elem.text.strip()
        
        # Now fetch the product page to get more details
        product_response = requests.get(product_url, headers=headers)
        product_soup = BeautifulSoup(product_response.content, 'lxml')
        
        # Extract brand and model
        title_elem = product_soup.select_one('h1.specs-phone-name-title')
        full_name = title_elem.text.strip() if title_elem else product_name
        brand = full_name.split(' ')[0] if full_name else ''
        
        # Get price (GSMArena doesn't typically have prices, so we'll use a placeholder)
        price = "₹Price varies"
        
        # Get rating (GSMArena has user opinions)
        rating_elem = product_soup.select_one('div.score')
        rating = float(rating_elem.text.strip()) / 2 if rating_elem else 4.0  # Convert to 5-star scale
        
        # Extract specifications
        specs = {}
        
        # GSMArena has a structured specs table
        specs_tables = product_soup.select('table')
        for table in specs_tables:
            category_elem = table.select_one('th')
            if category_elem:
                category = category_elem.text.strip().lower().replace(' ', '_')
                rows = table.select('tr')
                for row in rows:
                    cells = row.select('td')
                    if len(cells) >= 2:
                        key = cells[0].text.strip().lower().replace(' ', '_')
                        value = cells[1].text.strip()
                        specs[f"{category}_{key}"] = value
        
        return {
            'name': full_name,
            'price': price,
            'rating': rating,
            'brand': brand,
            'specs': specs
        }
    except Exception as e:
        print(f"Error fetching from GSMArena: {str(e)}")
        return None

# Chatbot API endpoint
# Store conversation history and context for each session
conversation_histories = {}
user_preferences = {}  # Store user preferences for personalized recommendations
sentiment_history = {}  # Track sentiment over time for each user
language_preferences = {}  # Store language preferences for multilingual support
feedback_data = {}  # Store user feedback on chatbot responses

@app.route('/api/feedback', methods=['POST'])
def chat_feedback():
    """API endpoint to receive feedback on chatbot responses"""
    try:
        data = request.json
        feedback_type = data.get('feedback', '')
        message_id = data.get('message_id', '')
        message = data.get('message', '')
        session_id = data.get('session_id', '')
        
        # Initialize feedback data for this session if it doesn't exist
        if session_id not in feedback_data:
            feedback_data[session_id] = []
        
        # Store feedback
        feedback_data[session_id].append({
            'feedback_type': feedback_type,
            'message_id': message_id,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
        
        # Log feedback for analysis
        print(f"Feedback received from session {session_id}: {feedback_type} for message: {message[:50]}...")
        
        # Return success response
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error processing feedback: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat_api():
    data = request.json
    user_message = data.get('message', '')
    session_id = data.get('session_id', request.remote_addr)  # Use IP address as default session ID
    user_language = data.get('language', 'en')  # Default to English
    
    # Initialize data structures for this session if they don't exist
    if session_id not in conversation_histories:
        conversation_histories[session_id] = []
    if session_id not in user_preferences:
        user_preferences[session_id] = {}
    if session_id not in sentiment_history:
        sentiment_history[session_id] = []
    if session_id not in language_preferences:
        language_preferences[session_id] = user_language
    
    # Get conversation history for this session
    conversation_history = conversation_histories[session_id]
    
    # Analyze sentiment of user message
    sentiment_data = analyze_sentiment(user_message)
    
    # Store sentiment data for trend analysis
    sentiment_history[session_id].append({
        'message': user_message,
        'sentiment': sentiment_data,
        'timestamp': datetime.now().isoformat()
    })
    
    # Limit sentiment history to last 20 messages
    if len(sentiment_history[session_id]) > 20:
        sentiment_history[session_id] = sentiment_history[session_id][-20:]
    
    # Detect language if not explicitly provided
    if user_language == 'en':
        try:
            detected_language = detect_language(user_message)
            if detected_language != 'en':
                # Update language preference if a non-English language is detected
                language_preferences[session_id] = detected_language
        except Exception as e:
            print(f"Error detecting language: {str(e)}")
    
    # Extract user preferences from message
    extract_user_preferences(user_message, session_id)
    
    # Always provide a specific response, no matter what
    response_provided = False
    final_response = ""
    
    # Force a response to be generated
    try:
        # Try multiple methods to get a response and combine them if possible
        responses = []
        
        # Method 1: Check for tech-specific information
        try:
            tech_info = get_tech_info(user_message)
            if tech_info:
                responses.append(tech_info)
        except Exception as e:
            print(f"Error getting tech info: {str(e)}")
        
        # Method 2: Check our product database
        try:
            product_info = get_product_info_from_database(user_message)
            if product_info:
                responses.append(product_info)
        except Exception as e:
            print(f"Error getting product info: {str(e)}")
        
        # Method 3: Try web search
        try:
            web_search_results = perform_web_search(user_message)
            if web_search_results:
                responses.append(web_search_results)
        except Exception as e:
            print(f"Error performing web search: {str(e)}")
        
        # Method 4: Generate a response based on the query
        try:
            generated_response = generate_tech_response(user_message)
            if generated_response:
                responses.append(generated_response)
        except Exception as e:
            print(f"Error generating tech response: {str(e)}")
        
        # If we have any responses, format them in a structured way
        if responses:
            # Extract information from the responses
            title = "Technology Information"
            description = "Here's what I found about your query:"
            
            # Try to extract a better title from the responses
            for response in responses:
                if response.startswith('#'):
                    # Already formatted, use as is
                    final_response = response
                    response_provided = True
                    break
                elif ':' in response[:100]:  # Look for a title in the first 100 chars
                    potential_title = response.split(':', 1)[0].strip()
                    if len(potential_title) < 50:  # Reasonable title length
                        title = potential_title
            
            if not response_provided:  # Only if we didn't find an already formatted response
                # Format the responses in a structured way
                sections = []
                
                # Split responses into sections
                for i, response in enumerate(responses[:2]):  # Limit to top 2 responses
                    if i == 0:
                        description = response[:200] + "..." if len(response) > 200 else response
                    
                    # Convert the response into bullet points if it's not already
                    if not response.startswith('•') and not response.startswith('#'):
                        lines = response.split('\n')
                        formatted_lines = []
                        
                        for j, line in enumerate(lines):
                            if j == 0 and i > 0:
                                formatted_lines.append(f"**Source {i+1}**:")
                            
                            if line.strip() and not line.startswith('•') and not line.startswith('#'):
                                if ':' in line and len(line.split(':', 1)[0]) < 30:
                                    # This looks like a key-value pair
                                    key, value = line.split(':', 1)
                                    formatted_lines.append(f"• **{key.strip()}**: {value.strip()}")
                                else:
                                    formatted_lines.append(f"• {line.strip()}")
                        
                        sections.append(formatted_lines)
                    else:
                        # Already formatted, just split into lines
                        sections.append(response.split('\n'))
                
                # Create the structured response
                final_response = format_structured_response(title, description, *sections)
                response_provided = True
        
        # If all else fails, provide a specific response based on keywords
        if not response_provided:
            query = user_message.lower()
            if 'laptop' in query:
                final_response = format_structured_response(
                    "Laptops",
                    "Portable computers with integrated screen, keyboard, and touchpad in a clamshell design.",
                    [
                        "**Performance Categories**:",
                        "• Entry-level: Basic web browsing, document editing, media consumption",
                        "• Mid-range: Productivity work, light content creation, casual gaming",
                        "• High-end: Professional content creation, engineering applications, AAA gaming"
                    ],
                    [
                        "**Key Specifications**:",
                        "• **Processor (CPU)**: Intel Core i3/i5/i7/i9 or AMD Ryzen 3/5/7/9",
                        "• **Memory (RAM)**: 8GB (basic), 16GB (recommended), 32GB+ (professional)",
                        "• **Storage**: SSD for speed (256GB-2TB), HDD for capacity",
                        "• **Display**: Resolution, panel type (IPS/OLED), refresh rate",
                        "• **Battery Life**: Typically 5-15 hours depending on usage and model"
                    ],
                    [
                        "**Popular Brands**:",
                        "• **Apple**: MacBook Air, MacBook Pro",
                        "• **Dell**: XPS, Inspiron, Latitude",
                        "• **HP**: Spectre, Envy, Pavilion",
                        "• **Lenovo**: ThinkPad, Yoga, IdeaPad",
                        "• **ASUS**: ZenBook, ROG, VivoBook"
                    ]
                )
            elif 'phone' in query or 'smartphone' in query:
                final_response = format_structured_response(
                    "Smartphones",
                    "Portable devices combining cellular connectivity with advanced computing capabilities.",
                    [
                        "**Key Features**:",
                        "• **Operating Systems**: iOS (Apple) or Android (various manufacturers)",
                        "• **Form Factors**: Standard, foldable, or flip designs",
                        "• **Connectivity**: 5G, Wi-Fi 6/6E, Bluetooth 5.0+, NFC",
                        "• **Security**: Facial recognition, fingerprint sensors, encryption"
                    ],
                    [
                        "**Important Specifications**:",
                        "• **Processor**: Apple A-series, Snapdragon, Exynos, MediaTek",
                        "• **Memory**: 4-12GB RAM depending on model and OS",
                        "• **Storage**: 64GB-1TB internal storage",
                        "• **Display**: OLED/AMOLED/LCD, refresh rate (60-120Hz+)",
                        "• **Camera System**: Multiple lenses, megapixels, sensor size",
                        "• **Battery**: Capacity (mAh), charging speed, wireless charging"
                    ],
                    [
                        "**Leading Models**:",
                        "• **Apple**: iPhone 15 series (Standard, Plus, Pro, Pro Max)",
                        "• **Samsung**: Galaxy S24 series, Galaxy Z Fold/Flip",
                        "• **Google**: Pixel 8 series",
                        "• **Other Notable Brands**: OnePlus, Xiaomi, OPPO, Vivo"
                    ]
                )
            elif 'processor' in query or 'cpu' in query:
                final_response = format_structured_response(
                    "Processors (CPUs)",
                    "The primary computing components in electronic devices that execute instructions and perform calculations.",
                    [
                        "**Architecture Types**:",
                        "• **x86-64**: Used in most desktop and laptop computers (Intel, AMD)",
                        "• **ARM**: Used in mobile devices, increasingly in laptops (Apple M-series, Qualcomm)",
                        "• **RISC-V**: Open-source architecture gaining traction in specialized applications"
                    ],
                    [
                        "**Key Specifications**:",
                        "• **Cores/Threads**: More cores enable better multitasking",
                        "• **Clock Speed**: Measured in GHz, affects single-thread performance",
                        "• **Cache Size**: L1/L2/L3 cache affects data access speed",
                        "• **TDP (Thermal Design Power)**: Power consumption and heat output",
                        "• **Process Node**: Smaller is better (5nm, 7nm, etc.)"
                    ],
                    [
                        "**Leading Manufacturers**:",
                        "• **Intel**: Core series (i3, i5, i7, i9), Core Ultra, Xeon",
                        "• **AMD**: Ryzen series (3, 5, 7, 9), Threadripper, EPYC",
                        "• **Apple**: M-series (M1, M2, M3) with various configurations",
                        "• **ARM-based**: Qualcomm Snapdragon, MediaTek Dimensity"
                    ]
                )
            elif 'graphics' in query or 'gpu' in query:
                final_response = format_structured_response(
                    "Graphics Processing Units (GPUs)",
                    "Specialized processors designed to render images, videos, and animations, crucial for gaming, content creation, and AI workloads.",
                    [
                        "**GPU Categories**:",
                        "• **Integrated**: Built into the CPU, lower performance but power-efficient",
                        "• **Discrete**: Separate component with dedicated memory, higher performance",
                        "• **Workstation**: Optimized for professional applications (CAD, 3D rendering)",
                        "• **Data Center**: Designed for AI/ML and high-performance computing"
                    ],
                    [
                        "**Key Specifications**:",
                        "• **VRAM**: Dedicated video memory (8-24GB+ for modern cards)",
                        "• **CUDA/Stream Processors**: Parallel processing units",
                        "• **Clock Speeds**: Core and memory clock rates",
                        "• **Ray Tracing**: Hardware acceleration for realistic lighting",
                        "• **DLSS/FSR**: AI upscaling technologies",
                        "• **Power Requirements**: Wattage needed (150W-450W+)"
                    ],
                    [
                        "**Leading Manufacturers**:",
                        "• **NVIDIA**: GeForce RTX series (4090, 4080, 4070, etc.), RTX Workstation",
                        "• **AMD**: Radeon RX series (7900 XTX, 7800 XT, etc.)",
                        "• **Intel**: Arc series (A770, A750, etc.)",
                        "• **Apple**: Integrated solutions in M-series chips"
                    ]
                )
            else:
                final_response = format_structured_response(
                    "Technology Information",
                    "I can provide detailed information about various technology products and categories.",
                    [
                        "**Popular Categories**:",
                        "• **Computing**: Laptops, desktops, tablets, servers",
                        "• **Mobile**: Smartphones, wearables, accessories",
                        "• **Components**: CPUs, GPUs, storage, memory",
                        "• **Peripherals**: Monitors, keyboards, mice, printers",
                        "• **Audio/Video**: Headphones, speakers, TVs, projectors",
                        "• **Networking**: Routers, switches, mesh systems"
                    ],
                    [
                        "**How I Can Help**:",
                        "• Provide detailed specifications for specific products",
                        "• Compare different models or technologies",
                        "• Explain technical concepts and terminology",
                        "• Offer recommendations based on your needs",
                        "• Troubleshoot common technical issues"
                    ],
                    [
                        "For more specific information, please ask about a particular:",
                        "• Device type (e.g., gaming laptop, ultrabook)",
                        "• Brand or model (e.g., MacBook Pro, RTX 4080)",
                        "• Technology (e.g., OLED displays, DDR5 memory)",
                        "• Use case (e.g., video editing, gaming, office work)"
                    ]
                )
        
        # Try to use OpenAI if available to enhance our response
        api_key = os.environ.get('OPENAI_API_KEY')
        
        if api_key:
            # Initialize OpenAI client
            openai.api_key = api_key
            
            # Create a comprehensive system message to define the chatbot's behavior
            system_message = """
            You are TechAssist, an advanced AI assistant specializing in technology for the DuelTech website.
            
            CAPABILITIES:
            - Provide in-depth, accurate information about all technology products and categories
            - Offer detailed comparisons between different tech products based on specifications and user needs
            - Make personalized recommendations considering user preferences, budget, and use cases
            - Explain technical concepts in both simple and advanced terms depending on the user's knowledge level
            - Answer questions about the latest technology trends, releases, and innovations
            - Help troubleshoot common technical issues with detailed step-by-step guidance
            - Provide insights on product durability, reliability, and value for money
            - Search the web for the most up-to-date information when needed
            - Adapt your tone based on the user's emotional state and communication style
            - Remember user preferences and past interactions to provide more personalized assistance
            - Support multiple languages and adapt to the user's preferred language
            
            PERSONALITY:
            - Knowledgeable but accessible - explain complex concepts clearly without being condescending
            - Helpful and patient - understand that users may have varying levels of technical knowledge
            - Objective and balanced - present pros and cons of different products fairly
            - Conversational and engaging - maintain a natural dialogue while being informative
            - Empathetic and responsive - adjust your tone based on the user's sentiment
            
            GUIDELINES:
            - Prioritize accuracy over generalization
            - When you don't know something specific, acknowledge it instead of providing potentially incorrect information
            - Tailor your responses to the user's demonstrated technical knowledge level
            - Maintain context from previous messages in the conversation
            - For product recommendations, consider various price points and use cases
            - Format your responses for readability with appropriate spacing and organization
            - When discussing products from our database, highlight their key features and specifications
            - If you mention products from our database, let users know they can find more details on our website
            - When using web search results, synthesize the information and cite sources when appropriate
            - If the user seems frustrated or confused, acknowledge their feelings and offer clearer explanations
            - If the user has shown specific preferences for brands, features, or price ranges, prioritize these in your recommendations
            
            You have access to information about all major tech products up to your knowledge cutoff date,
            plus the ability to search the web for the most current information.
            """
            
            # Prepare messages including conversation history
            messages = [{"role": "system", "content": system_message}]
            
            # Add user preferences as context for the AI
            user_prefs = user_preferences.get(session_id, {})
            if user_prefs:
                preferred_categories = user_prefs.get('categories', [])
                preferred_brands = user_prefs.get('brands', [])
                price_range = user_prefs.get('price_range', {})
                preferred_features = user_prefs.get('features', [])
                
                preferences_context = "User preferences detected:\n"
                
                if preferred_categories:
                    categories_str = ", ".join([categories.get(cat, {}).get('name', cat) for cat in preferred_categories])
                    preferences_context += f"- Interested in: {categories_str}\n"
                
                if preferred_brands:
                    brands_str = ", ".join(preferred_brands)
                    preferences_context += f"- Preferred brands: {brands_str}\n"
                
                if price_range:
                    if 'range' in price_range:
                        preferences_context += f"- Price preference: {price_range['range']} range\n"
                    elif 'min' in price_range and 'max' in price_range:
                        preferences_context += f"- Price range: ${price_range['min']} - ${price_range['max']}\n"
                
                if preferred_features:
                    features_str = ", ".join(preferred_features)
                    preferences_context += f"- Important features: {features_str}\n"
                
                messages.append({"role": "system", "content": preferences_context})
            
            # Add sentiment analysis as context for the AI
            current_sentiment = sentiment_data.get('sentiment', 'neutral')
            is_question = sentiment_data.get('is_question', False)
            is_urgent = sentiment_data.get('is_urgent', False)
            
            sentiment_context = "User message analysis:\n"
            sentiment_context += f"- Sentiment: {current_sentiment}\n"
            if is_question:
                sentiment_context += "- This appears to be a question\n"
            if is_urgent:
                sentiment_context += "- The user seems to have an urgent request\n"
            
            # Add sentiment trend if we have history
            if len(sentiment_history.get(session_id, [])) > 3:
                recent_sentiments = [item['sentiment']['sentiment'] for item in sentiment_history[session_id][-3:]]
                if all(s == 'negative' for s in recent_sentiments):
                    sentiment_context += "- The user has expressed negative sentiment in multiple messages. Consider acknowledging this and being extra helpful.\n"
            
            messages.append({"role": "system", "content": sentiment_context})
            
            # Add language preference
            user_lang = language_preferences.get(session_id, 'en')
            if user_lang != 'en':
                messages.append({"role": "system", "content": f"The user's preferred language appears to be {user_lang}. Consider responding in this language if appropriate."})
            
            # Add conversation history (up to last 10 messages to stay within token limits)
            messages.extend(conversation_history[-10:])
            
            # Add our final response as context for the AI
            messages.append({"role": "system", "content": f"Here is relevant information about the user's query: {final_response}. Use this information to provide a comprehensive and accurate response."})
            
            # Add the current user message
            messages.append({"role": "user", "content": user_message})
            
            try:
                # Call OpenAI API with enhanced parameters
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo-16k",  # Using a model with larger context window
                    messages=messages,
                    max_tokens=1000,  # Allow for more detailed responses
                    temperature=0.7,   # Balanced between creativity and accuracy
                    top_p=0.9,         # Nucleus sampling for more natural responses
                    presence_penalty=0.6,  # Encourage the model to talk about new topics
                    frequency_penalty=0.3   # Reduce repetition
                )
                
                # Extract the response
                bot_response = response.choices[0].message.content
            except Exception as openai_error:
                print(f"Error calling OpenAI API: {str(openai_error)}")
                # Use our final response if OpenAI fails
                bot_response = final_response
            
            # Update conversation history
            conversation_history.append({"role": "user", "content": user_message})
            conversation_history.append({"role": "assistant", "content": bot_response})
            
            # Limit conversation history to last 20 messages to prevent unlimited growth
            if len(conversation_history) > 20:
                conversation_history = conversation_history[-20:]
            
            conversation_histories[session_id] = conversation_history
        else:
            # When no API key is available, use our final response
            bot_response = final_response
            
            # Still maintain conversation history even without OpenAI
            conversation_history.append({"role": "user", "content": user_message})
            conversation_history.append({"role": "assistant", "content": bot_response})
            conversation_histories[session_id] = conversation_history
        
        return jsonify({
            'response': bot_response,
            'session_id': session_id  # Return the session ID for the client to store
        })
    except Exception as e:
        print(f"Chatbot error: {str(e)}")
        # Provide a specific response even in case of errors
        query = user_message.lower()
        
        # Generate a well-structured response based on keywords in the query
        if 'laptop' in query:
            error_response = format_structured_response(
                "Laptops",
                "Portable computing devices available in various configurations for different needs.",
                [
                    "**Key Considerations**:",
                    "• **Processor**: Intel Core or AMD Ryzen series",
                    "• **Memory**: 8GB (minimum), 16GB (recommended), 32GB (professional)",
                    "• **Storage**: SSD for speed and reliability",
                    "• **Display**: Resolution, size, and panel type (IPS/OLED)",
                    "• **Battery Life**: 5-15 hours depending on model and usage"
                ],
                [
                    "**Popular Models**:",
                    "• **Apple**: MacBook Air, MacBook Pro",
                    "• **Dell**: XPS series, Inspiron",
                    "• **HP**: Spectre, Envy",
                    "• **Lenovo**: ThinkPad, Yoga",
                    "• **ASUS**: ZenBook, ROG (gaming)"
                ]
            )
        elif 'phone' in query or 'smartphone' in query:
            error_response = format_structured_response(
                "Smartphones",
                "Advanced mobile devices combining communication and computing capabilities.",
                [
                    "**Key Features to Consider**:",
                    "• **Operating System**: iOS (Apple) or Android",
                    "• **Processor**: Performance for apps and multitasking",
                    "• **Camera System**: Photo and video quality",
                    "• **Battery Life**: Capacity and charging speed",
                    "• **Display**: Size, resolution, and refresh rate"
                ],
                [
                    "**Leading Options**:",
                    "• **Apple**: iPhone 15 series",
                    "• **Samsung**: Galaxy S24 series",
                    "• **Google**: Pixel 8 series",
                    "• **Other**: OnePlus, Xiaomi, Nothing Phone"
                ]
            )
        elif 'gaming' in query:
            error_response = format_structured_response(
                "Gaming Technology",
                "Hardware optimized for gaming performance and immersive experiences.",
                [
                    "**PC Gaming Components**:",
                    "• **GPU**: NVIDIA RTX or AMD Radeon RX series",
                    "• **CPU**: Intel Core i7/i9 or AMD Ryzen 7/9",
                    "• **Memory**: 16GB+ DDR4/DDR5 RAM",
                    "• **Storage**: NVMe SSD for fast loading",
                    "• **Cooling**: Adequate airflow for sustained performance"
                ],
                [
                    "**Gaming Consoles**:",
                    "• **PlayStation 5**: Best for exclusive titles and controller features",
                    "• **Xbox Series X**: Powerful hardware with Game Pass subscription",
                    "• **Nintendo Switch**: Portable gaming with unique titles"
                ]
            )
        else:
            error_response = format_structured_response(
                "Technology Information",
                "I can provide detailed information about various technology products and categories.",
                [
                    "**Popular Categories**:",
                    "• **Computing**: Laptops, desktops, tablets",
                    "• **Mobile**: Smartphones, wearables",
                    "• **Audio/Visual**: Headphones, speakers, displays",
                    "• **Gaming**: Consoles, PC components",
                    "• **Smart Home**: IoT devices, automation"
                ],
                [
                    "**How I Can Help**:",
                    "• Compare different products and technologies",
                    "• Explain technical concepts and specifications",
                    "• Recommend solutions based on your needs",
                    "• Provide troubleshooting guidance",
                    "• Stay updated on the latest tech trends"
                ]
            )
        
        return jsonify({
            'response': error_response,
            'session_id': session_id
        })

def perform_web_search(user_message):
    """Search the web for information related to the user's query using DuckDuckGo"""
    try:
        # Clean up the query
        query = user_message.strip()
        
        # Add tech-related terms if appropriate
        tech_terms = ['tech', 'technology', 'gadget', 'device', 'computer', 'phone', 'laptop']
        category_terms = list(categories.keys()) + [info['name'].lower() for info in categories.values()]
        
        query_lower = query.lower()
        if not any(term in query_lower for term in tech_terms) and not any(term in query_lower for term in category_terms):
            query += " technology"
        
        print(f"Searching for: {query}")
        
        # Use DuckDuckGo API (which doesn't require authentication)
        search_url = f"https://api.duckduckgo.com/?q={query}&format=json&pretty=1"
        
        response = requests.get(search_url, timeout=10)
        
        if response.status_code == 200:
            try:
                data = response.json()
                
                # Extract the abstract text (main answer)
                abstract = data.get('Abstract', '')
                abstract_source = data.get('AbstractSource', '')
                
                # Extract related topics
                related_topics = data.get('RelatedTopics', [])
                
                # Format the results
                results = []
                
                # Add the abstract if available
                if abstract:
                    results.append(f"Information from {abstract_source}:\n{abstract}")
                
                # Add related topics
                if related_topics:
                    topics_text = "Related Information:\n"
                    for i, topic in enumerate(related_topics[:5], 1):  # Limit to 5 topics
                        if 'Text' in topic:
                            topics_text += f"{i}. {topic['Text']}\n"
                    
                    if len(topics_text) > 20:  # Only add if we have actual content
                        results.append(topics_text)
                
                # If we have results from DuckDuckGo, return them
                if results:
                    return "\n\n".join(results)
            except Exception as json_error:
                print(f"Error parsing DuckDuckGo response: {str(json_error)}")
        
        # If DuckDuckGo fails or returns no results, try our backup methods
        print("DuckDuckGo search failed or returned no results. Trying backup methods.")
        return backup_search(query)
    
    except Exception as e:
        print(f"Error in web search function: {str(e)}")
        # Fallback to backup search
        return backup_search(user_message)

def backup_search(query):
    """Backup search method when DuckDuckGo fails"""
    try:
        # Try to get information from our database first
        db_info = get_info_from_database(query)
        if db_info:
            return db_info
        
        # Try to get tech-specific information
        tech_info = get_tech_info(query)
        if tech_info:
            return tech_info
        
        # Last resort: Generate a response based on the query
        return generate_tech_response(query)
    except Exception as e:
        print(f"Error in backup search: {str(e)}")
        return generate_tech_response(query)

def get_info_from_database(query):
    """Get information from our database based on the query"""
    try:
        query_lower = query.lower()
        
        # Check for category matches
        for category_id, category_info in categories.items():
            if category_id in query_lower or category_info['name'].lower() in query_lower:
                # Get products from this category
                products = Product.query.filter_by(category_id=category_id).limit(5).all()
                if products:
                    result = f"Here's information about {category_info['name']} from our database:\n\n"
                    result += f"{category_info['description']}\n\n"
                    result += "Top products in this category:\n"
                    
                    for product in products:
                        result += f"- {product.name} ({product.brand}) - {product.price}\n"
                        
                        # Get key specs
                        specs = ProductSpec.query.filter_by(product_id=product.id).limit(3).all()
                        if specs:
                            for spec in specs:
                                result += f"  • {spec.spec_key.replace('_', ' ').title()}: {spec.spec_value}\n"
                    
                    return result
        
        # Check for brand matches
        common_brands = ['apple', 'samsung', 'dell', 'hp', 'lenovo', 'asus', 'acer', 'msi', 'lg', 'sony', 
                        'intel', 'amd', 'nvidia']
        
        for brand in common_brands:
            if brand in query_lower:
                # Get products from this brand
                products = Product.query.filter(Product.brand.ilike(f'%{brand}%')).limit(5).all()
                if products:
                    result = f"Here's information about {brand.upper()} products from our database:\n\n"
                    result += "Top products from this brand:\n"
                    
                    for product in products:
                        result += f"- {product.name} - {product.price}\n"
                        category_name = categories.get(product.category_id, {}).get('name', product.category_id)
                        result += f"  • Category: {category_name}\n"
                        
                        # Get key specs
                        specs = ProductSpec.query.filter_by(product_id=product.id).limit(2).all()
                        if specs:
                            for spec in specs:
                                result += f"  • {spec.spec_key.replace('_', ' ').title()}: {spec.spec_value}\n"
                    
                    return result
        
        # Check for specific product name matches
        words = [w for w in query_lower.split() if len(w) > 3 and w not in ['what', 'which', 'where', 'when', 'tell', 'about']]
        if words:
            for word in words:
                products = Product.query.filter(Product.name.ilike(f'%{word}%')).limit(3).all()
                if products:
                    result = f"Here's information about products matching '{word}' from our database:\n\n"
                    
                    for product in products:
                        result += f"- {product.name} ({product.brand}) - {product.price}\n"
                        category_name = categories.get(product.category_id, {}).get('name', product.category_id)
                        result += f"  • Category: {category_name}\n"
                        
                        # Get key specs
                        specs = ProductSpec.query.filter_by(product_id=product.id).limit(3).all()
                        if specs:
                            for spec in specs:
                                result += f"  • {spec.spec_key.replace('_', ' ').title()}: {spec.spec_value}\n"
                    
                    return result
        
        return None
    except Exception as e:
        print(f"Error getting info from database: {str(e)}")
        return None

def search_wikipedia(query):
    """Search Wikipedia for information"""
    try:
        # Format the query for Wikipedia API
        wiki_query = query.replace(' ', '+')
        wiki_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={wiki_query}&format=json&srlimit=1"
        
        response = requests.get(wiki_url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            search_results = data.get('query', {}).get('search', [])
            
            if search_results:
                result = search_results[0]
                title = result.get('title', '')
                snippet = result.get('snippet', '').replace('<span class="searchmatch">', '').replace('</span>', '')
                
                # Get the full page content
                page_url = f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exintro&titles={title.replace(' ', '_')}&format=json&explaintext"
                page_response = requests.get(page_url, timeout=5)
                
                if page_response.status_code == 200:
                    page_data = page_response.json()
                    pages = page_data.get('query', {}).get('pages', {})
                    
                    if pages:
                        # Get the first page (there should only be one)
                        page_id = list(pages.keys())[0]
                        extract = pages[page_id].get('extract', '')
                        
                        if extract:
                            # Limit the extract to a reasonable length
                            if len(extract) > 1000:
                                extract = extract[:1000] + "..."
                            
                            return f"Wikipedia Information:\n{title}\n\n{extract}\n\nSource: Wikipedia"
            
            return None
    except Exception as e:
        print(f"Error searching Wikipedia: {str(e)}")
        return None

def generate_tech_response(query):
    """Generate a response about technology based on the query when other methods fail"""
    try:
        query_lower = query.lower()
        current_year = datetime.now().year
        
        # Check for specific tech categories
        for category_id, category_info in categories.items():
            if category_id in query_lower or category_info['name'].lower() in query_lower:
                response = f"Information about {category_info['name']}:\n\n"
                response += f"{category_info['description']}\n\n"
                
                if category_id == 'laptops':
                    response += f"Key trends in laptops for {current_year}:\n"
                    response += "- Thinner and lighter designs with improved battery life\n"
                    response += "- More powerful processors from Intel, AMD, and Apple\n"
                    response += "- Higher resolution displays with better color accuracy\n"
                    response += "- AI-enhanced features for productivity and performance\n"
                    response += "- Improved cooling systems for better sustained performance\n\n"
                    response += "Popular laptop brands include Apple, Dell, HP, Lenovo, ASUS, and MSI."
                
                elif category_id == 'smartphones':
                    response += f"Key trends in smartphones for {current_year}:\n"
                    response += "- Advanced AI capabilities for photography and productivity\n"
                    response += "- Improved camera systems with computational photography\n"
                    response += "- Faster charging technologies and better battery life\n"
                    response += "- Higher refresh rate displays (120Hz+) becoming standard\n"
                    response += "- Foldable and rollable display innovations\n\n"
                    response += "Popular smartphone brands include Apple, Samsung, Google, Xiaomi, and OnePlus."
                
                elif category_id == 'cpus' or category_id == 'gpus':
                    response += f"Key trends in processors and graphics cards for {current_year}:\n"
                    response += "- Increased core counts and higher clock speeds\n"
                    response += "- Improved power efficiency with newer architectures\n"
                    response += "- Enhanced AI acceleration capabilities\n"
                    response += "- Better integration between CPU and GPU in APUs\n"
                    response += "- Ray tracing and upscaling technologies becoming standard\n\n"
                    response += "Leading CPU manufacturers are Intel, AMD, and Apple, while NVIDIA and AMD dominate the GPU market."
                
                elif category_id == 'audio':
                    response += f"Key trends in audio technology for {current_year}:\n"
                    response += "- Spatial audio and 3D sound experiences\n"
                    response += "- Advanced noise cancellation in headphones and earbuds\n"
                    response += "- Higher resolution audio formats and streaming\n"
                    response += "- Smart speakers with improved voice assistants\n"
                    response += "- True wireless earbuds with longer battery life\n\n"
                    response += "Popular audio brands include Sony, Bose, Apple, Sennheiser, and JBL."
                
                else:
                    response += f"This is a popular category in consumer technology with many options available from various manufacturers.\n\n"
                    response += f"For more specific information about {category_info['name']}, please ask a more detailed question."
                
                return response
        
        # Check for general tech terms
        if any(term in query_lower for term in ['tech', 'technology', 'gadget', 'device']):
            response = f"Technology Trends in {current_year}:\n\n"
            response += "1. Artificial Intelligence Integration\n"
            response += "   AI is becoming more prevalent in consumer devices, enhancing features like photography, productivity, and user experience.\n\n"
            response += "2. Sustainable Technology\n"
            response += "   Manufacturers are focusing on eco-friendly materials, energy efficiency, and recyclability.\n\n"
            response += "3. Extended Reality (XR)\n"
            response += "   VR, AR, and mixed reality technologies are advancing rapidly for both entertainment and productivity.\n\n"
            response += "4. Advanced Connectivity\n"
            response += "   5G adoption is expanding, and Wi-Fi 6E/7 is improving home and office networks.\n\n"
            response += "5. Smart Home Integration\n"
            response += "   More devices are becoming interconnected with improved standards like Matter for better compatibility.\n\n"
            response += "For more specific information, please ask about a particular technology category or product."
            return response
        
        # Default response for any tech query
        return f"I understand you're asking about '{query}'. For the most accurate and detailed information, please specify which aspect of technology you're interested in, such as a particular device category, brand, or feature."
    
    except Exception as e:
        print(f"Error generating tech response: {str(e)}")
        return f"I understand you're asking about technology related to '{query}'. To provide you with the most helpful information, could you please be more specific about what you'd like to know?"

def get_tech_info(query):
    """Get information from predefined tech sources based on the query"""
    try:
        # Check for specific tech terms in the query
        query_lower = query.lower()
        
        # Smartphone information
        if any(term in query_lower for term in ['iphone', 'apple phone']):
            return """iPhone Information:
            
The latest iPhone models include the iPhone 15 series, featuring the iPhone 15, iPhone 15 Plus, iPhone 15 Pro, and iPhone 15 Pro Max. 

Key features of the iPhone 15 Pro/Pro Max include:
- A17 Pro chip with 6-core CPU and 6-core GPU
- Titanium design, more durable and lighter than previous models
- USB-C port replacing Lightning
- 48MP main camera with improved low-light performance
- Action button replacing the mute switch
- ProMotion display with always-on capability

Source: Apple Official Website (as of late 2023)"""
        
        elif any(term in query_lower for term in ['samsung', 'galaxy']):
            return """Samsung Galaxy Information:
            
The latest Samsung Galaxy flagship models include the Galaxy S24 series, featuring the S24, S24+, and S24 Ultra.

Key features of the Galaxy S24 Ultra include:
- Snapdragon 8 Gen 3 processor (in most regions)
- 6.8-inch QHD+ Dynamic AMOLED 2X display
- 200MP main camera with advanced AI photography features
- S Pen stylus built into the device
- Up to 12GB RAM and 1TB storage
- Galaxy AI features for enhanced productivity
- 5000mAh battery with fast charging

Source: Samsung Official Website (as of early 2024)"""
        
        # Laptop information
        elif any(term in query_lower for term in ['macbook', 'apple laptop']):
            return """MacBook Information:
            
The latest MacBook models feature Apple Silicon processors, including:

MacBook Air:
- Available with M2 or M3 chips
- Fanless design for silent operation
- Up to 18 hours of battery life
- 13.6-inch or 15.3-inch Liquid Retina display options

MacBook Pro:
- Available with M3, M3 Pro, or M3 Max chips
- 14-inch and 16-inch models
- Liquid Retina XDR display with ProMotion
- Up to 22 hours of battery life
- Multiple Thunderbolt/USB 4 ports

Source: Apple Official Website (as of early 2024)"""
        
        # Gaming information
        elif any(term in query_lower for term in ['gaming', 'game']):
            return """Gaming Technology Information:
            
Latest gaming hardware trends include:

GPUs:
- NVIDIA RTX 40 series (4090, 4080, 4070, 4060) with DLSS 3 and Frame Generation
- AMD Radeon RX 7000 series with FSR 3.0 technology

Consoles:
- PlayStation 5 Pro rumored for late 2024
- Xbox Series X/S with expanding Game Pass library
- Nintendo Switch successor expected announcement

Gaming Laptops:
- Increasing adoption of high refresh rate displays (240Hz+)
- More efficient cooling solutions
- AI-enhanced gaming features

Source: Various Tech Publications (as of early 2024)"""
        
        # CPU/Processor information
        elif any(term in query_lower for term in ['cpu', 'processor']):
            return """CPU/Processor Information:
            
Latest CPU developments include:

Intel:
- 14th Gen Core processors (Raptor Lake Refresh)
- Core Ultra series (Meteor Lake) with integrated NPU for AI tasks
- Upcoming Arrow Lake architecture expected later in 2024

AMD:
- Ryzen 7000 series with Zen 4 architecture
- 3D V-Cache variants for gaming performance (7800X3D, 7950X3D)
- Ryzen 8000 series for mobile with integrated RDNA 3 graphics
- Upcoming Zen 5 architecture expected in 2024

Apple:
- M3 series chips (M3, M3 Pro, M3 Max, M3 Ultra)
- 3nm manufacturing process
- Improved CPU, GPU, and Neural Engine performance

Source: Intel, AMD, and Apple Official Information (as of early 2024)"""
        
        # AI and machine learning
        elif any(term in query_lower for term in ['ai', 'artificial intelligence', 'machine learning']):
            return """AI Technology Information:
            
Latest AI trends in consumer technology:

Smartphone AI:
- Apple Intelligence for iOS
- Google Gemini for Android
- Samsung Galaxy AI features

PC AI Acceleration:
- NPUs (Neural Processing Units) in modern CPUs
- NVIDIA RTX AI acceleration
- Microsoft Copilot integration in Windows

AI Models:
- GPT-4o and Claude 3 leading conversational AI
- Stable Diffusion XL and DALL-E 3 for image generation
- Sora and other video generation models

Source: Various Tech Publications (as of early 2024)"""
        
        return None
    
    except Exception as e:
        print(f"Error getting tech info: {str(e)}")
        return None

def simulate_search_results(query):
    """Simulate search results for when actual web search fails"""
    try:
        # Create a response based on the query terms
        query_lower = query.lower()
        current_year = datetime.now().year
        
        # Format the response as if it came from search results
        response = f"Search Results for: {query}\n\n"
        
        # Add tech category-specific information
        for category_id, category_info in categories.items():
            if category_id in query_lower or category_info['name'].lower() in query_lower:
                response += f"Category: {category_info['name']}\n"
                response += f"Description: {category_info['description']}\n\n"
                response += f"Top {category_info['name']} in {current_year}:\n"
                
                # Get some products from our database for this category
                products = Product.query.filter_by(category_id=category_id).limit(3).all()
                if products:
                    for product in products:
                        response += f"- {product.name} ({product.brand})\n"
                else:
                    # Fallback for common categories
                    if category_id == 'laptops':
                        response += "- Apple MacBook Pro 16 (M3 Max)\n- Dell XPS 17\n- ASUS ROG Zephyrus G16\n"
                    elif category_id == 'smartphones':
                        response += "- Samsung Galaxy S24 Ultra\n- Apple iPhone 15 Pro Max\n- Google Pixel 8 Pro\n"
                    elif category_id == 'cpus':
                        response += "- AMD Ryzen 9 7950X3D\n- Intel Core i9-14900KS\n- Apple M3 Max\n"
                    elif category_id == 'gpus':
                        response += "- NVIDIA GeForce RTX 4090\n- AMD Radeon RX 7900 XTX\n- NVIDIA GeForce RTX 4080 Super\n"
                
                response += "\nSource: TechRadar, Tom's Hardware, and The Verge (compiled information)"
                return response
        
        # If no specific category was found, provide general tech information
        response += f"Latest Technology Trends in {current_year}:\n"
        response += "- AI integration in consumer devices\n"
        response += "- Foldable and rollable display technology\n"
        response += "- Advanced AR/VR headsets\n"
        response += "- Improved battery technology\n"
        response += "- Sustainable and eco-friendly tech\n\n"
        response += "Source: Multiple technology publications (compiled information)"
        
        return response
    
    except Exception as e:
        print(f"Error simulating search results: {str(e)}")
        return None

def get_product_info_from_database(user_message):
    """Search the database for products that match the user's query and return formatted information"""
    try:
        # Convert message to lowercase for case-insensitive matching
        query = user_message.lower()
        
        # Extract potential product types, brands, or categories from the query
        product_types = []
        for category_id, category_info in categories.items():
            if category_id in query or category_info['name'].lower() in query:
                product_types.append(category_id)
        
        # Look for brand names in the query
        brands = []
        common_brands = ['apple', 'samsung', 'dell', 'hp', 'lenovo', 'asus', 'acer', 'msi', 'lg', 'sony', 
                        'intel', 'amd', 'nvidia', 'microsoft', 'google', 'oneplus', 'xiaomi', 'realme', 'oppo', 'vivo']
        for brand in common_brands:
            if brand in query:
                brands.append(brand)
        
        # Build the database query based on extracted information
        db_query = Product.query
        
        # Filter by category if detected
        if product_types:
            db_query = db_query.filter(Product.category_id.in_(product_types))
        
        # Filter by brand if detected
        if brands:
            brand_filters = [Product.brand.ilike(f'%{brand}%') for brand in brands]
            db_query = db_query.filter(db.or_(*brand_filters))
        
        # If no category or brand filters applied but there are words that might be product-related
        # try to match against product names
        if not product_types and not brands:
            # Get words that might be product-related (exclude common words)
            common_words = ['what', 'which', 'how', 'can', 'you', 'tell', 'me', 'about', 'is', 'are', 'the', 'best', 'good']
            potential_product_terms = [word for word in query.split() if word not in common_words and len(word) > 2]
            
            if potential_product_terms:
                name_filters = [Product.name.ilike(f'%{term}%') for term in potential_product_terms]
                db_query = db_query.filter(db.or_(*name_filters))
        
        # Limit to 5 products to avoid overwhelming responses
        products = db_query.limit(5).all()
        
        if not products:
            return None
        
        # Format the product information
        product_info = ""
        for product in products:
            # Get product specifications
            specs = ProductSpec.query.filter_by(product_id=product.id).all()
            specs_dict = {spec.spec_key: spec.spec_value for spec in specs}
            
            # Format key specifications (limit to most important ones)
            key_specs = []
            important_specs = ['processor', 'memory', 'storage', 'display', 'graphics', 'battery', 'camera', 'resolution']
            
            for spec_key in important_specs:
                if spec_key in specs_dict:
                    formatted_key = spec_key.replace('_', ' ').title()
                    key_specs.append(f"{formatted_key}: {specs_dict[spec_key]}")
            
            # Add formatted product information
            product_info += f"**{product.name}** ({product.brand})\n"
            product_info += f"Price: {product.price} | Rating: {product.rating}/5\n"
            product_info += "Key Specifications:\n"
            product_info += "\n".join([f"- {spec}" for spec in key_specs[:5]])  # Limit to 5 key specs
            product_info += "\n\n"
        
        return product_info
    except Exception as e:
        print(f"Error searching product database: {str(e)}")
        return None

def format_structured_response(title, description, section1=None, section2=None, section3=None, section4=None):
    """Format a response in a well-structured, easy-to-read format"""
    response = f"# {title}\n\n{description}\n\n"
    
    # Add sections if provided
    if section1:
        response += "\n".join(section1) + "\n\n"
    
    if section2:
        response += "\n".join(section2) + "\n\n"
    
    if section3:
        response += "\n".join(section3) + "\n\n"
    
    if section4:
        response += "\n".join(section4) + "\n\n"
    
    # Add a footer
    response += "---\n*For more detailed information or specific questions, please feel free to ask.*"
    
    return response

def analyze_sentiment(text):
    """Analyze the sentiment of a text message and return sentiment score and classification"""
    try:
        # Use TextBlob for sentiment analysis
        analysis = TextBlob(text)
        
        # Get polarity score (-1 to 1, where -1 is very negative, 1 is very positive)
        polarity = analysis.sentiment.polarity
        
        # Get subjectivity score (0 to 1, where 0 is objective, 1 is subjective)
        subjectivity = analysis.sentiment.subjectivity
        
        # Classify sentiment
        if polarity > 0.3:
            sentiment = "positive"
        elif polarity < -0.3:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        # Detect questions
        is_question = False
        if "?" in text or text.lower().startswith(('what', 'how', 'why', 'when', 'where', 'which', 'who', 'can', 'could', 'would', 'will', 'do', 'does', 'is', 'are')):
            is_question = True
        
        # Detect urgency
        urgency_words = ['urgent', 'immediately', 'asap', 'emergency', 'quickly', 'hurry', 'fast', 'soon']
        is_urgent = any(word in text.lower() for word in urgency_words)
        
        return {
            'polarity': polarity,
            'subjectivity': subjectivity,
            'sentiment': sentiment,
            'is_question': is_question,
            'is_urgent': is_urgent
        }
    except Exception as e:
        print(f"Error analyzing sentiment: {str(e)}")
        return {
            'polarity': 0,
            'subjectivity': 0,
            'sentiment': 'neutral',
            'is_question': False,
            'is_urgent': False
        }

def detect_language(text):
    """Detect the language of the input text"""
    try:
        # Use TextBlob for language detection
        blob = TextBlob(text)
        detected_language = blob.detect_language()
        return detected_language
    except Exception as e:
        print(f"Error detecting language: {str(e)}")
        return 'en'  # Default to English

def extract_user_preferences(message, session_id):
    """Extract user preferences from messages to personalize future responses"""
    try:
        message_lower = message.lower()
        
        # Initialize preference categories if they don't exist
        if 'categories' not in user_preferences[session_id]:
            user_preferences[session_id]['categories'] = []
        if 'brands' not in user_preferences[session_id]:
            user_preferences[session_id]['brands'] = []
        if 'price_range' not in user_preferences[session_id]:
            user_preferences[session_id]['price_range'] = {}
        if 'features' not in user_preferences[session_id]:
            user_preferences[session_id]['features'] = []
        
        # Category preferences
        for category_id, category_info in categories.items():
            if category_id in message_lower or category_info['name'].lower() in message_lower:
                if category_id not in user_preferences[session_id]['categories']:
                    user_preferences[session_id]['categories'].append(category_id)
        
        # Brand preferences
        common_brands = ['apple', 'samsung', 'dell', 'hp', 'lenovo', 'asus', 'acer', 'msi', 'lg', 'sony', 
                        'intel', 'amd', 'nvidia', 'microsoft', 'google', 'oneplus', 'xiaomi']
        
        for brand in common_brands:
            if brand in message_lower:
                if brand not in user_preferences[session_id]['brands']:
                    user_preferences[session_id]['brands'].append(brand)
        
        # Price range preferences
        budget_terms = {
            'budget': 'low',
            'cheap': 'low',
            'inexpensive': 'low',
            'affordable': 'low',
            'mid-range': 'medium',
            'mid range': 'medium',
            'middle': 'medium',
            'premium': 'high',
            'expensive': 'high',
            'high-end': 'high',
            'high end': 'high',
            'top': 'high'
        }
        
        for term, price_range in budget_terms.items():
            if term in message_lower:
                user_preferences[session_id]['price_range']['range'] = price_range
        
        # Extract specific price mentions
        price_pattern = r'\$?(\d+[,\d]*)(?:\s*-\s*\$?(\d+[,\d]*))?'
        price_matches = re.findall(price_pattern, message)
        
        if price_matches:
            for match in price_matches:
                try:
                    min_price = int(match[0].replace(',', ''))
                    if match[1]:  # If there's a range
                        max_price = int(match[1].replace(',', ''))
                    else:
                        max_price = min_price
                    
                    user_preferences[session_id]['price_range']['min'] = min_price
                    user_preferences[session_id]['price_range']['max'] = max_price
                except ValueError:
                    pass
        
        # Feature preferences
        feature_terms = [
            'battery life', 'performance', 'camera', 'display', 'screen', 'storage', 'memory', 
            'processor', 'graphics', 'gaming', 'lightweight', 'portable', 'durable', 'waterproof',
            'fast charging', 'wireless charging', '5g', 'wifi', 'bluetooth', 'usb', 'hdmi',
            'touchscreen', 'fingerprint', 'face recognition', 'stylus', 'keyboard'
        ]
        
        for feature in feature_terms:
            if feature in message_lower and feature not in user_preferences[session_id]['features']:
                user_preferences[session_id]['features'].append(feature)
        
        # Print extracted preferences for debugging
        print(f"Extracted preferences for session {session_id}: {user_preferences[session_id]}")
        
    except Exception as e:
        print(f"Error extracting user preferences: {str(e)}")

def get_fallback_response(message):
    """Provide fallback responses when OpenAI API is not available"""
    message = message.lower()
    
    # Basic keyword matching for common tech questions
    if any(word in message for word in ['best', 'recommend', 'top']):
        if 'laptop' in message:
            if 'gaming' in message:
                return "For gaming laptops, I'd recommend looking at models with at least an NVIDIA RTX 3060 GPU, 16GB RAM, and a high refresh rate display. Popular gaming laptop brands include ASUS ROG, MSI, Alienware, and Lenovo Legion."
            elif 'budget' in message:
                return "For budget laptops, consider models like the Acer Aspire 5, Lenovo IdeaPad 3, or HP Pavilion. Look for at least 8GB RAM and an SSD for better performance."
            else:
                return "When choosing a laptop, consider your specific needs. For general use, laptops with at least 8GB RAM, an SSD, and an Intel Core i5 or AMD Ryzen 5 processor offer good performance. Popular brands include Dell, HP, Lenovo, and ASUS."
        
        elif 'phone' in message or 'smartphone' in message:
            if 'android' in message:
                return "Top Android phones include the Samsung Galaxy S23 Ultra, Google Pixel 8 Pro, and OnePlus 11. Each offers different strengths in camera quality, performance, and software experience."
            elif 'iphone' in message or 'apple' in message:
                return "The latest iPhones offer excellent performance and camera quality. The iPhone 15 Pro and Pro Max are the premium options with the best cameras and performance, while the standard iPhone 15 offers great value."
            else:
                return "When choosing a smartphone, consider factors like camera quality, battery life, display, and software preferences. Top options include the iPhone 15 series, Samsung Galaxy S23 series, and Google Pixel 8 series."
        
        elif 'graphics card' in message or 'gpu' in message:
            if 'budget' in message:
                return "For budget gaming, consider the NVIDIA RTX 3050, RTX 3060, or AMD RX 6600. These offer good performance for 1080p gaming at a reasonable price."
            else:
                return "Top graphics cards include the NVIDIA RTX 4080 and 4090 for high-end performance, while the RTX 4070 offers excellent value. AMD's RX 7900 XTX is also a strong competitor at the high end."
        
        elif 'processor' in message or 'cpu' in message:
            return "Top CPUs include Intel's Core i9-13900K and AMD's Ryzen 9 7950X for high-end performance. For a balance of performance and value, consider the Intel Core i5-13600K or AMD Ryzen 7 7700X."
    
    elif 'compare' in message or 'vs' in message or 'versus' in message:
        if 'iphone' in message and ('samsung' in message or 'galaxy' in message):
            return "iPhone vs Samsung Galaxy: iPhones offer seamless iOS integration, longer software support, and typically better video recording. Samsung Galaxy phones offer more customization with Android, often have better displays, and usually provide more hardware features like expandable storage on some models."
        
        elif 'intel' in message and 'amd' in message:
            return "Intel vs AMD processors: Intel CPUs often have better single-core performance which benefits gaming, while AMD typically offers more cores at similar price points, benefiting multi-tasking and content creation. AMD has been more competitive in recent years with their Ryzen series."
        
        elif 'nvidia' in message and 'amd' in message:
            return "NVIDIA vs AMD graphics cards: NVIDIA generally offers better ray tracing performance and DLSS for AI upscaling. AMD cards often provide better value at lower price points and more VRAM. NVIDIA has stronger software features like CUDA for productivity applications."
        
        elif 'ssd' in message and 'hdd' in message:
            return "SSD vs HDD: SSDs are significantly faster, more durable with no moving parts, and consume less power. HDDs offer much lower cost per terabyte and are better for large storage needs where speed isn't critical. Many users opt for a smaller SSD for the operating system and a larger HDD for storage."
    
    elif 'how' in message:
        if 'choose' in message:
            if 'laptop' in message:
                return "When choosing a laptop, consider: 1) Your budget, 2) Primary use (gaming, work, general), 3) Desired portability (screen size, weight), 4) Battery life needs, 5) Performance requirements (processor, RAM, storage), and 6) Display quality. For most users, at least 8GB RAM and an SSD are recommended."
            elif 'phone' in message or 'smartphone' in message:
                return "When choosing a smartphone, consider: 1) Operating system preference (iOS or Android), 2) Budget, 3) Camera quality importance, 4) Battery life needs, 5) Display preferences (size, quality), 6) Storage needs, and 7) How long you plan to keep the device (iPhones typically receive updates longer)."
    
    elif 'what is' in message or 'what are' in message:
        if 'ram' in message:
            return "RAM (Random Access Memory) is your computer's short-term memory that temporarily stores data the CPU is actively using. More RAM allows your computer to work with more information at the same time, which can help with multitasking and running memory-intensive applications."
        elif 'ssd' in message:
            return "SSD (Solid State Drive) is a storage device that uses integrated circuit assemblies to store data persistently. SSDs are much faster than traditional HDDs (Hard Disk Drives) because they have no moving parts, allowing for quicker data access."
        elif 'cpu' in message or 'processor' in message:
            return "A CPU (Central Processing Unit) or processor is the primary component of a computer that performs most of the processing. It's essentially the 'brain' of your computer, executing instructions from programs by performing basic arithmetic, logic, controlling, and input/output operations."
        elif 'gpu' in message or 'graphics card' in message:
            return "A GPU (Graphics Processing Unit) or graphics card is specialized for displaying images, video rendering, and handling graphically intensive tasks. While originally designed for gaming and graphics work, GPUs are now also used for AI and machine learning due to their parallel processing capabilities."
    
    # Default response if no keywords match
    return "I'm your tech assistant and can help with product recommendations, comparisons, and technical information. Could you provide more details about what specific tech information you're looking for?"

# Create database and admin user if they don't exist
@app.before_first_request
def create_tables_and_admin():
    db.create_all()
    
    # Check if admin user exists
    admin = User.query.filter_by(is_admin=True).first()
    if not admin:
        # Create admin user
        hashed_password = generate_password_hash('admin123')
        admin_user = User(
            username='admin',
            email='admin@dueltech.com',
            password=hashed_password,
            is_admin=True
        )
        db.session.add(admin_user)
        db.session.commit()
        print("Admin user created!")
    
    # Instead of using the products dict that no longer exists,
    # check if we need to create sample products
    if Product.query.count() == 0:
        # Create a few sample products for each category
        for category_id in categories:
            for i in range(1, 6):  # Create 5 sample products per category
                product_id = f"{category_id}{i}"
                
                # Create product
                new_product = Product(
                    id=product_id,
                    name=f"Sample {categories[category_id]['name']} {i}",
                    price=f"₹{random.randint(10000, 100000):,}",
                    rating=round(random.uniform(3.5, 5.0), 1),
                    brand=random.choice(["Apple", "Samsung", "Dell", "HP", "Asus", "Lenovo", "MSI"]),
                    category_id=category_id
                )
                db.session.add(new_product)
                
                # Add some specs based on category
                specs = {}
                if category_id == 'laptops':
                    specs = {
                        'processor': random.choice(['Intel i7', 'Intel i9', 'AMD Ryzen 7', 'AMD Ryzen 9']),
                        'ram': f'{random.choice([8, 16, 32])}GB',
                        'storage': f'{random.choice([256, 512, 1024])}GB SSD',
                        'display': f'{random.choice([13.3, 14, 15.6])}inch'
                    }
                elif category_id == 'smartphones':
                    specs = {
                        'processor': random.choice(['Snapdragon 8 Gen 1', 'A15 Bionic', 'Exynos 2200']),
                        'ram': f'{random.choice([6, 8, 12])}GB',
                        'storage': f'{random.choice([128, 256, 512])}GB',
                        'camera': f'{random.choice([12, 48, 64, 108])}MP'
                    }
                else:
                    # Generic specs for other categories
                    specs = {
                        'feature1': random.choice(['Basic', 'Premium', 'Pro', 'Ultra']),
                        'feature2': f'Version {random.randint(1, 5)}',
                        'warranty': f'{random.choice([1, 2, 3])} years'
                    }
                
                # Add specs to database
                for spec_key, spec_value in specs.items():
                    new_spec = ProductSpec(
                        product_id=product_id,
                        spec_key=spec_key,
                        spec_value=spec_value
                    )
                    db.session.add(new_spec)
        
        db.session.commit()
        print("Sample products created successfully!")

# For local development
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

# For Vercel serverless function
def lambda_handler(event, context):
    return app
