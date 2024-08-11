from flask import Flask, jsonify, json, request, current_app
from models import db, User, Driver, Booking, CancelledRide, Bookingdetails
from flask_migrate import Migrate
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
from geopy.distance import geodesic
import random, requests, eventlet, os, urllib.parse
from sqlalchemy import desc, or_, not_, and_, func
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError
import calendar
import eventlet
import eventlet.wsgi

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://booking:booking@localhost:33066/booking'
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://booking:booking@host.docker.internal:33066/booking'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    migrate = Migrate(app, db)
    db.init_app(app)
    CORS(app, supports_credentials=True)
    GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
    socketio = SocketIO(app, cors_allowed_origins="*",  async_mode='eventlet')

    @app.route('/get_driver',methods = ['POST'])
    def get_driver():
        data = request.get_json()
        distinct_vehicle_types = (
        db.session.query(Driver.vehicle)
        .filter(Driver.status == 'active')
        .distinct()
        .all()
        )
        vehicle_types_list = [item[0] for item in distinct_vehicle_types]
        print(vehicle_types_list)
        vehicle_type_obj = [{'id':1, 'type': vehicle_type} for vehicle_type in vehicle_types_list]
        print(vehicle_type_obj)
        print(data['origin']['query'])
        print(data['destination']['query'])
        return jsonify({'message':'ok','vehicles':vehicle_type_obj})

    @app.route('/getprice',methods = ["POST"])
    def get_price():
        try:
            data = request.get_json()
            price = Driver.query.filter_by(vehicle = data['vehicle']).first()
            total = price.base_price
            if data['distance'] > price.base_distance_KM:
                total = float(price.base_price)+(float(price.price_per_km) * (data['distance']-price.base_distance_KM))
            return jsonify({'message':'ok','total':total+30})
        except:
            return jsonify({'message':'error'})

    def calculate_distance(user_coords, driver_coords):
        return geodesic(user_coords, driver_coords).kilometers

    @app.route('/riderequest', methods=['POST'])
    def riderequest():
        data = request.get_json()
        print(data)
        if data['email'] is None:
            return jsonify({'message':'user not found'})
        
        user_coords = (data['latitude'], data['longitude'])
        vehicle_type = data['vehicle']
        print(vehicle_type)
        drivers = Driver.query.filter_by(vehicle=vehicle_type, status='active').all()

        eligible_drivers = []
        for driver in drivers:
            driver_coords = (driver.latitude, driver.longitude)
            dist_km = calculate_distance(user_coords, driver_coords)
            print('sdhaskfhasji',dist_km)
            if dist_km <= 20:
                eligible_drivers.append(driver)
                
        if eligible_drivers:
            print(data['email'])
            user = User.query.filter_by(email = data['email']).first()
            print(user)
            selected_driver = eligible_drivers[0]
            socketio.emit('notification', {
                'message': 'New Booking Created!',
                'price': float(data['price']) - float(30),
                'direction': data['direction'],
                'distance': data['distance'],
                'user_id':user.user_id,
                'driver_id':selected_driver.id,
                'vehicle':vehicle_type
            }, room=selected_driver.email)

            selected_driver.status = 'onrequest'
            db.session.commit()

            km = float(data['distance'].split(' ')[0])
            try:
                booking = Booking(
                    user_id=user.id,
                    driver_id=selected_driver.id,
                    from_location=data['direction']['request']['origin']['query'],
                    to_location=data['direction']['request']['destination']['query'],
                    total_km=km,
                    vehicle_type=data['vehicle'],
                    status='pending',
                    fare=float(data['price']) - float(30)
                )
                db.session.add(booking)
                db.session.flush()  

                bookingdetails = Bookingdetails(
                    user_latitude=data['latitude'],
                    user_longitude=data['longitude'],
                    directions_data=data['direction'],
                    distance=data['distance'],
                    booking_id=booking.id
                )
                db.session.add(bookingdetails)
                db.session.commit()

            except SQLAlchemyError as e:
                db.session.rollback()
                print(f"Error occurred: {e}")

            return jsonify({'message': 'searching for driver','userid':user.id,'driverid':eligible_drivers[0].id})
        else:
            return jsonify({'message': 'driver is not available'})

    @socketio.on('connect')
    def handle_connect():
        email = request.args.get('email')
        join_room(email)
        emit('message', {'data': f'Connected as {email}'})
    
    @app.route('/getnotifications',methods = ['POST'])
    def getnotifications():
        try:
            data = request.get_json()
            print(data)
            driver = Driver.query.filter_by(email = data['email']).first()
            booking = Booking.query.filter_by(driver_id = driver.id).order_by(desc(Booking.id)).all()
            notification = []
            for i in booking:
                notification.append({'id':i.id,'time':i.scheduled_time,'user_id':i.user_id, 'driver_id':i.driver_id, 'date':i.scheduled_date, 'from':i.from_location, 'to':i.to_location, 'km':i.total_km, 'status':i.status, 'fare':i.fare})
            print(notification)
            return jsonify({'message':notification})
        except:
            return jsonify({'message':'error'})

    @app.route('/cancelrequest',methods = ["POST"])
    def cancelrequest():
        data = request.get_json()

        booking = Booking.query.filter_by(id = data['id']).first()
        driver = Driver.query.filter_by(email = data['email']).first()
        user = User.query.filter_by(user_id = data['user_id']).first()

        cancelled = CancelledRide(booking_id = booking.id, reason = data['reason'], driver_id = driver.id)
        booking_details = Bookingdetails.query.filter_by(booking_id = booking.id).first()
        driver.status = 'active'
        booking.status = 'cancelled by driver'

        db.session.add(cancelled)
        db.session.commit() 
   
        try:
            ten_minutes_ago = datetime.utcnow() - timedelta(minutes=5)
            bookings = Booking.query.filter(
                Booking.user_id == user.id,
                Booking.status == 'cancelled by driver',
                Booking.created_at >= ten_minutes_ago
            ).all()
            cancelled_drivers = [i.driver_id for i in bookings]
            print(cancelled_drivers)
            drivers = Driver.query.filter(
                and_(
                    not_(Driver.id.in_(cancelled_drivers)),
                    Driver.status == 'active',
                    Driver.vehicle == booking.vehicle_type
                )
            ).all()
            print(drivers)

            eligible_drivers = []
         
            user_coords = (booking_details.user_latitude,booking_details.user_longitude)
            for driver in drivers:
                driver_coords = (driver.latitude, driver.longitude)
                dist_km = calculate_distance(user_coords, driver_coords)
                if dist_km <= 20:
                    eligible_drivers.append(driver)
            print('finished')
            print(eligible_drivers)
            if eligible_drivers:
                selected_driver = eligible_drivers[0]
                socketio.emit('notification', {
                    'message': 'New Booking Created!',
                    'price': float(booking.fare),
                    'direction': booking_details.directions_data,
                    'distance': booking_details.distance,
                    'user_id':booking.user_id,
                    'driver_id':selected_driver.id,
                    'vehicle':booking.vehicle_type
                }, room=selected_driver.email)
                selected_driver.status = 'onrequest'
                db.session.commit()
                print('emitted')

                try:
                    booking = Booking(
                        user_id=booking.user_id,
                        driver_id=selected_driver.id,
                        from_location=booking.from_location,
                        to_location=booking.to_location,
                        total_km=booking.total_km,
                        vehicle_type=booking.vehicle_type,
                        status='pending',
                        fare=booking.fare
                    )
                    db.session.add(booking)
                    db.session.flush()  

                    bookingdetails = Bookingdetails(
                        user_latitude=booking_details.user_latitude,
                        user_longitude=booking_details.user_longitude,
                        directions_data=booking_details.directions_data,
                        distance=booking_details.distance,
                        booking_id=booking.id
                    )
                    db.session.add(bookingdetails)
                    db.session.commit()

                except SQLAlchemyError as e:
                    db.session.rollback()
                    print(f"Error occurred: {e}")
                
            else:
                try:
                    booking = Booking(
                        user_id=booking.user_id,
                        from_location=booking.from_location,
                        to_location=booking.to_location,
                        total_km=booking.total_km,
                        vehicle_type=booking.vehicle_type,
                        status='driver not available',
                        fare=booking.fare
                    )
                    db.session.add(booking)
                    db.session.flush()  

                    bookingdetails = Bookingdetails(
                        user_latitude=booking_details.user_latitude,
                        user_longitude=booking_details.user_longitude,
                        directions_data=booking_details.directions_data,
                        distance=booking_details.distance,
                        booking_id=booking.id
                    )
                    db.session.add(bookingdetails)
                    db.session.commit()

                except SQLAlchemyError as e:
                    db.session.rollback()
                    print(f"Error occurred: {e}")
            
        except Exception as e:
            print('something error',e)

        return jsonify({'message':'cancelled successful'})
    
    @app.route('/getpending', methods = ["POST"])
    def getpending():
        try:
            data = request.get_json()
            driver = Driver.query.filter_by(email = data['email']).first()
            booking = Booking.query.filter_by(driver_id = driver.id, status = 'pending').first()
            return jsonify({'id':booking.id})
        except:
            return jsonify({'message':'error'})
    
    @app.route('/getpending2', methods = ["POST"])
    def getpending2():
        try:
            data = request.get_json()
            driver = Driver.query.filter_by(email = data['email']).first()
            booking = Booking.query.filter_by(driver_id = driver.id, status = 'pending').first()
            data = {'user_id':booking.user_id, 'driver_id':booking.driver_id, 'vehicle_type':booking.vehicle_type, 'from_location':booking.from_location,'destination':booking.to_location, 'total_km':booking.total_km, 'fare':booking.fare}
            return jsonify({'message': data})
        except:
            return jsonify({'message': 'booking not found'})
        
    @app.route('/checknodriver',methods = ["POST"])
    def checknodriver():
        try:
            data = request.get_json()
            ten_minutes_ago = datetime.utcnow() - timedelta(minutes=1)
            old_bookings = Booking.query.filter(
                Booking.created_at >= ten_minutes_ago,
                Booking.user_id == data['userid'],
                Booking.status == 'driver not available',
            ).all()
            if old_bookings:
                return jsonify({'message':'request is not accepted'})
            return jsonify({'message':'searching'})
        except:
            return jsonify({'message':'error'})

    @app.route('/checknotificationpending', methods = ["POST"])
    def checknotificationpending():
        try:
            data = request.get_json()
            driver = Driver.query.filter_by(email = data['email']).first()
            booking = Booking.query.filter_by(driver_id=driver.id).filter(or_(Booking.status == 'pending', Booking.status == 'accepted by driver')).all()
            if booking:
                return jsonify({'message':'pending'})
        except:
            pass
        return jsonify({'message':'ok'})

    @app.route('/acceptbydriver',methods = ['POST'])
    def acceptbydriver():
        try:
            data = request.get_json()
            booking = Booking.query.filter_by(user_id = data['user_id'],driver_id = data['driver_id'], status = 'pending').first()
            booking.status = 'accepted by driver'
            db.session.commit()
            return jsonify({'message':'accepted'})
        except:
            print('ok')
            return jsonify({'message':'something error'})

    @app.route('/ridefinish',methods = ["POST"])
    def ridefinish():
        try:
            data = request.get_json()
            driver = Driver.query.filter_by(email = data['email']).first()
            booking = Booking.query.filter(Booking.driver_id == driver.driver_id, Booking.status == 'accepted by driver').first()
            booking.status = 'ride finished'
            driver.status = 'active'
            db.session.commit()
            return jsonify({'message':'success'})
        except:
            return jsonify({'message':'error'})
    
    @app.route('/cancelledbydriver', methods = ["POST"])
    def cancelledbydriver():
        try:
            data = request.get_json()
            driver = Driver.query.filter_by(email = data['email']).first()
            print(driver.driver_id)
            booking = Booking.query.filter(Booking.driver_id == driver.driver_id, Booking.status == 'accepted by driver').first()
            print(booking)
            cancelledride = CancelledRide(reason = data['reason'], booking_id = booking.id, driver_id = driver.driver_id)
            driver.status = 'active'
            booking.status = 'cancelled by driver after accepting'
            db.session.add(cancelledride)
            db.session.commit()
            return jsonify({'message':'ok','driverid':driver.id})
        except:
            return jsonify({'message':'error'})

    @app.route('/cancelfromuser', methods = ["POST"])
    def cancelfromuser():
        try:
            data = request.get_json()
            user = User.query.filter_by(email = data['email']).first()
            booking = Booking.query.filter(Booking.user_id == user.user_id, Booking.status == 'accepted by driver').first()
            cancelledride = CancelledRide(reason = data['reason'], booking_id = booking.id, driver_id = booking.driver_id)
            driver = Driver.query.filter_by(driver_id = booking.driver_id).first()
            driver.status = 'active'
            booking.status = 'cancelled by user after accepting'
            db.session.add(cancelledride)
            db.session.commit()
            return jsonify({'message':'ok','driverid':driver.driver_id})
        except:
            return jsonify({'message':'error'})
    
    @app.route('/bookingcount', methods = ["GET"])
    def bookingcount():
        try:
            finished = Booking.query.filter_by(status = 'ride finished').all()
            cancelled = Booking.query.filter(
                    or_(Booking.status == 'cancelled by user', Booking.status == 'cancelled by driver')
                ).all()
            print(len(cancelled),len(finished))
            return jsonify({'cancelled':len(cancelled),'accepted':len(finished)})
        except:
            return jsonify({'message':'error'})
        
    @app.route('/vehicles', methods = ["GET"])
    def vehicles():
        try:
            vehicles = Driver.query.all()
            inactive = Driver.query.filter_by(status = 'active').all()
            return jsonify({'total':len(vehicles), 'inactive':len(inactive)})
        except:
            return jsonify({'message':'error'})

    return app

if __name__ == '__main__':
    eventlet.monkey_patch()
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=9638)
