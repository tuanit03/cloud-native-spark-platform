# 🚀 Spark Data Platform on Kubernetes (Local Dev)

This project provides a comprehensive solution for deploying a data processing platform using Apache Spark on Kubernetes. The system utilizes **Argo Workflows** for orchestration, **Kubeflow Spark Operator** to manage the Spark application lifecycle, **MinIO** as an S3-compatible storage system (for logs and checkpoints), and **Spark History Server** to monitor and track jobs.

All infrastructure components are packaged using **Helm** and deployed on a local cluster via **KinD**.

---

## 🏗️ System Architecture

* **Kubernetes Cluster**: KinD (Kubernetes in Docker) v0.32.0 (1 Control Plane Node: `local-dev`).
* **Namespace Design**:
* `spark-staging`: Hosts all infrastructure components (Argo, Spark Operator, MinIO, History Server).
* `spark-jobs`: Hosts the Workloads (CronWorkflow, SparkApplications).


* **Core Components**:
* `Argo Workflows`: Orchestrates and schedules workflows (CronWorkflow).
* `Spark Operator`: Monitors `SparkApplication` resources and automatically provisions Spark Driver/Executor Pods.
* `MinIO`: Acts as S3 Object Storage for storing Spark Event Logs (`s3a://spark-bucket/logs`) and Streaming Checkpoints.
* `Spark History Server`: Reads logs from MinIO to render the reporting UI.
* `Custom Spark Image`: Contains Python processing logic (Batch & Streaming) and required `.jar` libraries (Hadoop-AWS, Kafka).



---

## 📂 Directory Structure

```text
.
├── Chart.yaml                  # Project's Umbrella Helm Chart configuration file
├── values.yaml                 # Global default values for Helm
├── argo-workflows/             # Subchart: Configuration and values for Argo Workflows
│   ├── Chart.yaml
│   ├── values.yaml
│   └── workflow-sa.yaml        # ServiceAccount/RBAC for Argo Workflows
├── minio/                      # Subchart: Configuration and values for MinIO S3
│   ├── Chart.yaml
│   └── values.yaml             # Automatically creates 'spark-bucket' upon initialization
├── spark/                      # Subchart: Spark History Server configuration
│   ├── Chart.yaml
│   └── values.yaml
├── spark-operator/             # Subchart: Kubeflow Spark Operator configuration
│   ├── Chart.yaml
│   └── values.yaml
├── spark-app/                  # Source code and Docker configuration directory for Spark Jobs
│   ├── Dockerfile              # Custom Dockerfile built from bitnami/spark
│   ├── jars/                   # Contains libraries (Hadoop S3A, AWS SDK, Kafka)
│   ├── main.py                 # Spark Batch source code (e.g., Pi Calculation)
│   ├── test.py                 # Spark Streaming source code
│   └── pyproject.toml          # Python dependencies management using 'uv'
├── spark-app.yaml              # Manifest defining the Argo CronWorkflow
└── cheatsheet.md               # Deployment helper commands

```

---

## 🛠️ Prerequisites

To run this project locally, ensure you have the following tools installed:

* **Docker Engine**
* **KinD** (`v0.32.0`)
* **kubectl** (`v1.35.0`)
* **Helm** (v3.x)

---

## 🚀 Quick Start

Follow the steps below to set up the environment and run the application.

### Step 1: Prepare Namespaces & RBAC

Initialize Kubernetes namespaces and configure Role-Based Access Control (RBAC) for Argo Workflows.

```bash
# Create namespaces
kubectl create namespace spark-staging
kubectl create namespace spark-jobs

# Apply RBAC for Argo Workflows
cd argo-workflows
kubectl apply -f workflow-sa.yaml
cd ..

```

### Step 2: Build & Load Custom Spark Image into KinD

Build the Docker image containing the application source code and load it into the KinD cluster's `local-dev` node so Pods can pull the image directly.

```bash
cd spark-app/jars
curl -fL https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.4.1/hadoop-aws-3.4.1.jar -o hadoop-aws-3.4.1.jar
curl -fL https://repo1.maven.org/maven2/software/amazon/awssdk/bundle/2.33.0/bundle-2.33.0.jar -o bundle-2.33.0.jar
curl -fL https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.13/4.0.0/spark-sql-kafka-0-10_2.13-4.0.0.jar -o spark-sql-kafka-0-10_2.13-4.0.0.jar
cd ..

docker build -t spark-app:0.1 .
kind load docker-image spark-app:0.1 --name local-dev
cd ..

```

### Step 3: Deploy Infrastructure using Helm

Use Helm to simultaneously deploy Argo Workflows, Spark Operator, MinIO, and Spark History Server into the `spark-staging` namespace.

```bash
# Download/Update Helm dependencies
helm dependency build .

# Install the entire stack (Umbrella Chart)
helm install spark-release . \
  -n spark-staging \
  -f ./argo-workflows/values.yaml \
  -f ./spark-operator/values.yaml \
  -f ./minio/values.yaml \
  -f ./spark/values.yaml

```

### Step 4: Run Workloads (CronJob)

Use the Argo Workflows configuration to create a daily Job scheduled at `02:00 AM`. This workflow will sequentially/concurrently trigger 2 SparkApplications (1 Batch and 1 Streaming).

```bash
kubectl apply -f spark-app.yaml

```

*(You can also trigger this workflow manually from the Argo UI).*

---

## 📊 UI Access

Once the system is successfully initialized (it typically takes a few minutes for Pods to reach the `Running` state), you can use `port-forward` to access the web interfaces:

**1. Argo Workflows UI (Pipeline Management)**

```bash
kubectl port-forward svc/spark-release-argo-workflows-server -n spark-staging 2746:2746 --address 0.0.0.0

```

👉 Access: [https://localhost:2746](https://www.google.com/search?q=https://localhost:2746)

**2. Spark History Server (Spark Jobs Reporting)**

```bash
kubectl port-forward svc/spark-history-server-master-svc -n spark-staging 18080:18080 --address 0.0.0.0

```

👉 Access: [http://localhost:18080](https://www.google.com/search?q=http://localhost:18080)

---

## 🧹 Clean Up

To uninstall the entire infrastructure and release Kubernetes resources, run the following commands:

```bash
# Uninstall Helm release
helm uninstall spark-release -n spark-staging

# (Optional) Delete namespaces
kubectl delete namespace spark-jobs
kubectl delete namespace spark-staging

```

---

## 📚 Resources & References

This project leverages the following official Helm charts and repositories for its core infrastructure setup. For advanced configuration options and parameter references, please consult the links below:

* **Argo Workflows Helm Chart (v1.0.13)**: [Artifact Hub - Argo Workflows Values](https://artifacthub.io/packages/helm/argo/argo-workflows/1.0.13?modal=values) — Reference for workflow controller and server configurations.
* **Kubeflow Spark Operator Chart (v2.5.0)**: [GitHub - Kubeflow Spark Operator Chart](https://github.com/kubeflow/spark-operator/tree/v2.5.0/charts/spark-operator-chart) — Source repository for the Kubernetes custom resource definitions (CRDs) and controller.
* **Bitnami Spark Helm Chart (v10.0.3)**: [Artifact Hub - Bitnami Spark Values](https://artifacthub.io/packages/helm/bitnami/spark/10.0.3?modal=values) — Reference deployment for the Spark History Server configuration.
* **Bitnami MinIO Helm Chart (v17.0.21)**: [Artifact Hub - Bitnami MinIO Values](https://artifacthub.io/packages/helm/bitnami/minio/17.0.21?modal=values) — Reference configuration for the S3-compatible standalone storage instance.