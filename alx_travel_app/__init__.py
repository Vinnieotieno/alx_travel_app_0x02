default_app_config = "listings.apps.ListingsConfig"
from .celery import app as celery_app

__all__ = ("celery_app",)
