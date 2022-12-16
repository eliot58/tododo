from django.urls import path, re_path as url
from .views import *
from django.contrib.auth import views as auth_views
from .forms import *

urlpatterns = [
    path('', index, name='index'),
    path('login/', login_view, name='login_view'),
    path('register/', signup, name='signup'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset_form.html',email_template_name = 'password_reset_email.html', form_class=ResetPassForm), name = 'password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name = 'password_reset_done'),
    url(r'^password-reset/confirm/(?P<uidb64>[-\w]+)/(?P<token>[-\w]+)/$', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html',form_class=PassSetForm), name ='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name = 'password_reset_complete'),
    path('logout/', logout_view, name='logout_core_view'),
    path('diler/order/<int:id>', diler_order, name='diler_order'),
    path('diler/orders', diler_orders, name='diler_orders'),
    path('diler/profile/save', diler_profile_save, name='dil_save'),
    path('diler/order/save', order_save, name='order_save'),
    path('provider/profile', provider_profile, name='provider_profile'),
    path('provider/work', provider_work, name='provider_work'),
    path('provider/orders', provider_orders, name='provider_orders'),
    path('provider/response/<int:id>', provider_response, name='provider_response'),
    path('provider/balance', provider_balance, name='provider_balance'),
    path('provider/send_quantity', provider_quantity, name='provider_quantity'),
    path('diler/response/<int:id>', diler_response, name='diler_response'),
    path('diler/company/card/<int:id>', company_card, name='company_card'),
    path('diler/order/delete/<int:id>', order_delete, name='order_delete'),
    path('diler/work', diler_work, name='diler_work'),
    path('diler/archive', diler_archive, name='diler_archive'),
    path('provider/check/<int:id>', provider_check, name='provider_check'),
    path('provider/archive', provider_archive, name='provider_archive'),
    path('diler/review', diler_review, name='diler_review'),
    path('diler/check', diler_check),
]