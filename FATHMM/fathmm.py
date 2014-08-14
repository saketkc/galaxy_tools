import requests
__url__="http://supfam3.cs.bris.ac.uk/FATHMM/cgi-bin/submit.cgi"

__type__="CANCER" ##Hidden field to show which type of variants we are processing
user_input = "P43026 L441P"
user_threshold = 0.75
data = {"batch": user_input,
        "threshold": user_threshold,
        "weighted": __type__}

response = requests.post(__url__, data=data)
print response.url
print response.text
