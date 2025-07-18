from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create UserProfile when User is created, but only if it doesn't exist"""
    if created:
        # Only create if UserProfile doesn't already exist
        if not hasattr(instance, 'userprofile'):
            try:
                UserProfile.objects.get(user=instance)
            except UserProfile.DoesNotExist:
                UserProfile.objects.create(user=instance, role='sales_staff')


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save UserProfile when User is saved"""
    try:
        if hasattr(instance, 'userprofile'):
            instance.userprofile.save()
    except UserProfile.DoesNotExist:
        # If UserProfile doesn't exist, create it
        UserProfile.objects.create(user=instance, role='sales_staff')
