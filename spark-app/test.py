from pyspark.sql import SparkSession
from pyspark.sql.functions import sum as spark_sum, count, avg, window
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

spark = (
    SparkSession.builder
    .appName("SparkStreamingDemo")
    .getOrCreate()
)

streaming_df = (
    spark.readStream
    .format("rate")              
    .option("rowsPerSecond", 5)  
    .load()
)

aggregated_df = (
    streaming_df
    .withWatermark("timestamp", "10 seconds")
    .groupBy(
        window("timestamp", "10 seconds", "5 seconds")
    )
    .agg(
        spark_sum("value").alias("total_value"),
        count("value").alias("count_value"),
        avg("value").alias("average_value")
    )
)

query = (
    aggregated_df.writeStream
    .outputMode("update")        
    .format("console")
    .option("truncate", False)
    .option("numRows", 10)
    .trigger(processingTime="5 seconds")
    .start()
)

logger.info("Spark Streaming has started — running indefinitely...")
logger.info("   Press Ctrl+C to stop.\n")

try:
    while query.isActive:
        progress = query.lastProgress
        if progress:
            rows_in  = progress.get("numInputRows", 0)
            rows_sec = progress.get("inputRowsPerSecond", 0.0)
            proc_sec = progress.get("processedRowsPerSecond", 0.0)
            logger.info(
                f"[Batch #{progress.get('batchId')}] "
                f"Input: {rows_in} rows | "
                f"Input Rate: {rows_sec:.1f} rows/s | "
                f"Processing Rate: {proc_sec:.1f} rows/s"
            )
        time.sleep(15)

except KeyboardInterrupt:
    logger.info("Received stop signal — shutting down gracefully...")
    query.stop()
    spark.stop()
    logger.info("Shutdown complete.")