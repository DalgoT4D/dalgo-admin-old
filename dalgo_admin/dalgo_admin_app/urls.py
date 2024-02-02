from django.urls import path
from django.views.generic import TemplateView
from .views import get_clients,get_client_detail,infra_info

urlpatterns= [
    path('', TemplateView.as_view(template_name='dashboard/home.html'), name='home'),
    path('clients-details/', get_clients, name='clients_details'),
    path('client/<int:client_id>/', get_client_detail, name='client'),
    path('infrastructure/', infra_info, name='infra_info'),
]