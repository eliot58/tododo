from django.urls import path
from .views import *

urlpatterns = [
    path('signin/', signin),
    path('signup/', signup),
    path('logout/', token_destroyed),
    path('diler-profile/', DilerProfileView.as_view()),
    path('provider-profile/', ProviderProfileView.as_view()),
    path('orders/', OrdersView.as_view()),
    path('order/', OrderView.as_view()),
    path('quantity/', QuantityView.as_view()),
    path('archive/', ArchiveList.as_view()),
    path('work/', WorkList.as_view()),
    path('isdiler/', isdiler),
]