from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    bookings = db.relationship('Booking', backref='user', lazy=True)

class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    theatres = db.relationship('Theatre', backref='city', lazy=True)

class Theatre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'), nullable=False)
    screens = db.relationship('Screen', backref='theatre', lazy=True)

class Screen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    theatre_id = db.Column(db.Integer, db.ForeignKey('theatre.id'), nullable=False)
    available_slots = db.Column(db.String(500), default="11:00,13:00,15:00,17:00,19:00,20:00")
    bookings = db.relationship('Booking', backref='screen', lazy=True)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    screen_id = db.Column(db.Integer, db.ForeignKey('screen.id'), nullable=False)
    booking_date = db.Column(db.String(20), nullable=False)
    booking_time = db.Column(db.String(10), nullable=False)
    occasion = db.Column(db.String(50), nullable=False)
    movie_preference = db.Column(db.String(200), nullable=True)
    message = db.Column(db.Text)
    media_file = db.Column(db.String(255))
    cake = db.Column(db.Boolean, default=False)
    balloons = db.Column(db.Boolean, default=False)
    decoration = db.Column(db.Boolean, default=False)
    party_poppers = db.Column(db.Boolean, default=False)
    flowers = db.Column(db.Boolean, default=False)
    chocolate_bouquet = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)