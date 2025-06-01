from django.contrib import admin

from .models import (UserIP, UserAddress, Ticket, TicketConversation)




admin.site.register(UserIP)
admin.site.register(UserAddress)

admin.site.register(Ticket)
admin.site.register(TicketConversation)
