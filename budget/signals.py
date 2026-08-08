import logging

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from budget.models import DEFAULT_CATEGORIES, Category

logger = logging.getLogger(__name__)
User = get_user_model()


@receiver(post_save, sender=User, dispatch_uid="budget.create_default_categories")
def create_default_categories(sender, instance, created, **kwargs):
    """
    Signal handler to seed default budget categories for new users.

    Risk: If this handler fails silently (except without logging/propagation),
    users created by signup will lack default categories, breaking the UX.

    Protection: Try/except with logging + graceful degradation.
    """
    if not created:
        return

    try:
        Category.objects.bulk_create(
            [Category(user=instance, name=name) for name in DEFAULT_CATEGORIES]
        )
        logger.info(f"Successfully created default categories for user {instance.id}")
    except Exception as exc:
        logger.exception(
            f"Failed to create default categories for user {instance.id}: {exc}",
            extra={"user_id": instance.id, "exception": type(exc).__name__},
        )
        # Signal handlers must not raise — swallow the exception but log it loudly
        # so operations don't break, but the failure is visible to monitoring.
        # Future: emit a monitoring alert or retry mechanism if needed.
