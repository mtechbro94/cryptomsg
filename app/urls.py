from django.urls import path
from . import views

urlpatterns = [
    # Home & Auth
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Messages
    path('send/', views.send_message, name='send_message'),
    path('inbox/', views.inbox, name='inbox'),
    path('outbox/', views.outbox, name='outbox'),
    path('message/<int:message_id>/', views.view_message, name='view_message'),
    
    # Router Operations
    path('router/accept/<int:message_id>/', views.router_accept_message, name='router_accept'),
    
    # Cloud Authority Operations
    path('ca/certificate/<int:message_id>/', views.ca_create_certificate, name='ca_create_certificate'),
    
    # API Endpoints
    path('api/message/<int:message_id>/status/', views.api_message_status, name='api_message_status'),
    path('api/stats/', views.api_user_stats, name='api_user_stats'),
]
