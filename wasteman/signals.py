# signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Schedule


@receiver(post_save, sender=Schedule)
def create_collection_status(sender, instance, created, **kwargs):
    if created:
        instance.create_collection_status()
