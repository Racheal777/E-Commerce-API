
from celery import Celery
from flask_mail import Message
from flask import current_app


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


celery = Celery(__name__)


@celery.task
def send_order_email(order_id, customer_email):
    with current_app.app_context():
        msg = Message("Order Confirmation",
                      sender="noreply@yourcompany.com",
                      recipients=[customer_email])
        msg.body = f"Thank you for your order! Your order ID is {order_id}."
        current_app.extensions['mail'].send(msg)


@celery.task
def send_payment_email(order_id, customer_email):
    with current_app.app_context():
        msg = Message('Payment Confirmation', sender="noreply@softlife.com", recipients=[customer_email])
        msg.body = f"We've received your payment for order {order_id}. Thank you!"
        current_app.extensions['mail'].send(msg)


@celery.task
def send_signup_email(otp_code, email):
    with current_app.app_context():
        msg = Message('Email Confirmation', sender="noreply@softlife.com", recipients=[email])
        msg.body = f"Verify your email by clicking on this link ! {otp_code}"
        current_app.extensions['mail'].send(msg)


def send_email(subject, sender, recipient, message):
    with current_app.app_context():
        msg = Message(subject=subject, sender=sender, recipients=[recipient])
        msg.body = message
        current_app.extensions['mail'].send(msg)
    return "Message sent!"


def init_celery(app):
    celery.conf.update(app.config)
    celery.conf.broker_connection_retry_on_startup = True

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

