#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from __future__ import print_function

# $example on$
from pyspark.ml.classification import LogisticRegressionModel
# $example off$
from pyspark.sql import SparkSession
from pyspark.ml import PipelineModel
import os

def getProjectRepo():
    repo = os.popen('bdvcli --get cluster.project_repo').read().rstrip()
    if not repo:
        print("unable to find, project repo, some history will be lost")
        return 'file:///tmp/'
    return 'file://'+ repo

if __name__ == "__main__":
    spark = SparkSession\
        .builder\
        .appName("LogisticRegressionTextPrediction")\
        .getOrCreate()
    model = PipelineModel.load('/tmp/rf')
    test = spark.createDataFrame([
        (4, "who let the dogs out i j k"),
        (5, "l m n"),
        (6, "spark hadoop spark"),
        (7, "apache hadoop")
    ], ["id", "text"])
    prediction = model.transform(test)
    # Make predictions on test documents and print columns of interest.
    prediction = model.transform(test)
    selected = prediction.select("id", "text", "probability", "prediction")
    for row in selected.collect():
        rid, text, prob, prediction = row
        print("(%d, %s) --> prob=%s, prediction=%f" % (rid, text, str(prob), prediction))
    spark.stop()