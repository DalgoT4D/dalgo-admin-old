from django.urls import path
from django.views.generic import TemplateView
from .views import get_client

urlpatterns= [
    path('', TemplateView.as_view(template_name='dashboard/home.html'), name='home'),
    path('client-details/', get_client, name='client_details'),
]