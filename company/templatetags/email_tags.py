import os

from django import template

from company import constants

register = template.Library()


@register.simple_tag
def email_image(image_name):
    return os.path.join(constants.EMAIL_STATIC_FILE_BUCKET, image_name)
