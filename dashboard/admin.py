from django.contrib import admin
from auditlog.registry import auditlog
from .models import UserIP, UserAddress, Ticket, TicketConversation


class SelectRelatedAdmin(admin.ModelAdmin):
    list_select_related = True


admin.site.register(UserIP, SelectRelatedAdmin)
admin.site.register(UserAddress, SelectRelatedAdmin)
admin.site.register(Ticket, SelectRelatedAdmin)
admin.site.register(TicketConversation, SelectRelatedAdmin)


auditlog.register(UserIP)
auditlog.register(UserAddress)
auditlog.register(Ticket)
auditlog.register(TicketConversation)
