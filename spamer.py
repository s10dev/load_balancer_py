import requests


while 1:
    try:
        requests.get("http://localhost/",timeout=0.01)
    except requests.exceptions.ReadTimeout: 
        pass
