from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from alx_travel_app.listings.views import (
    ListingViewSet,
    BookingViewSet,
    PaymentInitiateView,
    PaymentVerifyView,
)
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.http import HttpResponse

# Create router and register viewsets
router = DefaultRouter()
router.register(r"listings", ListingViewSet)
router.register(r"bookings", BookingViewSet)

# Swagger / Redoc schema view
schema_view = get_schema_view(
    openapi.Info(
        title="Travel App API",
        default_version="v1",
        description="API documentation",
        terms_of_service="",
        contact=openapi.Contact(email="vinnyotieno004@gmail.com"),
        license=openapi.License(name="Open License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

def home(request):
    return HttpResponse("Welcome to the Travel App API.")

urlpatterns = [
    path('', home),
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path(
        "api/payment/initiate/<uuid:booking_id>/",
        PaymentInitiateView.as_view(),
        name="payment-initiate",
    ),
    path(
        "api/payment/verify/",
        PaymentVerifyView.as_view(),
        name="payment-verify",
    ),
    re_path(r"^swagger/$", schema_view.with_ui("swagger", cache_timeout=0)),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]
