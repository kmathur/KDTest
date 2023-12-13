import os
import pandas as pd
import dill as pickle
import json
import sys
from flask import Flask, jsonify
from utils import PreProcessing

### input in postman should be like this

# [{"Loan_ID": "LP001022", "Gender": "Male", "Married": "Yes", 
# "Dependents": 1, "Education": "Graduate", "Self_Employed": "No", 
# "ApplicantIncome": 3076, "CoapplicantIncome": 1500, "LoanAmount": 126, "Loan_Amount_Term": 360, "Credit_History": 1, "Property_Area": "Urban"}]

def apicall(test_json, f):
    """API Call
    
    Pandas dataframe (sent as a payload) from API Call
    """
    try:
        #test = pd.read_json(json.dumps(test_json), orient='records', encoding='latin-1')
        test = pd.read_json(test_json, orient='records', encoding='latin-1')
        #test = pd.read_json(test_json, orient='records')
        #To resolve the issue of TypeError: Cannot compare types 'ndarray(dtype=int64)' and 'str'
        test['Dependents'] = [str(x) for x in list(test['Dependents'])]
        loan_ids = test['Loan_ID']
    except Exception as e:
        print(str(e))
        raise e
    if test.empty:
        return(bad_request())
    else:
        #Load the saved model
        #print("Loading the model...")
        loaded_model = None
        try:
             loaded_model = pickle.load(f)
        except Exception as e:
             print(str(e))
        #print("The model has been loaded...doing predictions now...")
        predictions = loaded_model.predict(test)
        #print(predictions)
        """Add the predictions as Series to a new pandas dataframe
                                OR
           Depending on the use-case, the entire test data appended with the new files
        """
        prediction_series = list(pd.Series(predictions))

        final_predictions = pd.DataFrame(list(zip(loan_ids, prediction_series)))
        """We can be as creative in sending the responses.
           But we need to send the response codes as well.
        """
        #responses = jsonify(predictions=final_predictions.to_json(orient="records"))
        responses = final_predictions.to_json(orient='values')
        #responses.status_code = 200
        print(responses)
        return responses
        #responses.status_code = 200
        #return (responses)

def main():
    test_json=sys.argv[1]
    model_loc = sys.argv[2]
    #print(test_json, model_loc)
    f = open(model_loc,'rb')
    apicall(test_json, f)



if __name__ == "__main__":
   main()        

