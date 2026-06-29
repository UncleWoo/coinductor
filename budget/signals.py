from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from budget.models import Category, DEFAULT_CATEGORIES

User = get_user_model()


@receiver(post_save, sender=User)
def create_default_categories(sender, instance, created, **kwargs):
    if not created:
        return

    Category.objects.bulk_create(
        [Category(user=instance, name=name) for name in DEFAULT_CATEGORIES]
    )
