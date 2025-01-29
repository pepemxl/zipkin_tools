import json
import os
import re
import requests
import statistics
from configparser import ConfigParser
from collections import defaultdict
from datetime import datetime


# Función para leer la configuración
def read_config():
    config = ConfigParser()
    config.read('settings.conf')
    return config['DEFAULT']

# Función para extraer trace IDs de las URLs
def extract_trace_id(url):
    match = re.search(r"/traces/([a-f0-9]+)", url)
    if match:
        return match.group(1)
    return None

# Función para obtener datos de la API de Zipkin
def fetch_trace_data(base_url, trace_id, save_path):
    api_url = f"{base_url}/api/v2/trace/{trace_id}"
    response = requests.get(api_url)
    if response.status_code == 200:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "w") as file:
            json.dump(response.json(), file, indent=4)
        print(f"Datos del trace ID {trace_id} guardados en {save_path}")
        return response.json()
    else:
        print(f"Error al obtener datos para el trace ID {trace_id}: {response.status_code}")
        return None

# Función para procesar los spans y calcular tiempos
def parse_spans_and_aggregate_time(trace_data):
    span_times = []
    for span in trace_data:
        start_time = int(span['timestamp']) / 1000  # Convertir microsegundos a milisegundos
        duration = int(span['duration']) / 1000  # Convertir microsegundos a milisegundos
        end_time = start_time + duration
        span_times.append((start_time, end_time))
    return span_times

# Función para calcular estadísticas
def compute_stats(span_times):
    durations = [end - start for start, end in span_times]
    if not durations:
        return None
    stats = {
        'total_spans': len(durations),
        'total_time': sum(durations),
        'avg_time': sum(durations) / len(durations),
        'min_time': min(durations),
        'max_time': max(durations),
    }
    return stats

# Función para guardar las estadísticas en un archivo
def save_stats_to_file(stats, output_dir):
    # Crear un nombre de archivo con la fecha y hora actual
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"{output_dir}/stats_{timestamp}.json"
    
    # Guardar las estadísticas en formato JSON
    with open(output_file, "w") as file:
        json.dump(stats, file, indent=4)
    print(f"Estadísticas guardadas en: {output_file}")

# Función principal
def main():
    # Leer la configuración
    config = read_config()
    base_url = config['ZIPKIN_BASE_URL']
    urls_file_path = config['URLS_FILE_PATH']
    output_dir = config.get('OUTPUT_DIR', '/data')  # Directorio de salida (por defecto: /data)
    print(f"Usando URL base de Zipkin: {base_url}")
    print(f"Leyendo URLs desde: {urls_file_path}")
    print(f"Guardando estadísticas en: {output_dir}")

    # Leer URLs desde el archivo
    try:
        with open(urls_file_path, "r") as file:
            urls = file.read().splitlines()
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo de URLs en {urls_file_path}")
        return

    # Procesar cada URL
    all_stats = []
    for url in urls:
        trace_id = extract_trace_id(url)
        if not trace_id:
            print(f"URL inválida, omitiendo: {url}")
            continue

        print(f"Procesando trace ID: {trace_id}")
        trace_data = fetch_trace_data(base_url, trace_id)
        if not trace_data:
            continue

        span_times = parse_spans_and_aggregate_time(trace_data)
        stats = compute_stats(span_times)
        if stats:
            all_stats.append(stats)
            print(f"Estadísticas para trace ID {trace_id}: {stats}")

    # Calcular estadísticas generales
    if all_stats:
        overall_stats = {
            'total_traces': len(all_stats),
            'total_spans': sum(stats['total_spans'] for stats in all_stats),
            'total_time': sum(stats['total_time'] for stats in all_stats),
            'avg_time': sum(stats['total_time'] for stats in all_stats) / sum(stats['total_spans'] for stats in all_stats),
            'min_time': min(stats['min_time'] for stats in all_stats),
            'max_time': max(stats['max_time'] for stats in all_stats),
        }
        print("\nEstadísticas generales:")
        print(json.dumps(overall_stats, indent=4))

        # Guardar las estadísticas en un archivo
        save_stats_to_file(overall_stats, output_dir)

if __name__ == "__main__":
    main()