import eventlet
eventlet.monkey_patch()
import pika
import json
from models import db, User, Driver
from app import create_app


app = create_app()
app.app_context().push()


rabbitmq_host = 'host.docker.internal'  
rabbitmq_port = 5672
rabbitmq_user = 'guest'  
rabbitmq_password = 'guest'  
rabbitmq_queue = 'Booking'


def get_rabbitmq_connection():
    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
    parameters = pika.ConnectionParameters(rabbitmq_host,
                                           rabbitmq_port,
                                           '/',
                                           credentials)
    return pika.BlockingConnection(parameters)


def callback(ch, method, properties, body):
    print('receive in Booking')
    data = json.loads(body)
    print(data)
    if data['role'] == 'user':
        user = User(user_id=data['id'], fullname=data['fullname'], email=data['email'], phone=data['phone'])
        db.session.add(user)
        db.session.commit()
    elif data['role'] == 'driver':
        driver = Driver(
            driver_id=data['id'],
            fullname=data['fullname'],
            email=data['email'],
            phone=data['phone'],
            vehicle=data['vehicle_type'],
            base_price=data['base_price'],
            base_distance_KM=data['base_distance_KM'],
            price_per_km=data['price_per_km'],
            make=data['make'],
            model=data['model'],
            license_plate=data['license_plate']
        )
        db.session.add(driver)
        db.session.commit()
    elif data['role'] == 'makeactive':
        print('activating')
        user = Driver.query.filter_by(email=data['email']).first()
        user.status = data['status']
        user.latitude = data['latitude']
        user.longitude = data['longitude']
        db.session.commit()
    elif data['role'] == 'onwork':
        user = Driver.query.filter_by(email=data['email']).first()
        user.status = data['role']
        db.session.commit()
        print('committed')


def start_consumer():
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()

        channel.queue_declare(queue=rabbitmq_queue)

        channel.basic_consume(queue=rabbitmq_queue, on_message_callback=callback, auto_ack=True)

        print('Consumer started. Waiting for messages...')
        channel.start_consuming()

    except Exception as e:
        print(f'Error in consumer: {str(e)}')

if __name__ == '__main__':
    start_consumer()

