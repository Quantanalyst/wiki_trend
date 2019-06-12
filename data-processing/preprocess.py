"""
Jason Wong
June 10, 2019
Wiki Trend

This script reads all of the tsv files in an Aamzon S3 Bucket.

The main function

Args:
    item1
    item2

Returns:
    Description of the return

"""

from pyspark import SparkContext
from pyspark.sql import SparkSession, Row

# sc =SparkContext().getOrCreate()
path = "s3a://insight-wiki-clickstream/2016_04_en_clickstream.tsv"
path2 = "./data/2016_04_en_clickstream.tsv"
# raw = sc.textFile(path)
# print(raw.first())


def loadFiles(bucket_name):
    """
    Load files in a aws bucket with name, bucket_name.
    """
    return sc.textFile(bucket_name)

def cleanData(raw):
    """
    Clean Wikipedia Clickstream Data
    """

    # Skip the Header
    header = raw.first()
    raw = raw.filter(lambda x: x != header)
    
    # Seperate the values by tabs
    parts = raw.map(lambda x: x.split('\t'))
    
    # Define Schema
    links = parts.map(lambda p: Row(FROM=p[0],
                                    TO=p[1],
                                    TYPE=p[2],
                                    OCCURENCE=int(p[3]))) 

    # Convert to dataframe
    wikiDF = spark.createDataFrame(links)

    return wikiDF

if __name__ == '__main__':
    # Begin Spark Session
    spark = SparkSession.builder.appName("wiki-trend").getOrCreate()

    # Begin Spark Context
    sc = SparkContext.getOrCreate()

    # Pre-process Data
    raw = loadFiles(path2)
    wikiDF = cleanData(raw)

    print(wikiDF.head(5))
