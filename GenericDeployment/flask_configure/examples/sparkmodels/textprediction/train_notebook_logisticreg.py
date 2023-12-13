from pyspark.ml import Pipeline
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.feature import HashingTF, Tokenizer
import os

# Prepare training documents from a list of (id, text, label) tuples.
def getProjectRepo():
    repo = os.popen('bdvcli --get cluster.project_repo').read().rstrip()
    if not repo:
        print("unable to find, project repo, some history will be lost")
        return '/tmp/'
    return repo

training = spark.createDataFrame([
    (0, "a b c d e spark", 1.0),
    (1, "b d", 0.0),
    (2, "spark f g h", 1.0),
    (3, "hadoop mapreduce", 0.0)
], ["id", "text", "label"])

# Configure an ML pipeline, which consists of three stages: tokenizer, hashingTF, and lr.
tokenizer = Tokenizer(inputCol="text", outputCol="words")
hashingTF = HashingTF(inputCol=tokenizer.getOutputCol(), outputCol="features")
lr = LogisticRegression(maxIter=10, regParam=0.001)
pipeline = Pipeline(stages=[tokenizer, hashingTF, lr])

# Fit the pipeline to training documents.
model = pipeline.fit(training)
#print(type(model))
model.save(getProjectRepo() + '/' + 'models/spark_models/TextPredction.model')

# Prepare test documents, which are unlabeled (id, text) tuples.
# test = spark.createDataFrame([
#     (4, "spark i j k"),
#     (5, "l m n"),
#     (6, "spark hadoop spark"),
#     (7, "apache hadoop")
# ], ["id", "text"])