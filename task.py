from flask import Flask
from celery import Celery
from flask_mail import  Mail, Message
from src import mail, app

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

app = Flask(__name__)
app.config.update(
    CELERY_BROKER_URL='amqp://guest:guest@localhost:5672//',
    CELERY_RESULT_BACKEND='rpc://',

)

celery = make_celery(app)


@celery.task
def send_order_email(order_id, customer_email):
    with app.app_context():
        msg = Message("Order Confirmation",
                      sender="noreply@yourcompany.com",
                      recipients=[customer_email])
        msg.body = f"Thank you for your order! Your order ID is {order_id}."
        mail.send(msg)




@celery.task
def send_payment_email(order_id, customer_email):
    with app.app_context():
        msg = Message('Payment Confirmation', sender="noreply@softlife.com", recipients=[customer_email])
        msg.body = f"We've received your payment for order {order_id}. Thank you!"
        mail.send(msg)




@celery.task
def send_signup_email(otp_code, email):
    with app.app_context():
        msg = Message('Email Confirmation', sender="noreply@softlife.com", recipients=[email])
        msg.body = f"Verify your email by clicking on this link ! {otp_code}"
        mail.send(msg)



def send_email(subject, sender, recipient, message):
    msg = Message(subject=subject, sender=sender, recipients=[recipient])
    msg.body = message
    mail.send(msg)
    return "Message sent!"




from  mailings import  send_order_email, send_payment_email, send_signup_email
import mailings
