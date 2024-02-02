from django.urls import path
from . import views
from django.views.generic import TemplateView

urlpatterns= [
    path('', TemplateView.as_view(template_name='dashboard/home.html'), name='home'),
    path('infrastructure/', views.infra_info, name='infra_info'),
]