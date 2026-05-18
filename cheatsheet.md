kubectl create namespace spark-staging
kubectl create namespace spark-jobs

cd argo-workflows
kubectl apply -f workflow-sa.yaml
cd ..

cd spark-app/jars
curl -fL https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.4.1/hadoop-aws-3.4.1.jar -o hadoop-aws-3.4.1.jar
curl -fL https://repo1.maven.org/maven2/software/amazon/awssdk/bundle/2.33.0/bundle-2.33.0.jar -o bundle-2.33.0.jar
curl -fL https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.13/4.0.0/spark-sql-kafka-0-10_2.13-4.0.0.jar -o spark-sql-kafka-0-10_2.13-4.0.0.jar
cd ..

docker build -t spark-app:0.1 .
kind load docker-image spark-app:0.1 --name local-dev
cd ..

helm dependency build .
helm install spark-release . \
  -n spark-staging \
  -f ./argo-workflows/values.yaml \
  -f ./spark-operator/values.yaml \
  -f ./minio/values.yaml \
  -f ./spark/values.yaml

kubectl port-forward svc/spark-release-argo-workflows-server   -n spark-staging   2746:2746   --address 0.0.0.0
kubectl port-forward svc/spark-history-server-master-svc   -n spark-staging   18080:18080   --address 0.0.0.0

kubectl apply -f spark-app.yaml

helm uninstall spark-release -n spark-staging