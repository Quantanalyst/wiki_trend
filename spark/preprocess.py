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
from pyspark.sql import SparkSession, Row, SQLContext
import os 

# path = "s3a://insight-wiki-clickstream/2016_04_en_clickstream.tsv"
# path = "./data/2016_shorted.tsv"
path = "./data/Actual/clickstream-enwiki-2018-11.tsv"

def loadFiles(bucket_name, sc):
    """
    Load files in a aws bucket with name, bucket_name.
    """
    return sc.textFile(bucket_name)

def cleanData(raw, spark):
    """
    Clean Wikipedia Clickstream Data
    """

    # Skip the Header
    header = raw.first()
    raw = raw.filter(lambda x: x != header)
    
    # Seperate the values by tabs
    #neo4j-admin doesn't support: quotes next to each other and escape quotes with '\""'
    parts = raw.map(lambda x: x.replace("\r","").replace("\"", "").replace("\\", "").replace('"','').replace(',',''))
    parts = parts.map(lambda x: x.split('\t'))
        
    # filter empty rows
    parts = parts.filter(lambda x: len(x) == 4)
    parts = parts.filter(lambda x: (x[0]!='' and x[1]!='' 
                                    and x[2]!='' and x[3]!=''))
    parts = parts.filter(lambda x: (x[0] not in ['other-search', 'other-internal', 'other-empty', 'other-external']) and
                                   (x[2] not in ['external']) and 
                                    (int(x[3]) > 0))
    
    # Define Schema
    links = parts.map(lambda p: Row(FROM=p[0],
                                    TO=p[1],
                                    TYPE=p[2],
                                    OCCURENCE=int(p[3]))) 

    # Convert to dataframe
    wikiDF = spark.createDataFrame(links)
    return wikiDF

def exportAsCSV(data_frame):
    data_frame.write.format("csv").save("s3a://modified-clickstream-data/Output")
    print('SUCCESS')
    return 

if __name__ == '__main__':
    # Begin Spark Session
    spark = SparkSession.builder.appName("wiki-trend")\
            .config("spark.hadoop.fs.s3a.fast.upload","true")\
            .getOrCreate()

    # Begin Spark Context
    sc = SparkContext.getOrCreate()

    sql_context = SQLContext(sc)

    # Pre-process Data
    raw = loadFiles(path, sc)
    wikiDF = cleanData(raw, spark)

    print(wikiDF.head(5))

    # exportAsCSV(wikiDF)
