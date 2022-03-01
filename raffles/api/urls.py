from django.urls import path
from .views import RaffleView, RaffleParticipateView, RaffleWinnersView, VerifyRaffleTicketView

urlpatterns = [
    path('', RaffleView.as_view()),
    path('<uuid:id>/', RaffleView.as_view()),
    path('<uuid:id>/participate/', RaffleParticipateView.as_view()),
    path('<uuid:id>/winners/', RaffleWinnersView.as_view()),
    path('<uuid:id>/verify-ticket/', VerifyRaffleTicketView.as_view()),
]
