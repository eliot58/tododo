from django.urls import path
from .views import *

urlpatterns = [
    path('auth/token/login/', signin),
    path('auth/token/logout/', token_destroyed),
    path('signup/', sign_up),
    path('orders/', Orders.as_view()),
    path('uservalidate/', IsUser.as_view()),
    path('phonevalidate/', IsPhone.as_view()),
    path('profile/', Profiles.as_view()),
    path('data/', GetData.as_view()),
    path('order/<int:id>/', Orderget.as_view()),
    path('response/<int:id>/', Respon.as_view()),
    path('work/', WorkList.as_view()),
    path('archive/', ArchiveList.as_view()),
    path('isdiler/', isdiler),
    path('providercard/<int:id>/', GetProvider.as_view()),
    path('isblanked/', isblanked),
    path('send_quantity/', send_quantity),
    path('quatitydel/<int:id>/', QuantityDel.as_view()),
    path('savephonelist/', savephonelist),
    path('provider_check/<int:id>/', provider_check),
    path('balance/', balance)
]