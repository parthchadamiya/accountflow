from django.urls import path
from . import views

urlpatterns = [
    path('trial-balance/', views.TrialBalanceView.as_view(), name='trial_balance'),
    path('party-ledger/', views.PartyLedgerView.as_view(), name='party_ledger'),
]
