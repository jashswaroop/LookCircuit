from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(256))
    wardrobe_items = db.relationship('WardrobeItem', backref='owner', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class WardrobeItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    brand = db.Column(db.String(128))
    size = db.Column(db.String(64))
    color = db.Column(db.String(64))
    image_url = db.Column(db.String(256))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not 'username' in data or not 'email' in data or not 'password' in data:
        return jsonify({'message': 'Missing data'}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already taken'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already registered'}), 400

    user = User(username=data['username'], email=data['email'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not 'email' in data or not 'password' in data:
        return jsonify({'message': 'Missing data'}), 400

    user = User.query.filter_by(email=data['email']).first()

    if user is None or not user.check_password(data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401

    return jsonify({'message': 'Login successful'}), 200

@app.route('/wardrobe/add', methods=['POST'])
def add_wardrobe_item():
    data = request.get_json()
    if not data or not 'name' in data or not 'image_url' in data:
        return jsonify({'message': 'Missing data'}), 400

    # In a real app, you would get the user_id from the session or token
    user_id = 1
    item = WardrobeItem(
        name=data['name'],
        brand=data.get('brand'),
        size=data.get('size'),
        color=data.get('color'),
        image_url=data['image_url'],
        user_id=user_id
    )
    db.session.add(item)
    db.session.commit()

    return jsonify({'message': 'Item added to wardrobe'}), 201

@app.route('/wardrobe', methods=['GET'])
def get_wardrobe_items():
    # In a real app, you would get the user_id from the session or token
    user_id = 1
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    items = []
    for item in user.wardrobe_items:
        items.append({
            'id': item.id,
            'name': item.name,
            'brand': item.brand,
            'size': item.size,
            'color': item.color,
            'image_url': item.image_url
        })

    return jsonify(items), 200

@app.route('/wardrobe/<int:item_id>', methods=['GET'])
def get_wardrobe_item(item_id):
    item = WardrobeItem.query.get(item_id)
    if not item:
        return jsonify({'message': 'Item not found'}), 404

    return jsonify({
        'id': item.id,
        'name': item.name,
        'brand': item.brand,
        'size': item.size,
        'color': item.color,
        'image_url': item.image_url
    }), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
