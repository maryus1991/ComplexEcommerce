from django.contrib import admin
from auditlog.registry import auditlog

from .models import (
    SiteSetting,
    FastLinks,
    Newsletter,
    QuestionAndAnswer,
    ContactUs,
    Slider,
    Banners,
)

admin.site.register(SiteSetting)
admin.site.register(QuestionAndAnswer)
admin.site.register(ContactUs)
admin.site.register(FastLinks)
admin.site.register(Slider)
admin.site.register(Banners)


auditlog.register(SiteSetting)
auditlog.register(FastLinks)
auditlog.register(Newsletter)
auditlog.register(QuestionAndAnswer)
auditlog.register(ContactUs)
auditlog.register(Slider)
auditlog.register(Banners)
