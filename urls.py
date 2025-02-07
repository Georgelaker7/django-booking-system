from django.contrib import admin
from django.urls import path
from .views import home, booking, payment

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('booking/', booking, name='booking'),
    path('payment/', payment, name='payment'),
]
