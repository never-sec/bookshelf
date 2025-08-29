from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('create', views.create, name='create'),
    path('tier', views.tier, name='tier'),
    path('random_quote/', views.random_quote, name='random_quote'),
    path('like/<int:quote_id>/', views.like_quote, name='like_quote'),
]