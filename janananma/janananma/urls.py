from django.contrib import admin
from django.urls import path
from django.urls import path, include
from .views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('jana.urls')),  # 👈 this links your app’s URLs
]


