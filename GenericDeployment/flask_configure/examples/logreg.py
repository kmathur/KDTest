# # Save Model Using Pickle
# import pandas
# import numpy as np
# from sklearn import model_selection
# from sklearn.linear_model import LogisticRegression
# import pickle
# import os

# url = "https://raw.githubusercontent.com/jbrownlee/Datasets/master/pima-indians-diabetes.data.csv"
# names = ['preg', 'plas', 'pres', 'skin', 'test', 'mass', 'pedi', 'age', 'class']
# dataframe = pandas.read_csv(url, names=names)
# array = dataframe.values
# X = array[:,0:8]
# Y = array[:,8]
# test_size = 0.33
# seed = 7
# Save Model Using Pickle
import pandas
from sklearn import model_selection
from sklearn.linear_model import LogisticRegression
from numpy import genfromtxt
import dill as pickle
import sys, json

# url = "https://raw.githubusercontent.com/jbrownlee/Datasets/master/pima-indians-diabetes.data.csv"
# names = ['preg', 'plas', 'pres', 'skin', 'test', 'mass', 'pedi', 'age', 'class']
# dataframe = pandas.read_csv(url, names=names)
# array = dataframe.values

def predict(model_loc):
	# Xlist = inputjson["X"]
	# Ylist = inputjson["Y"]
	# X = np.asarray(Xlist)
	# Y = np.asarray(Ylist)
	# test_size = 0.98
	# seed = 7
	# X_train, X_test, Y_train, Y_test = model_selection.train_test_split(X, Y, test_size=test_size, random_state=seed)
	# # Fit the model on 33%
	# model = LogisticRegression()
	# model.fit(X_train, Y_train)
	# # save the model to disk
	# #filename = '/Users/kartik/utilities/ai_ml/try_flask/models/finalized_model.save'
	# pickle.dump(model, open(filename, 'wb'))
	# np.savetxt("Xtest.csv", X_test, delimiter=",")
	# np.savetxt("Ytest.csv", Y_test, delimiter=",")
	 
	# load the model from disk
	X_test = genfromtxt('misc_examples/Xtest.csv', delimiter=',')
	Y_test = genfromtxt('misc_examples/Ytest.csv', delimiter=',')
	loaded_model = pickle.load(open(model_loc, 'rb'))
	result = loaded_model.score(X_test, Y_test)
	print(result)
	return json.dumps(result)

def main():
    test_json=sys.argv[1]
    model_loc = sys.argv[2]
    #print(test_json, model_loc)
    #f = open(model_loc,'rb')
    #print("model location is " + str(model_loc))
    predict(model_loc)



if __name__ == "__main__":
   main()  
