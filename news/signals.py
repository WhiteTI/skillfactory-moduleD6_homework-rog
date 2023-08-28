from django.core.mail import mail_managers
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver

from news.models import PostCategory
from news.tasks import new_post_subscription


@receiver(m2m_changed, sender=PostCategory)
def notify_subscribers_appointment(sender, instance, **kwargs):
    if kwargs['action'] == 'post_add':
        pass
        new_post_subscription(instance)

