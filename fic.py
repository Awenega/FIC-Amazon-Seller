import requests
import json

def load_credentials():
    try:
        with open('credentials.json', 'r') as f:
            credentials = json.load(f)
            return credentials
    except FileNotFoundError:
        print(f"File 'credentials.json not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON in credentials.json")
        return None

def tmp():
  credentials = load_credentials()
  headers = {'Authorization': f'Bearer {credentials.get("token")}', 
            'accept': 'application/json',
            'content-type': 'application/json'}
  url = 'https://api-v2.fattureincloud.it'
  path = f'/c/{credentials.get("company_id")}/issued_documents'
  body = {
    "data": {
      "name": "",
    }
  }
  request_parameters = json.dumps(body)
  print(url+path, headers)
  response = requests.post(url+path, headers=headers, data=request_parameters).json()