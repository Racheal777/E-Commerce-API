import os

from dotenv import load_dotenv
from flask_mail import Mail, Message
from src import mail, app, celery

load_dotenv()

app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = os.getenv('MAIL_PORT')
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False


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


def send_email(subject, sender, recipient, message):
    msg = Message(subject=subject, sender=sender, recipients=[recipient])
    msg.body = message
    mail.send(msg)
    return "Message sent!"
