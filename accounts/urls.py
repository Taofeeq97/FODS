from django.contrib.auth import views as auth_view
from django.urls import path
from . import views


urlpatterns = [
    path('create_customer_account/', views.CustomerAccountCreateView.as_view(), name='create_customer_account'),
    path('update_profile/',views.CustomerDetailsUpdateView.as_view(), name='update_profile'),
    path('create_deliveryperson_account/', views.CreateDeliveryPersonView.as_view(), name='create_delivery_person'),
    path('logout/', views.MyLogoutView.as_view(), name='logout'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('reset_password/', auth_view.PasswordResetView.as_view(template_name='accounts/password_reset.html'), name='reset_password'),
    path('reset_password_sent/', auth_view.PasswordResetDoneView.as_view(template_name='accounts/password_reset_sent.html'), name='password_reset_done'),
    path('account/reset/<str:uidb64>/<str:token>/', auth_view.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_form.html'), name='password_reset_confirm'),
    path('reset_password_complete/', auth_view.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_done.html'), name='password_reset_complete'),

]