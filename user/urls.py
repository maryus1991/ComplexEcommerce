from django.urls import path
from .views import (
    LogoutView,
    OTP,
    LoginView,
    RegisterView,
    ActiveAccount,
    ForgotPassword,
    EditUserInformation,
    ChangeNumber,
    ChangePassword
)


app_name = 'user'

urlpatterns = [
    path('logout/', LogoutView.as_view(), name='logout'),
    path('otp/', OTP.as_view(), name='otp'),
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('reset-password/', ForgotPassword.as_view(), name='reset_password'),
    path('active-account/', ActiveAccount.as_view(), name='active_account'),

    # user setting in dashboard
    path('change-number/', ChangeNumber.as_view(), name='change-number'),
    path('change-password/', ChangePassword.as_view(), name='change-password'),
    path('edit-information/', EditUserInformation.as_view(), name='edit-information'),

]