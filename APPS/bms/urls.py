from django.urls import path
import APPS.bms.views

urlpatterns = [
    path("usr/register", APPS.bms.views.register),
    path("usr/login", APPS.bms.views.login),
    path("usr/info", APPS.bms.views.u_info),

]
