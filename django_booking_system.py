import django
from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.conf import settings
import stripe

# Initialize Stripe API
stripe.api_key = settings.STRIPE_SECRET_KEY

# Models
class Vehicle(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='vehicles/')
    price_per_km = models.DecimalField(max_digits=10, decimal_places=2)
    seats = models.IntegerField()
    
    def __str__(self):
        return self.name

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    pickup_location = models.CharField(max_length=255)
    dropoff_location = models.CharField(max_length=255)
    pickup_date = models.DateField()
    pickup_time = models.TimeField()
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Booking {self.id} - {self.user}"

# Views
from django.views import View
from django.views.decorators.csrf import csrf_exempt

def home(request):
    return render(request, 'home.html', {'vehicles': Vehicle.objects.all()})

class BookingView(View):
    def get(self, request):
        vehicles = Vehicle.objects.all()
        return render(request, 'booking.html', {
            'vehicles': vehicles, 
            'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY
        })
    
    def post(self, request):
        data = request.POST
        vehicle = Vehicle.objects.get(id=data['vehicle_id'])
        total_price = vehicle.price_per_km * 10  # Example calculation
        booking = Booking.objects.create(
            user=request.user if request.user.is_authenticated else None,
            pickup_location=data['pickup_location'],
            dropoff_location=data['dropoff_location'],
            pickup_date=data['pickup_date'],
            pickup_time=data['pickup_time'],
            vehicle=vehicle,
            total_price=total_price
        )
        return redirect('payment', booking.id)

# Payment Processing
class PaymentView(View):
    def get(self, request, booking_id):
        booking = Booking.objects.get(id=booking_id)
        return render(request, 'payment.html', {'booking': booking, 'stripe_public_key': settings.STRIPE_PUBLIC_KEY})
    
@csrf_exempt
def create_checkout_session(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'eur',
                'product_data': {
                    'name': booking.vehicle.name,
                },
                'unit_amount': int(booking.total_price * 100),
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=settings.DOMAIN + '/success/',
        cancel_url=settings.DOMAIN + '/cancel/',
    )
    return JsonResponse({'id': checkout_session.id})

# URL Routing
from django.urls import path

urlpatterns = [
    path('', home, name='home'),
    path('booking/', BookingView.as_view(), name='booking'),
    path('payment/<int:booking_id>/', PaymentView.as_view(), name='payment'),
    path('create-checkout-session/<int:booking_id>/', create_checkout_session, name='checkout_session'),
]

# Frontend Enhancements
from django.templatetags.static import static

def booking_page(request):
    return render(request, 'booking.html', {
        'vehicles': Vehicle.objects.all(),
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY
    })

# Frontend Templates
from django.template import loader

def load_templates():
    template_names = ['home.html', 'booking.html', 'payment.html']
    templates = {}
    for name in template_names:
        try:
            templates[name] = loader.get_template(name).template.source
        except:
            templates[name] = ""
    return templates

# Responsive UI Enhancements
from django.utils.safestring import mark_safe

def responsive_ui(request):
    return render(request, 'responsive_ui.html', {
        'styles': mark_safe("<style>            @media (max-width: 768px) { body { font-size: 14px; } }            @media (max-width: 480px) { body { font-size: 12px; } button { width: 100%; } }            .animated-button { transition: all 0.3s ease-in-out; }            .animated-button:hover { transform: scale(1.1); background-color: #ff6600; color: white; }            .fade-in { animation: fadeIn 1s ease-in-out; }            @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }            .slide-up { animation: slideUp 0.5s ease-in-out; }            @keyframes slideUp { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }        </style>")
    })
