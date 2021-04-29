from django.urls import path
import APPS.bms.views as bms_views

urlpatterns = [
    path("usr/register", bms_views.register),
    path("usr/login", bms_views.login),
    path("usr/info", bms_views.u_info),
    path("book", bms_views.bms),
    path("book/checkout", bms_views.book_checkout),
    path("book/appointment", bms_views.book_appointment),
    path("book/return", bms_views.book_return),
    path("book/log", bms_views.borrow_log)

]
