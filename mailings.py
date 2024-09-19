from celery import Celery
from flask_mail import Mail, Message
from dotenv import load_dotenv
from flask_mail import  Mail, Message
from src import mail, app
from src.task import celery

load_dotenv()


@celery.task(name='tasks.send_order_email')
def send_order_email(order_id, customer_email):
    with app.app_context():
        msg = Message("Order Confirmation",
                      sender="noreply@yourcompany.com",
                      recipients=[customer_email])
        msg.body = f"Thank you for your order! Your order ID is {order_id}."
        mail.send(msg)




@celery.task(name='tasks.send_payment_email')
def send_payment_email(order_id, customer_email):
    with app.app_context():
        msg = Message('Payment Confirmation', sender="noreply@softlife.com", recipients=[customer_email])
        msg.body = f"We've received your payment for order {order_id}. Thank you!"
        mail.send(msg)




@celery.task(name='tasks.send_signup_email')
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
