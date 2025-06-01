from django.contrib import admin

from .models import (SiteSetting, QuestionAndAnswer, ContactUs, FastLinks)

admin.site.register(SiteSetting)
admin.site.register(QuestionAndAnswer)
admin.site.register(ContactUs)
admin.site.register(FastLinks)
