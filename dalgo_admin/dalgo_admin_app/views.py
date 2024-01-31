from django.shortcuts import render
from django.http import HttpResponse
from .models import Client

# Create your views here.

def get_client(request):
     clients = Client.objects.prefetch_related('pipelineconfig','datasource').all()
     return render(request, 'dashboard/client_details.html', {'clients': clients})