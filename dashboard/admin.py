from django.contrib import admin
from auditlog.registry import auditlog

from .models import UserIP, UserAddress, Ticket, TicketConversation


admin.site.register(UserIP)
admin.site.register(UserAddress)
admin.site.register(Ticket)
admin.site.register(TicketConversation)


auditlog.register(UserIP)
auditlog.register(UserAddress)
auditlog.register(Ticket)
auditlog.register(TicketConversation)
