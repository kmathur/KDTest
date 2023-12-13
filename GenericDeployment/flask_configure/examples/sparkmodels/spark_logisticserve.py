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
def findModel():
    ##Hacky bdvcli again
    ##FIX ME
    AttachedModel = os.popen('bdvcli --get attachments.models').read().rstrip().split(',')
    cmd = 'bdvcli --get attachments.models.' + AttachedModel[0] + '.model_location'
    model = os.popen(cmd).read().rstrip()
    if model == 'undefined':
        #setup_logger.warning('scoring script not found')
        print("unable to find model")
        return ''
    return model

if __name__ == "__main__":
    spark = SparkSession\
        .builder\
        .appName("LogisticRegressionTextPrediction")\
        .getOrCreate()
    model = PipelineModel.load(findModel())
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
