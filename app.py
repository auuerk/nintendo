from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_cors import CORS
from datetime import timedelta

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://aruuke:aruuke123@localhost:5432/shopping_platform'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def get_id(self):
        return self.user_id

class Genre(db.Model):
    __tablename__ = 'genre'
    genre_id = db.Column(db.Integer, primary_key=True)
    genre_name = db.Column(db.String(100), unique=True, nullable=False)

class Publisher(db.Model):
    __tablename__ = 'publisher'
    publisher_id = db.Column(db.Integer, primary_key=True)
    publisher_name = db.Column(db.String(100), unique=True, nullable=False)

class ESRBRating(db.Model):
    __tablename__ = 'esrb_rating'
    esrb_id = db.Column(db.Integer, primary_key=True)
    rating_name = db.Column(db.String(20), unique=True, nullable=False)

class NumberOfPlayers(db.Model):
    __tablename__ = 'number_of_players'
    players_id = db.Column(db.Integer, primary_key=True)
    players_count = db.Column(db.String(20), unique=True, nullable=False)

class SupportedLanguage(db.Model):
    __tablename__ = 'supported_languages'
    lang_id = db.Column(db.Integer, primary_key=True)
    language_name = db.Column(db.String(100), unique=True, nullable=False)

class Game(db.Model):
    __tablename__ = 'games'
    game_id = db.Column(db.Integer, primary_key=True)
    game_name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    release_date = db.Column(db.Date, nullable=False)
    genre_id = db.Column(db.Integer, db.ForeignKey('genre.genre_id'), nullable=False)
    publisher_id = db.Column(db.Integer, db.ForeignKey('publisher.publisher_id'), nullable=False)
    esrb_id = db.Column(db.Integer, db.ForeignKey('esrb_rating.esrb_id'), nullable=False)
    players_id = db.Column(db.Integer, db.ForeignKey('number_of_players.players_id'), nullable=False)
    game_file_size = db.Column(db.String(20))
    country_of_origin = db.Column(db.String(100))
    play_modes = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    stock_quantity = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    genre = relationship('Genre', backref='games')
    publisher = relationship('Publisher', backref='games')
    esrb = relationship('ESRBRating', backref='games')
    players = relationship('NumberOfPlayers', backref='games')

    def __repr__(self):
        return f"Game('{self.game_name}', '{self.price}')"
class Hardware(db.Model):
    __tablename__ = 'hardware'
    hardware_id = db.Column(db.Integer, primary_key=True)
    hardware_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.Text)
    country_of_origin = db.Column(db.String(100))
    manufacturer = db.Column(db.String(100))
    sku = db.Column(db.String(50))
    upc = db.Column(db.String(50))
    play_modes = db.Column(db.Text)
    screen_size = db.Column(db.String(50))
    battery_life = db.Column(db.String(50))
    image_url = db.Column(db.String(255))
    stock_quantity = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f"Hardware('{self.hardware_name}', '{self.price}')"

class GameSupportedLanguage(db.Model):
    __tablename__ = 'games_supported_languages'
    game_id = db.Column(db.Integer, db.ForeignKey('games.game_id'), primary_key=True)
    lang_id = db.Column(db.Integer, db.ForeignKey('supported_languages.lang_id'), primary_key=True)
    __table_args__ = (db.UniqueConstraint('game_id', 'lang_id', name='unique_languages_per_game'),)

class Cart(db.Model):
    __tablename__ = 'cart'
    cart_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('games.game_id'))
    hardware_id = db.Column(db.Integer, db.ForeignKey('hardware.hardware_id'))
    quantity = db.Column(db.Integer, default=1)
    added_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class PurchaseHistory(db.Model):
    __tablename__ = 'purchase_history'
    purchase_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('games.game_id'))
    hardware_id = db.Column(db.Integer, db.ForeignKey('hardware.hardware_id'))
    quantity = db.Column(db.Integer, default=1)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    purchase_date = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Define relationships
    game = db.relationship('Game', backref=db.backref('purchases', lazy='dynamic'))
    hardware = db.relationship('Hardware', backref=db.backref('purchases', lazy='dynamic'))

    def __repr__(self):
        return f'<PurchaseHistory purchase_id={self.purchase_id}>'
class Address(db.Model):
    __tablename__ = 'addresses'
    address_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    address_line1 = db.Column(db.String(255), nullable=False)
    address_line2 = db.Column(db.String(255))
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(100), nullable=False)

class Shipment(db.Model):
    __tablename__ = 'shipment'
    shipment_id = db.Column(db.Integer, primary_key=True)
    purchase_id = db.Column(db.Integer, db.ForeignKey('purchase_history.purchase_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    address_id = db.Column(db.Integer, db.ForeignKey('addresses.address_id'), nullable=False)
    shipment_method = db.Column(db.String(50))
    tracking_number = db.Column(db.String(100))
    shipment_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    status = db.Column(db.String(20), default='Pending')




# User loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        new_user = User(username=username, email=email, password_hash=hashed_password, full_name=request.form['full_name'])
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=True, duration=timedelta(days=7))
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    flash('Logout successful!', 'success')
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    else:
        return redirect(url_for('user_dashboard'))

@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        return redirect(url_for('home'))
    return render_template('admin_dashboard.html')

@app.route('/user')
@login_required
def user_dashboard():
    return render_template('user_dashboard.html', user=current_user)

@app.route('/products')
def products():
    games = Game.query.all()
    hardware_items = Hardware.query.all()
    return render_template('products.html', games=games, hardware_items=hardware_items)


@app.route('/product/<string:product_type>/<int:product_id>')
def product_detail(product_type, product_id):
    if product_type == 'game':
        product = Game.query.get(product_id)
        if product:
            product_type = 'game'
            product_name = product.game_name
            product_description = product.description
            product_price = product.price
            product_image_url = product.image_url
            product_release_date = product.release_date
            product_genre = product.genre.genre_name if product.genre else ""
            product_publisher = product.publisher.publisher_name if product.publisher else ""
            product_esrb = product.esrb.rating_name if product.esrb else ""
            product_players = product.players.players_count if product.players else ""
            product_game_file_size = product.game_file_size
            product_play_modes = product.play_modes
            product_stock_quantity = product.stock_quantity
            product_sku = None
            product_upc = None
            product_screen_size = None
            product_battery_life = None
            product_manufacturer = None
            product_country_of_origin = None
            return render_template('product_detail.html', **locals())
    elif product_type == 'hardware':
        product = Hardware.query.get(product_id)
        if product:
            product_type = 'hardware'
            product_name = product.hardware_name
            product_description = product.description
            product_price = product.price
            product_image_url = product.image_url
            product_release_date = None
            product_genre = None
            product_publisher = None
            product_esrb = None
            product_players = None
            product_game_file_size = None
            product_country_of_origin = product.country_of_origin
            product_stock_quantity = product.stock_quantity
            product_play_modes = product.play_modes
            product_manufacturer = product.manufacturer
            product_sku = product.sku
            product_upc = product.upc
            product_screen_size = product.screen_size
            product_battery_life = product.battery_life
            return render_template('product_detail.html', **locals())

    flash('Product not found!', 'danger')
    return redirect(url_for('home'))


@app.route('/admin/users')
@login_required
def manage_users():
    if not current_user.is_admin:
        return redirect(url_for('home'))
    users = User.query.all()
    return render_template('admin_users.html', users=users)

@app.route('/admin/user/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if not current_user.is_admin:
        return redirect(url_for('home'))
    user = User.query.get(user_id)
    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        user.full_name = request.form['full_name']
        user.is_admin = 'is_admin' in request.form
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('manage_users'))
    return render_template('edit_user.html', user=user)

@app.route('/admin/products')
@login_required
def manage_products():
    if not current_user.is_admin:
        return redirect(url_for('home'))
    games = Game.query.all()
    hardware = Hardware.query.all()
    return render_template('manage_products.html', games=games, hardware=hardware)

@app.route('/admin/product/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    if not current_user.is_admin:
        return redirect(url_for('home'))
    game = Game.query.get(product_id)
    hardware = Hardware.query.get(product_id)
    if request.method == 'POST':
        if game:
            game.game_name = request.form['game_name']
            game.description = request.form['description']
            game.price = request.form['price']
            game.release_date = request.form['release_date']
            game.genre_id = request.form['genre_id']
            game.publisher_id = request.form['publisher_id']
            game.esrb_id = request.form['esrb_id']
            game.players_id = request.form['players_id']
            game.game_file_size = request.form['game_file_size']
            game.country_of_origin = request.form['country_of_origin']
            game.play_modes = request.form['play_modes']
            game.image_url = request.form['image_url']
            game.stock_quantity = request.form['stock_quantity']
            db.session.commit()
        elif hardware:
            hardware.hardware_name = request.form['hardware_name']
            hardware.price = request.form['price']
            hardware.description = request.form['description']
            hardware.country_of_origin = request.form['country_of_origin']
            hardware.manufacturer = request.form['manufacturer']
            hardware.sku = request.form['sku']
            hardware.upc = request.form['upc']
            hardware.play_modes = request.form['play_modes']
            hardware.screen_size = request.form['screen_size']
            hardware.battery_life = request.form['battery_life']
            hardware.image_url = request.form['image_url']
            hardware.stock_quantity = request.form['stock_quantity']
            db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('manage_products'))
    return render_template('edit_product.html', game=game, hardware=hardware)


@app.route('/update_cart_item', methods=['POST'])
@login_required
def update_cart_item():
    user_id = current_user.user_id
    product_id = request.form.get('product_id')
    product_type = request.form.get('product_type')
    quantity = int(request.form.get('quantity'))

    # Find the cart item to update
    if product_type == 'game':
        cart_item = Cart.query.filter_by(user_id=user_id, game_id=product_id).first()
    elif product_type == 'hardware':
        cart_item = Cart.query.filter_by(user_id=user_id, hardware_id=product_id).first()
    else:
        return jsonify({'error': 'Invalid product type'})

    if cart_item:
        cart_item.quantity = quantity
        db.session.commit()
        flash('Cart updated successfully!', 'success')
    else:
        flash('Item not found in cart!', 'danger')

    return redirect(url_for('cart'))

@app.route('/remove_from_cart', methods=['POST'])
@login_required
def remove_from_cart():
    user_id = current_user.user_id
    product_id = request.form.get('product_id')
    product_type = request.form.get('product_type')

    # Find the cart item to remove
    if product_type == 'game':
        cart_item = Cart.query.filter_by(user_id=user_id, game_id=product_id).first()
    elif product_type == 'hardware':
        cart_item = Cart.query.filter_by(user_id=user_id, hardware_id=product_id).first()
    else:
        return jsonify({'error': 'Invalid product type'})

    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        flash('Item removed from cart!', 'success')
    else:
        flash('Item not found in cart!', 'danger')

    return redirect(url_for('cart'))

@app.route('/cart')
@login_required
def cart():
    user_id = current_user.user_id
    cart_items = Cart.query.filter_by(user_id=user_id).all()

    formatted_cart_items = []
    total_price = 0

    for item in cart_items:
        if item.game_id:
            product = Game.query.get(item.game_id)
            product_name = product.game_name
            product_type = 'game'
        elif item.hardware_id:
            product = Hardware.query.get(item.hardware_id)
            product_name = product.hardware_name
            product_type = 'hardware'
        else:
            product = None
            product_name = "Unknown Product"
            product_type = ""

        if product:
            price = product.price
        else:
            price = 0

        item_price = item.quantity * price
        total_price += item_price

        formatted_cart_items.append({
            'product_name': product_name,
            'quantity': item.quantity,
            'price': price,
            'item_price': item_price,
            'product_id': item.game_id or item.hardware_id,
            'product_type': product_type
        })

    return render_template('cart.html', cart_items=formatted_cart_items, total_price=total_price)




@app.route('/add_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    user_id = current_user.user_id
    product_id = request.form.get('product_id')
    product_type = request.form.get('product_type')
    quantity = int(request.form.get('quantity'))

    # Example logic to add items to cart
    if product_type == 'game':
        cart_item = Cart.query.filter_by(user_id=user_id, game_id=product_id).first()
        if cart_item:
            cart_item.quantity += quantity
        else:
            cart_item = Cart(user_id=user_id, game_id=product_id, quantity=quantity)
            db.session.add(cart_item)
    elif product_type == 'hardware':
        cart_item = Cart.query.filter_by(user_id=user_id, hardware_id=product_id).first()
        if cart_item:
            cart_item.quantity += quantity
        else:
            cart_item = Cart(user_id=user_id, hardware_id=product_id, quantity=quantity)
            db.session.add(cart_item)
    else:
        return jsonify({'error': 'Invalid product type'})

    db.session.commit()
    return jsonify({'message': 'Item added to cart'})


from flask import flash, redirect, render_template, request, url_for
from datetime import datetime


@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if request.method == 'POST':
        # Dummy logic to simulate checkout process
        # In a real application, you would process the payment, update order status, etc.
        # Here, we'll just flash a message indicating successful checkout
        flash('Checkout Successful! Your order has been processed.', 'success')

        # Update purchase history
        user_id = current_user.user_id
        cart_items = Cart.query.filter_by(user_id=user_id).all()
        total_price = 0  # Initialize total price

        if cart_items:
            for item in cart_items:
                if item.game_id:
                    product = Game.query.get(item.game_id)
                elif item.hardware_id:
                    product = Hardware.query.get(item.hardware_id)
                else:
                    continue  # Skip if neither game nor hardware

                if product:
                    item_price = item.quantity * product.price
                    total_price += item_price

                    purchase = PurchaseHistory(
                        user_id=user_id,
                        game_id=item.game_id,
                        hardware_id=item.hardware_id,
                        quantity=item.quantity,
                        total_price=item_price,
                        purchase_date=datetime.now()
                    )
                    db.session.add(purchase)

            # Delete cart items after successful checkout
            Cart.query.filter_by(user_id=user_id).delete()
            db.session.commit()

        # Redirect back to cart after successful checkout
        return redirect(url_for('cart'))

    # If GET request, render the checkout page
    return render_template('checkout.html')

@app.route('/purchase_history')
@login_required
def purchase_history():
    purchases = PurchaseHistory.query.filter_by(user_id=current_user.user_id).all()
    return render_template('purchase_history.html', purchases=purchases)


if __name__ == '__main__':
    app.run(debug=True)
