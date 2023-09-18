from django.urls import path
from mainBet.views.admin import auth, home, user_views, bet_views, sale_views, payment_views, report_views

handler404 = "mainBet.views.admin.home.handle_not_found"

urlpatterns = [
    path('login', auth.login_view, name='admin/login'),
    path('logout', auth.logout_view, name="admin/logout"),
    path('', home.index, name='admin'),
    path('users', user_views.UsersView.as_view(), name='admin/users'),
    path('user/<int:id>', user_views.UserView.as_view()),
    path('bets', bet_views.BetsView.as_view(), name='admin/bets'),
    path('bet/<int:id>', bet_views.BetView.as_view()),
    path('sales', sale_views.SalesView.as_view(), name='admin/sales'),
    path('payments', payment_views.PaymentsView.as_view(), name='admin/payments'),
    path('reports/users', report_views.ReportUsersView.as_view(), name='admin/reports/users'),
    path('reports/user/<int:id>', report_views.ReportUserView.as_view()),
]