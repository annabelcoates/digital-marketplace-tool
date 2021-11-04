import json
import csv
import requests
import time

class Analyzer:
    def __init__(self):
        conf = json.load(open('config.json', 'r'))
        self.url = conf["api_endpoint"]
        # Initialiaze url and Azure cognitive services API key in header
        # To see how to create a Cognitive Services resource in Azure: https://docs.microsoft.com/en-us/azure/cognitive-services/cognitive-services-apis-create-account?tabs=multiservice%2Cwindows
        self.header = {"Ocp-Apim-Subscription-Key" : conf["api_key"]}
        self.result = {"documents" : []}

    def analyze(self, answers):
        body = { 'documents': [] }
        index = 1
        # Iterate through each block of evidence
        for ans in answers:
            # Add each block to request payload until reached 5 blocks or the end of the client
            # API endpoint only allows 5 documents per request, regardless of Azure subscription
            body["documents"].append({
                    "language" : "en",
                    "id" : str(index),
                    "text" : ans
                })
            if len(body["documents"]) % 5 == 0:
                res = requests.post(self.url, data=json.dumps(body), headers=self.header)
                
                for item in json.loads(res.text)["documents"]:   
                    self.result["documents"].append(item)

                body["documents"] = []
        
            index += 1
        # Send any remaining blocks
        if len(body["documents"]) > 0:
            res = requests.post(self.url, data=json.dumps(body), headers=self.header)
            for item in json.loads(res.text)["documents"]:
                self.result["documents"].append(item)

        print('Done.')

