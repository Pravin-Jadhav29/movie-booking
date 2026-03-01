from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Movie, Show, Theatre
from bookings.models import Booking
import random
from .models import Theatre
import json

# 🏠 Home Page
def home(request):
    movies = Movie.objects.all()
    return render(request, 'home.html', {'movies': movies})


# 🎬 Movie Detail Page
def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    shows = Show.objects.filter(movie=movie)

    return render(request, 'movie_detail.html', {
        'movie': movie,
        'shows': shows
    })


# 🎟 Seat Selection
@login_required
def select_seat(request, show_id):
    show = get_object_or_404(Show, id=show_id)

    rows = ['A','B','C','D','E','F','G','H']
    numbers = range(1, 15)

    seats = [f"{row}{num}" for row in rows for num in numbers]

    booked_seats = Booking.objects.filter(show=show)\
                    .values_list('seat_number', flat=True)

    if request.method == "POST":
        selected_seats = request.POST.getlist('seats')

        if not selected_seats:
            return redirect('select_seat', show_id=show.id)

        seat_price = 150
        total_price = len(selected_seats) * seat_price

        # Store in session
        request.session['selected_seats'] = selected_seats
        request.session['show_id'] = show.id
        request.session['total_price'] = total_price

        return redirect('payment')

    return render(request, 'select_seat.html', {
        'show': show,
        'seats': seats,
        'booked_seats': booked_seats
    })


# 💳 Payment Page
@login_required
def payment_page(request):
    selected_seats = request.session.get('selected_seats')
    show_id = request.session.get('show_id')
    total_price = request.session.get('total_price')

    if not show_id or not selected_seats:
        return redirect('home')

    show = get_object_or_404(Show, id=show_id)

    if request.method == "POST":

        for seat in selected_seats:
            Booking.objects.create(
                user=request.user,
                show=show,
                seat_number=seat,
                price=150
            )

        # Clear session after saving
        request.session.pop('selected_seats', None)
        request.session.pop('show_id', None)
        request.session.pop('total_price', None)

        return redirect('ticket')

    return render(request, 'payment.html', {
        'show': show,
        'selected_seats': selected_seats,
        'total_price': total_price
    })


# 🎟 Ticket Page (Database Based - Industry Style)
@login_required
def ticket_page(request):

    booking = Booking.objects.filter(
        user=request.user
    ).order_by('-id').first()

    if not booking:
        return redirect('home')

    return render(request, 'ticket.html', {
        'booking': booking
    })

# ❌ Cancel Booking
@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(
        Booking,
        id=booking_id,
        user=request.user
    )
    booking.delete()
    return redirect('my_bookings')


# 📄 My Bookings Page
@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(
        user=request.user
    ).order_by('-booked_at')

    return render(request, 'my_bookings.html', {
        'bookings': bookings
    })


# 📊 Multi-Theatre Admin Dashboard
@login_required
def admin_dashboard(request):

    # SUPER ADMIN
    if request.user.is_superuser:
        bookings = Booking.objects.all()
    else:
        theatre = Theatre.objects.filter(admin=request.user).first()
        if not theatre:
            return redirect('home')
        bookings = Booking.objects.filter(show__theatre=theatre)

    total_bookings = bookings.count()
    total_revenue = bookings.aggregate(
        total=Sum('price')
    )['total'] or 0

    revenue_by_movie = bookings.values(
        'show__movie__title'
    ).annotate(
        total=Sum('price')
    )

    # Prepare data for chart
    movie_labels = [item['show__movie__title'] for item in revenue_by_movie]
    movie_totals = [float(item['total']) for item in revenue_by_movie]

    context = {
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'movie_labels': json.dumps(movie_labels),
        'movie_totals': json.dumps(movie_totals),
    }

    return render(request, 'admin_dashboard.html', context)