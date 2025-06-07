from django.contrib import admin

from .models import (SiteSetting, QuestionAndAnswer, ContactUs, FastLinks, Slider, Banners)

admin.site.register(SiteSetting)
admin.site.register(QuestionAndAnswer)
admin.site.register(ContactUs)
admin.site.register(FastLinks)
admin.site.register(Slider)
admin.site.register(Banners)
