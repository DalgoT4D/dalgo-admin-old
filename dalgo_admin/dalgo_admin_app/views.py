from django.shortcuts import render
from django.http import HttpResponse
from .models import Client

# Create your views here.

def get_clients(request):
     clients = Client.objects.all()
     return render(request, 'dashboard/clients_details.html', {'clients': clients})

def get_client_detail(request,client_id):
     try:
        client = Client.objects.get(id=client_id)
        context = {'client': client}
        return render(request, 'dashboard/client.html', context)
     except Client.DoesNotExist:
        return HttpResponse("Client not found", status=404)