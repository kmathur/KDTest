from pyspark.sql.types import *
from pyspark.sql import Row
import pyspark.mllib
import pyspark.mllib.regression
from pyspark.mllib.regression import LabeledPoint
from pyspark.sql.functions import *
from pyspark.mllib.util import MLUtils
from pyspark.mllib.linalg import Vectors
from pyspark.mllib.feature import StandardScaler
from pyspark.mllib.regression import LinearRegressionWithSGD
from __future__ import print_function

# $example on$
from pyspark.ml.classification import LogisticRegression
# $example off$
from pyspark.sql import SparkSession

if __name__ == "__main__":
    spark = SparkSession\
        .builder\
        .appName("LogisticRegressionWithElasticNet")\
        .getOrCreate()
	houses_data = spark.read\
	  .format('org.apache.spark.sql.execution.datasources.csv.CSVFileFormat')\
	  .option('header', 'true')\
	  .option('inferSchema', 'true')\
	  .load("file:///bd-fs-mnt/KartikServing/data/houses_data.csv")
	rdd = spark.sparkContext.textFile('file:///bd-fs-mnt/KartikServing/data/houses_data.csv')
	rdd.take(5)
	rdd = rdd.map(lambda line: line.split(","))
	rdd.take(2)
	header = rdd.first()
	rdd = rdd.filter(lambda line:line != header)
	rdd.take(2)
	df = rdd.map(lambda line: Row(street = line[0], city = line[1], zip=line[2], beds=line[4], baths=line[5], sqft=line[6], price=line[9])).toDF()
	df.show()
	df.toPandas().head()
	df.groupBy("beds").count().show()
	df.describe(['baths', 'beds','price','sqft']).show() 
	df = df.select('price','baths','beds','sqft')
	df = df[df.baths > 0]
	df = df[df.beds > 0]
	df = df[df.sqft > 0]
	df.describe(['baths','beds','price','sqft']).show()
	temp = df.rdd.map(lambda line:LabeledPoint(line[0],[line[1:]]))
	temp.take(5)
	features = df.rdd.map(lambda row: row[1:])
	features.take(5)
	standardizer = StandardScaler()
	model = standardizer.fit(features)
	features_transform = model.transform(features)
	features_transform.take(5)
	lab = df.rdd.map(lambda row: row[0])
	lab.take(5)
	transformedData = lab.zip(features_transform)
	transformedData.take(5)
	transformedData = transformedData.map(lambda row: LabeledPoint(row[0],[row[1]]))
	transformedData.take(5)
	trainingData, testingData = transformedData.randomSplit([.8,.2],seed=1234)
	linearModel = LinearRegressionWithSGD.train(trainingData,1000,.2)
	linearModel.weights
	testingData.take(10)
	linearModel.save(spark, '/tmp/housing.model')
	linearModel.predict([1.49297445326,3.52055958053,1.73535287287])


