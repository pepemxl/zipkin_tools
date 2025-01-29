# Usar Ubuntu 24.04 como imagen base
FROM ubuntu:24.04

# Instalar Python y pip
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
RUN pip3 install requests

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar el script y el archivo de configuración
COPY ./app/script.py /app/script.py
COPY ./app/settings.conf /app/settings.conf

# Ejecutar el script
CMD ["python3", "script.py"]