from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('api/', include(("APPS.bms.urls", "APPS.bms"), namespace="APPS.bms")),
]
