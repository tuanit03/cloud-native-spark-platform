FROM bitnamilegacy/spark:4.0.0-debian-12-r20

USER root

RUN echo 'Acquire::http::Proxy "";' > /etc/apt/apt.conf.d/proxy.conf && \
    echo 'Acquire::https::Proxy "";' >> /etc/apt/apt.conf.d/proxy.conf

ENV HTTP_PROXY="" \
    HTTPS_PROXY="" \
    http_proxy="" \
    https_proxy="" \
    NO_PROXY="localhost,127.0.0.1,.cluster.local,.svc.cluster.local,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,minio.spark-staging.svc.cluster.local" \
    no_proxy="localhost,127.0.0.1,.cluster.local,.svc.cluster.local,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,minio.spark-staging.svc.cluster.local"

RUN apt-get update && apt-get install -y curl && \
    pip install --no-cache-dir uv

WORKDIR /app
COPY pyproject.toml ./

RUN uv pip install --system -r pyproject.toml

COPY main.py /app/main.py
COPY test.py /app/test.py

COPY jars/hadoop-aws-3.4.1.jar /opt/bitnami/spark/jars/
COPY jars/bundle-2.33.0.jar /opt/bitnami/spark/jars/
COPY jars/spark-sql-kafka-0-10_2.13-4.0.0.jar /opt/bitnami/spark/jars/

RUN mkdir -p /app/artifacts && chown -R 1001:1001 /app /opt/bitnami/spark

USER 1001
EXPOSE 4040