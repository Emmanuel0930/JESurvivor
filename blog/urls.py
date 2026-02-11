from django.urls import path
from blog.views import CrearReservaView

urlpatterns = [
    path('reserva/crear/', CrearReservaView.as_view(), name='crear-reserva'),
]
