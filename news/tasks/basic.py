from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings


def user_subscribers(category):
    user_emails = []
    for user in category.subscribers.all():
        user_emails.append(user.email)
    return user_emails


def new_post_subscription(instance):
    template = 'account/email/new_post.html'

    for category in instance.postCategory.all():
        email_sub = f'New post in category {category.name}'
        user_emails = user_subscribers(category)

        html = render_to_string(
            template_name=template,
            context={
                'categories': category,
                'post': instance
            }
        )

        msg = EmailMultiAlternatives(
            subject=email_sub,
            body='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=user_emails
        )

        msg.attach_alternative(html, 'text/html')
        msg.send()
