from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('movie/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('select-seat/<int:show_id>/', views.select_seat, name='select_seat'),
    path('payment/', views.payment_page, name='payment'),
    path('ticket/', views.ticket_page, name='ticket'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('cancel-booking/<int:booking_id>/',
         views.cancel_booking,
         name='cancel_booking'),
    
]
