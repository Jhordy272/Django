from django.urls import path
from . import views

urlpatterns = [
    path('',                          views.home,          name='home'),
    path('login/',                    views.login_view,    name='login'),
    path('logout/',                   views.logout_view,   name='logout'),
    path('planning/',                 views.planning,      name='planning'),
    path('users/',                    views.users,         name='users'),
    path('users/<int:pk>/edit/',      views.user_edit,     name='user_edit'),
    path('users/<int:pk>/delete/',    views.user_delete,   name='user_delete'),
    path('clients/',                  views.clients,       name='clients'),
    path('tax-returns/',              views.tax_returns,   name='tax_returns'),
    path('my-returns/',               views.my_returns,    name='my_returns'),
    path('configuration/',            views.configuration, name='configuration'),
]
