from datetime import datetime
import os
import glob
import json
from pathlib import Path
import logging
import requests
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from .models import Client

root_dir = Path(settings.BASE_DIR).resolve().parent
logger = logging.getLogger()


def get_clients(request):
    """return list of clients"""
    clients = Client.objects.all()
    return render(request, "dashboard/clients_details.html", {"clients": clients})


def get_client_detail(request, client_id):
    """fetch client details by id and render the client details page."""
    try:
        client = Client.objects.get(id=client_id)
        context = {"client": client}
        return render(request, "dashboard/client.html", context)
    except Client.DoesNotExist:
        return HttpResponse("Client not found", status=404)


# function to render the file content
def infra_info(request):
    """merges the monitoring data with the infrastructure data"""
    if request.method != "GET":
        infra_info_response = "error"
        return render(
            request,
            "./infrastructure/infrastructure.html",
            {"data": infra_info_response},
        )

    # fetching data from file
    file_path = settings.BASE_DIR / "data" / "mock.json"  # Input json file path
    infra_info_response = read_file(file_path)

    log_file_path = (
        fetch_latest_promtail_file() or root_dir / "assets" / "promtail_output.txt"
    )  # log file path

    if log_file_path:
        memory, ram, cpu_usage = get_live_data(log_file_path)
        (
            infra_info_response["available_disk_space_gb"],
            infra_info_response["available_ram_gb"],
            infra_info_response["cpu_usage_percent"],
        ) = (memory, ram, cpu_usage)

    return render(
        request, "./infrastructure/infrastructure.html", {"data": infra_info_response}
    )


def fetch_prometheus_metrics(output_file):
    """fetches the prometheus metrics and writes them to a file."""
    url = settings.PROMETHEUS_ENDPOINT
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    with open(output_file, "w", encoding="utf8") as fout:
        fout.write(response.text)


def write_monitoring_file():
    """fetches the prometheus metrics and writes them to a timestamped file."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = root_dir / "downloads" / f"promtail_output_{timestamp}.txt"

    try:
        fetch_prometheus_metrics(output_file)
        logger.info("Metrics fetched successfully and saved to %s", output_file)
    except Exception as e:  # pylint: disable=broad-except
        logger.warning("Failed to fetch metrics")
        logger.exception(e)


def fetch_latest_promtail_file():
    """returns the most recent promtail output file and deletes the rest."""
    files = glob.glob(str(root_dir / "downloads" / "promtail_output_*.txt"))
    if len(files) > 0:
        latest_file = max(files, key=os.path.getctime)

        for file in files:
            if file != latest_file:
                os.remove(file)
        return latest_file


# function to read the file content
def read_file(file_path):
    """reads the json file and returns the data in the form of dictionary"""
    with open(file_path, "r", encoding="utf8") as f:
        data = json.load(f)
        airbyte_version = data["Airbyte"]["version"]
        prefect_version = data["Prefect"]["version"]
        dbt_version = data["dbt"]["version"]

        return {
            "airbyte_version": airbyte_version,
            "perfect_version": prefect_version,
            "dbt_version": dbt_version,
        }


def get_live_data(log_file_path):
    """reads the promtail response and returns the cpu, memory and disk usage"""

    with open(log_file_path, "r", encoding="utf8") as file:
        lines = file.readlines()

        metrics = []
        active_bytes, mem_total_bytes = [], []
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
                active_bytes.append(line.split()[-1])

            if line.startswith("node_memory_MemTotal_bytes"):
                mem_total_bytes.append(line.split()[-1])

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
        disk_usage = round(float(filesystem_avail_bytes[0]) / (1024 * 1024 * 1024), 2)
        memory_usage = round(float(active_bytes[0]) / (1024 * 1024 * 1024), 2)

        total_disk_space = round(
            float(filesystem_size_bytes[0]) / (1024 * 1024 * 1024), 2
        )
        total_memory = round(float(mem_total_bytes[0]) / (1024 * 1024 * 1024), 2)

        available_disk_space = round(total_disk_space - disk_usage, 2)
        available_ram = round(total_memory - memory_usage, 2)

        # Memory ,disk, cpu
        data = [available_disk_space, available_ram, avg_cpu_usage_rate]
        return data
