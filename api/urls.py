from django.urls import path
from .views import *

urlpatterns = [
    path('signin/', signin),
    path('signup/', signup),
    path('logout/', token_destroyed),
    path('profile/', ProfileUpdate.as_view()),
    path('diler/profile/', DilerProfile.as_view()),
    path('provider/profile/', ProviderProfile.as_view()),
    path('order/<int:pk>/', OrderView.as_view()),
    path('orders/', OrdersView.as_view()),
    path('quantity/<int:pk>/', QuantityView.as_view()),
    path('archives/', ArchiveList.as_view()),
    path('works/', WorkList.as_view()),
]