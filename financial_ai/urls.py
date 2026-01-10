"""
URL configuration for Financial AI project.
"""
from django.contrib import admin
from django.urls import path
from financial_ai import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('query/', views.process_query, name='process_query'),
    path('history/', views.query_history, name='query_history'),
    path('metrics/', views.metrics_dashboard, name='metrics_dashboard'),
    path('metrics/json/', views.metrics_json, name='metrics_json'),
    path('metrics/prometheus/', views.metrics_prometheus, name='metrics_prometheus'),
]

