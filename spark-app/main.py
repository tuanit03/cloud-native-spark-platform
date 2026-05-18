from pyspark.sql import SparkSession
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

spark = (
    SparkSession.builder
    .appName("SparkAppDemo")
    .getOrCreate()
)

total_sum = spark.range(1, 1001).groupBy().sum().collect()[0][0]
logger.info(f"Total sum from 1 to 1000 is: {total_sum}")

spark.stop()