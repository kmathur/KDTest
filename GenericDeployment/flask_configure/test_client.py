import requests
import json
import time
import sys

url = "http://10.35.249.2:10001/train"
#code = "print(1)"
filename = "code"
# Open the file as f.
# The function readlines() reads the file.
with open(filename) as f:
	code = f.read()
print(type(code))
payload = {
	"training_code" : code
}
headers = {
    'Content-Type': "application/json"
    }

json_response = requests.request("POST", url, data=json.dumps(payload), headers=headers).json()
print(json_response)
his_url = json_response['request_url']
print(his_url)
history_response = requests.request("GET", his_url).json()[0]
status = history_response['status']
last = ''
while status == 'Running':
	time.sleep(3)
	log_url = history_response['log_url']
	logs_json = requests.request("GET", log_url).json()
	print(logs_json)
	history_response = requests.request("GET", his_url).json()[0]
	#print(history_response)
	status = history_response['status']


#print(history_response['log_url'])
