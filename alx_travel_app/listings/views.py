# listings/views.py

import os
import uuid
import requests
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.mail import send_mail
from .models import Listing, Booking, Payment
from .serializers import ListingSerializer, BookingSerializer, PaymentSerializer
from .tasks import send_booking_confirmation_email


CHAPA_SECRET_KEY = os.environ.get("CHAPA_SECRET_KEY")
CHAPA_BASE_URL = "https://api.chapa.co/v1/transaction"
CHAPA_VERIFY_URL = "https://api.chapa.co/v1/transaction/verify/"


class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer


class PaymentInitiateView(APIView):
    def post(self, request, booking_id):
        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return Response({"error": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)

        tx_ref = f"TRAVELAPP-{uuid.uuid4()}"
        amount = str(booking.listing.price)

        data = {
            "amount": amount,
            "currency": "ETB",
            "email": "vincentotienoakuku@gmail.com",  # replace this with user's real email if available
            "tx_ref": tx_ref,
            "callback_url": "http://127.0.0.1:8000/api/payment/verify/",
            "return_url": "http://127.0.0.1:8000/payment-success/"
        }

        headers = {
            "Authorization": f"Bearer {CHAPA_SECRET_KEY}",
            "Content-Type": "application/json"
        }

        chapa_response = requests.post(
            f"{CHAPA_BASE_URL}/initialize",
            json=data,
            headers=headers
        )

        chapa_data = chapa_response.json()

        if chapa_data.get("status") == "success":
            payment = Payment.objects.create(
                booking=booking,
                amount=booking.listing.price,
                transaction_id=tx_ref,
                status='pending'
            )
            return Response({
                "payment_url": chapa_data["data"]["checkout_url"],
                "payment": PaymentSerializer(payment).data
            })
        else:
            return Response({"error": chapa_data.get("message")}, status=status.HTTP_400_BAD_REQUEST)


class PaymentVerifyView(APIView):
    def post(self, request):
        tx_ref = request.data.get("tx_ref")

        headers = {
            "Authorization": f"Bearer {CHAPA_SECRET_KEY}",
            "Content-Type": "application/json"
        }

        verify_url = f"{CHAPA_VERIFY_URL}{tx_ref}"

        chapa_response = requests.get(verify_url, headers=headers)
        chapa_data = chapa_response.json()

        if chapa_data.get("status") == "success":
            payment_data = chapa_data["data"]
            tx_ref = payment_data["tx_ref"]

            try:
                payment = Payment.objects.get(transaction_id=tx_ref)
                payment.status = "completed"
                payment.save()

                send_mail(
                    subject="Booking Payment Completed",
                    message=f"Your payment of {payment.amount} ETB has been confirmed!",
                    from_email="no-reply@travelapp.com",
                    recipient_list=["user@example.com"],
                    fail_silently=True,
                )

                return Response({"message": "Payment completed successfully."})
            except Payment.DoesNotExist:
                return Response({"error": "Payment not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"error": chapa_data.get("message")}, status=status.HTTP_400_BAD_REQUEST)
