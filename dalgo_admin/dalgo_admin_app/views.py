import json
from pathlib import Path
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from .models import Client
from datetime import datetime
import os
import glob

root_dir = Path(settings.BASE_DIR).resolve().parent


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
        # fetching data from file
        file_path = settings.BASE_DIR / "data" / "mock.json"  # Input json file path

        log_file_path = fetch_latest_file() or  root_dir / "assets" / "promtail_output.txt"  # log file path

        memory, RAM, cpu_usage = get_live_data(log_file_path)
        
        data = read_file(file_path)
        data["available_disk_space_gb"], data["available_ram_gb"], data["cpu_usage_percent"] = memory, RAM, cpu_usage
        return render(request, "./infrastructure/infrastructure.html", {"data": data})
    else:
        data = "error"
        return render(request, "./infrastructure/infrastructure.html", {"data": data})


def fetch_prometheus_metrics(requests, output_file):
    url = settings.PROMETHEUS_ENDPOINT
    response = requests.get(url)
    if response.status_code == 200:
        with open(output_file, "w") as f:
            f.write(response.text)
        return True
    else:
        return False


def write_monitoring_file():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = root_dir / "downloads" / "promtail_output_{timestamp}.txt"

    if fetch_prometheus_metrics(output_file):
        print(f"Metrics fetched successfully and saved to {output_file}")
    else:
        print("Failed to fetch metrics")


def fetch_latest_file():
    files = glob.glob(str(root_dir / "downloads" / "promtail_output_*.txt"))
    latest_file = max(files,key= os.path.getctime)

    for file in files:
        if file != latest_file:
            os.remove(file)
    return latest_file        

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

        final_data = {
            "airbyte_version": airbyte_version,
            "perfect_version": prefect_version,
            "dbt_version": dbt_version,
            "cpu_usage_percent": cpu_usage_percent,
            "available_ram_gb":available_ram_gb,
            "available_disk_space_gb": available_disk_space_gb
        }

        return final_data


def get_live_data(log_file_path):

    with open(log_file_path, "r") as file:
        lines = file.readlines()

        metrics = []
        Active_bytes, MemTotal_bytes = [], []
        filesystem_avail_bytes, filesystem_size_bytes = [], []

        for line in reversed(lines):

            #  calculation for cpu usages

            if line.startswith("node_cpu_seconds_total"):
                parts = line.split()
                time_value = parts[-1]
                mode = parts[-2].split(',mode="')[-1].split('"')[0]
                cpu = parts[-2].split('cpu="')[-1].split('"')[0]

                if mode != "idle":
                    metrics.append(
                        {"cpu": cpu, "mode": mode, "time": float(time_value)}
                    )

            # calculation of the ram usages
            if line.startswith("node_memory_Active_bytes"):
                Active_bytes.append(line.split()[-1])

            if line.startswith("node_memory_MemTotal_bytes"):
                MemTotal_bytes.append(line.split()[-1])

            # calculation of free disk
            if line.startswith("node_filesystem_avail_bytes"):
                device = line.split()[-2].split("device=")[-1].split(",")[0]
                if "root" in device:
                    filesystem_avail_bytes.append(line.split()[-1])

            if line.startswith("node_filesystem_size_bytes"):
                device = line.split()[-2].split("device=")[-1].split(",")[0]
                if "root" in device:
                    filesystem_size_bytes.append(line.split()[-1])

        cpu_times = {}
        total_time = 0.0

        # Sum the times for each mode and CPU
        for metric in metrics:
            cpu = metric["cpu"]
            mode = metric["mode"]
            time = metric["time"]

            if cpu not in cpu_times:
                cpu_times[cpu] = {}

            if mode not in cpu_times[cpu]:
                cpu_times[cpu][mode] = 0.0

            cpu_times[cpu][mode] += time
            total_time += time

        # Calculate the CPU usage rate
        cpu_usage_rates = {}
        for cpu, modes in cpu_times.items():
            total_cpu_time = sum(modes.values())
            cpu_usage_rates[cpu] = (total_cpu_time / total_time) * 100

        total_cpu_count = len(cpu_usage_rates)
        total_cpu_usage = sum(cpu_usage_rates.values())
        avg_cpu_usage_rate = total_cpu_usage / total_cpu_count

        # further calculation
        disk_Usage = round(float(filesystem_avail_bytes[0]) / (1024 * 1024 * 1024), 2)
        Memory_Usage = round(float(Active_bytes[0]) / (1024 * 1024 * 1024), 2)

        Total_disk_space = round(
            float(filesystem_size_bytes[0]) / (1024 * 1024 * 1024), 2
        )
        Total_Memory = round(float(MemTotal_bytes[0]) / (1024 * 1024 * 1024), 2)

        available_disk_space = round(Total_disk_space - disk_Usage, 2)
        available_RAM = round(Total_Memory - Memory_Usage, 2)

        # Memory ,disk, cpu
        data = [available_disk_space, available_RAM, avg_cpu_usage_rate]
        return data
