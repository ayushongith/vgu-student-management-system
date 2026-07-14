import os
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from .models import User


@receiver(post_delete, sender=User)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes profile photo from filesystem when corresponding User object is deleted.
    """
    if instance.profile_photo:
        try:
            if os.path.isfile(instance.profile_photo.path):
                os.remove(instance.profile_photo.path)
        except Exception:
            pass


@receiver(pre_save, sender=User)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old profile photo from filesystem when corresponding User object is updated with a new photo.
    """
    if not instance.pk:
        return False

    try:
        old_file = User.objects.get(pk=instance.pk).profile_photo
    except User.DoesNotExist:
        return False

    new_file = instance.profile_photo
    if old_file and old_file != new_file:
        try:
            if os.path.isfile(old_file.path):
                os.remove(old_file.path)
        except Exception:
            pass
