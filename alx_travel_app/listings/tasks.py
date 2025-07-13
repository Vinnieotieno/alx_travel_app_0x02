from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_booking_confirmation_email(email, amount):
    send_mail(
        subject="Booking Confirmed!",
        message=f"Your booking payment of {amount} ETB has been confirmed. Thank you!",
        from_email="no-reply@travelapp.com",
        recipient_list=[email],
        fail_silently=False,
    )
