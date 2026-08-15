# config/jinja2.py

from django.templatetags.static import static
from django.urls import reverse
from jinja2 import Environment

def environment(**options):
    env = Environment(**options)
    # This makes Django's 'static' and 'url' functions available inside Jinja2 templates
    env.globals.update({
        'static': static,
        'url': reverse,
    })
    return env