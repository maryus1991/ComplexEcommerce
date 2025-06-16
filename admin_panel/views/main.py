from django.views.generic import TemplateView

from user.mixins.logins import AdminUserMixin

class HomePageView(AdminUserMixin, TemplateView):
    template_name = 'admin_panel/index2.html'