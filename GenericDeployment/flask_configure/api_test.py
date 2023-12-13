import requests

url = "http://bluedata-11.bdlocal:10001/Model1/2/predict"

payload =  "{   \n\t\"use_scoring\" : true,\n\t\"scoring_args\" : \"1 9\"\n}\t"
headers = {
    'Content-Type': "application/json",
    'Cache-Control': "no-cache",
    }

response = requests.request("POST", url, data=payload, headers=headers)

print(response.text)