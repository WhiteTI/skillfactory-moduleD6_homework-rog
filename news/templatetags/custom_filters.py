from django import template
import re

register = template.Library()


@register.filter
def censor_text(value):
    censored_words = ['suka', 'сука']

    for word in censored_words:
        value = re.sub(r'\b%s\b' % word, '' * len(word), value, flags=re.IGNORECASE)

    return value
