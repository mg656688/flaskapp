from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import hashlib  # for password hashing
import jwt
from sqlalchemy.exc import IntegrityError

# Init app
app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'dp5.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['ENV'] = 'development'
app.config['DEBUG'] = True
secret_key = "SH15dsfv@Fs"
algo = "HS256"

# Init db
db = SQLAlchemy(app)


# Activity Class/Model
class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    place = db.Column(db.String(200))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    duration = db.Column(db.Integer)
    date = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, name, place, latitude, longitude, duration, user_id):
        self.name = name
        self.place = place
        self.latitude = latitude
        self.longitude = longitude
        self.duration = duration
        self.user_id = user_id


# User Class/Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(50))
    lastName = db.Column(db.String(50))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    gender = db.Column(db.String(2))
    birthdate = db.Column(db.DateTime)
    activities = db.relationship('Activity', backref='user', lazy=True)  # One-to-many relationship

    def __init__(self, firstName, lastName, email, password, gender, birthdate):
        self.firstName = firstName
        self.lastName = lastName
        self.email = email
        self.password = password
        self.gender = gender
        self.birthdate = birthdate


def hash_password(password):
    """Hashes a password using SHA-256."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(plain_password, hashed_password):
    """Verifies if a plain-text password matches the hashed password."""
    return hash_password(plain_password) == hashed_password


def generate_token(user_id, key, algorithm):
    """Generates a secure token string with user ID as payload."""
    payload = {'user_id': user_id}
    token = jwt.encode(payload, key, algorithm=algorithm)
    return token


# Create a user

@app.route('/register', methods=['POST'])
def create_user():
    try:
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        email = request.form.get('email')
        password = hash_password(request.form.get('password'))
        gender = request.form.get('gender')
        birthdate = datetime.strptime(request.form.get('birthdate'), '%Y-%m-%d')
        new_user = User(firstName, lastName, email, password, gender, birthdate)

        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            "id": new_user.id,
            "firstName": new_user.firstName,
            "lastName": new_user.lastName,
            "email": new_user.email,
            "gender": new_user.gender,
            "birthdate": new_user.birthdate.strftime('%Y-%m-%d')
        })
    except IntegrityError as e:
        db.session.rollback()  # Rollback the transaction
        return jsonify({"error": "Email address is already registered"}), 400


@app.route("/login", methods=["POST"])
def login():
    """Login a user (POST request to /login)"""
    email = request.form['email']
    password = request.form['password']

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Invalid email or password"}), 401

    if not verify_password(password, user.password):
        return jsonify({"error": "Invalid email or password"}), 401

    # Login successful
    token = generate_token(user.id, secret_key, algo)
    return jsonify({"message": "Login successful", "token": token}), 200


# Get All users
@app.route('/user', methods=['GET'])
def get_users():
    all_users = User.query.all()
    if not all_users:
        return jsonify({"error": "Not Found Users!!"}), 404

    users = []
    for user in all_users:
        user_data = {
            "id": user.id,
            "firstName": user.firstName,
            "lastName": user.lastName,
            "email": user.email,
            "gender": user.gender,
            "birthdate": user.birthdate.strftime('%Y-%m-%d')
        }
        users.append(user_data)

    return jsonify(users)


# Delete user
@app.route('/user/<id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({
        "message": "User deleted successfully",
        "user": {
            "id": user.id,
            "firstName": user.firstName,
            "lastName": user.lastName,
            "email": user.email,
            "gender": user.gender,
            "birthdate": user.birthdate.strftime('%Y-%m-%d')
        }
    })

# Create an Activity
@app.route('/activity', methods=['POST'])
def add_activity():
    data = request.form
    name = data.get('name')
    place = data.get('place')
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    duration = data.get('duration')
    user_id = data.get('user_id')

    # Check if the activity name is already taken for the user
    existing_activity = Activity.query.filter_by(name=name, user_id=user_id).first()
    if existing_activity:
        return jsonify({"error": "Activity '{}' already exists for this user".format(name)}), 400

    # Create a new activity
    new_activity = Activity(name, place, latitude, longitude, duration, user_id)

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Invalid user ID"}), 404

    user.activities.append(new_activity)
    db.session.add(new_activity)
    db.session.commit()

    return jsonify({
        "id": new_activity.id,
        "name": new_activity.name,
        "place": new_activity.place,
        "latitude": new_activity.latitude,
        "longitude": new_activity.longitude,
        "duration": new_activity.duration,
        "date": new_activity.date.strftime('%Y-%m-%d %H:%M:%S'),
        "user_id": new_activity.user_id
    })


# Get All Activities
@app.route('/activity', methods=['GET'])
def get_activities():
    all_activities = Activity.query.all()
    if not all_activities:
        return jsonify({"error": "No activities found"}), 404

    activities = []
    for activity in all_activities:
        activity_data = {
            "id": activity.id,
            "name": activity.name,
            "place": activity.place,
            "latitude": activity.latitude,
            "longitude": activity.longitude,
            "duration": activity.duration,
            "date": activity.date.strftime('%Y-%m-%d %H:%M:%S'),
            "user_id": activity.user_id
        }
        activities.append(activity_data)

    return jsonify(activities)


# Get Single Activity
@app.route('/activity/<id>', methods=['GET'])
def get_activity(id):
    activity = Activity.query.get(id)
    if not activity:
        return jsonify({"error": "Activity not found"}), 404

    activity_data = {
        "id": activity.id,
        "name": activity.name,
        "place": activity.place,
        "latitude": activity.latitude,
        "longitude": activity.longitude,
        "duration": activity.duration,
        "date": activity.date.strftime('%Y-%m-%d %H:%M:%S'),
        "user_id": activity.user_id
    }

    return jsonify(activity_data)


# Update an Activity
@app.route('/activity/<id>', methods=['PUT'])
def update_activity(id):
    activity = Activity.query.get(id)
    if not activity:
        return jsonify({"error": "Activity not found"}), 404

    activity.name = request.form.get('name')
    activity.place = request.form.get('place')
    activity.latitude = request.form.get('latitude')
    activity.longitude = request.form.get('longitude')
    activity.duration = request.form.get('duration')
    activity.date = datetime.strptime(request.form.get('date'), '%Y-%m-%d %H:%M:%S')

    db.session.commit()

    return jsonify({
        "id": activity.id,
        "name": activity.name,
        "place": activity.place,
        "latitude": activity.latitude,
        "longitude": activity.longitude,
        "duration": activity.duration,
        "date": activity.date.strftime('%Y-%m-%d %H:%M:%S'),
        "user_id": activity.user_id
    })


@app.route('/user/<user_id>/activities', methods=['GET'])
def get_user_activities(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    activities = []
    for activity in user.activities:
        activity_data = {
            "id": activity.id,
            "name": activity.name,
            "place": activity.place,
            "latitude": activity.latitude,
            "longitude": activity.longitude,
            "duration": activity.duration,
            "date": activity.date.strftime('%Y-%m-%d %H:%M:%S'),
            "user_id": activity.user_id
        }
        activities.append(activity_data)

    return jsonify(activities)


@app.route('/user/<user_id>/activities/<activity_id>', methods=['GET'])
def get_specific_user_activity(user_id, activity_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    activity = Activity.query.filter_by(user_id=user_id, id=activity_id).first()
    if not activity:
        return jsonify({"error": "Activity not found"}), 404

    activity_data = {
        "id": activity.id,
        "name": activity.name,
        "place": activity.place,
        "latitude": activity.latitude,
        "longitude": activity.longitude,
        "duration": activity.duration,
        "date": activity.date.strftime('%Y-%m-%d %H:%M:%S'),
        "user_id": activity.user_id
    }

    return jsonify(activity_data)


@app.route('/user/<user_id>/activities/<activity_id>', methods=['DELETE'])
def delete_specific_user_activity(user_id, activity_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    activity = Activity.query.filter_by(user_id=user_id, id=activity_id).first()
    if not activity:
        return jsonify({"error": "Activity not found"}), 404

    db.session.delete(activity)
    db.session.commit()

    return jsonify({
        "message": "Activity deleted successfully",
        "activity": {
            "id": activity.id,
            "name": activity.name,
            "place": activity.place,
            "latitude": activity.latitude,
            "longitude": activity.longitude,
            "duration": activity.duration,
            "date": activity.date.strftime('%Y-%m-%d %H:%M:%S'),
            "user_id": activity.user_id
        }
    })


# with app.app_context():
#     db.create_all()

# Run Server
if __name__ == '__main__':
    app.run(debug=True)
