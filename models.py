from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import DECIMAL, JSON
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable = False)
    fullname = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    bookings = db.relationship('Booking', back_populates='user')

class Driver(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    driver_id = db.Column(db.Integer, nullable = False)
    fullname = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    vehicle = db.Column(db.String(50), nullable = False)
    base_price = db.Column(DECIMAL(10,2),nullable = False)
    base_distance_KM = db.Column(db.Integer, nullable = False)
    price_per_km = db.Column(DECIMAL(10,2), nullable = False)
    make = db.Column(db.Integer, nullable = True)
    model = db.Column(db.String(50), nullable = True)
    license_plate = db.Column(db.String(100), nullable = True)
    latitude = db.Column(db.String(200), nullable = True)
    longitude = db.Column(db.String(200), nullable = True)
    status = db.Column(db.String(200), default = 'inactive')
    bookings = db.relationship('Booking', back_populates='driver')
    cancelledride = db.relationship('CancelledRide', back_populates = 'driver')

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'), nullable=True)
    scheduled_time = db.Column(db.Time, nullable=True)
    scheduled_date = db.Column(db.Date, nullable=True)
    from_location = db.Column(db.String(100), nullable=False)
    to_location = db.Column(db.String(100), nullable=False)
    total_km = db.Column(db.Float, nullable=False)
    vehicle_type = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    fare = db.Column(DECIMAL(10, 2), nullable=False)
    user = db.relationship('User', back_populates='bookings')
    driver = db.relationship('Driver', back_populates='bookings')
    cancelledride = db.relationship('CancelledRide', back_populates = 'booking')
    bookingdetails = db.relationship('Bookingdetails', back_populates = 'booking')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Bookingdetails(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_latitude = db.Column(db.String(200), nullable = True)
    user_longitude = db.Column(db.String(200), nullable = True)
    directions_data = db.Column(JSON, nullable=False)
    distance = db.Column(db.String(50), nullable = False)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    booking = db.relationship('Booking', back_populates='bookingdetails')

class CancelledRide(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    reason = db.Column(db.String(200), nullable = False)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'), nullable = False)
    booking = db.relationship('Booking', back_populates='cancelledride')
    driver = db.relationship('Driver', back_populates='cancelledride')