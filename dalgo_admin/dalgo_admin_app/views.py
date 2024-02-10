import json
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from .models import Client

def get_clients(request):
    clients = Client.objects.all()
    return render(request, "dashboard/clients_details.html", {"clients": clients})


def get_client_detail(request, client_id):
    try:
        client = Client.objects.get(id=client_id)
        context = {"client": client}
        return render(request, "dashboard/client.html", context)
    except Client.DoesNotExist:
        return HttpResponse("Client not found", status=404)


# function to render the file content
def infra_info(request):
    if request.method == "GET":
        # fetchingg data from file
        file_path = settings.BASE_DIR / "data" / "mock.json"  # Input json file path
        data = read_file(file_path)
        return render(request, "./infrastructure/infrastructure.html", {"data": data})
    else:
        data = "error"
        return render(request, "./infrastructure/infrastructure.html", {"data": data})


# function to read the file content
def read_file(file_path):
    with open(file_path, "r") as f:
        data = json.load(f)
        airbyte_version = data["Airbyte"]["version"]
        prefect_version = data["Prefect"]["version"]
        dbt_version = data["dbt"]["version"]
        cpu_usage_percent = data["Machine_metrics"]["CPU_usage_percent"]
        available_ram_gb = data["Machine_metrics"]["available_RAM_GB"]
        available_disk_space_gb = data["Machine_metrics"]["available_disk_space_GB"]
        final_data = [
            airbyte_version,
            prefect_version,
            dbt_version,
            cpu_usage_percent,
            available_ram_gb,
            available_disk_space_gb,
        ]
        return final_data

