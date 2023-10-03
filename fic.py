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

def get_supplier(credentials, supplier_id):
  headers = {'Authorization': f'Bearer {credentials.get("token")}', 
            'accept': 'application/json',
            'content-type': 'application/json'}
  url = 'https://api-v2.fattureincloud.it'
  path = f'/c/{credentials.get("company_id")}/entities/suppliers/{credentials.get(supplier_id)}'
  response = requests.get(url+path, headers=headers).json()
  return response

def create_invoice(is_ebay, name, date):
    credentials = load_credentials()
    
    if is_ebay:
        supplier_entity = get_supplier(credentials, "EBAY_SUPPLIER_ID")
    elif 'ITAOIT3' in name:
        supplier_entity = get_supplier(credentials, "PPC_IT_SUPPLIER_ID")
    elif 'ES-AOES' in name:
        supplier_entity = get_supplier(credentials, "PPC_ES_SUPPLIER_ID")
    else:
        supplier_entity = get_supplier(credentials, "DEFAULT_SUPPLIER_ID")

    headers = {'Authorization': f'Bearer {credentials.get("token")}', 
                'accept': 'application/json',
                'content-type': 'application/json'}
    url = 'https://api-v2.fattureincloud.it'
    path = f'/c/{credentials.get("company_id")}/issued_documents'
    
    body = {
      "data": {
            "type": "self_supplier_invoice",
            "entity": supplier_entity['data'],
            "date": date,
            "numeration": "AF",
            "visible_subject": "Commissioni Amazon",
            "currency": {
                "id": "EUR",
                "exchange_rate": "1.00000",
                "symbol": "€"
            },
            "language": {
                "code": "it",
                "name": "Italiano"
            },
            "items_list": [
            {
                "name": "Commissioni del venditore",
                "net_price": 10,
                "qty": 1,
                "vat": {
                    "id": 0, #22%
                }
            }],
            "payments_list": [
            {
                "amount": 12.20,
                "due_date": "2022-09-23",
                "paid_date": "2022-09-23",
                "status": "paid",
                "payment_account": {
                    "id": credentials.get("AMAZON_PAYMENT_ACCOUNT_ID")
                }
            }
            ],
            "template": {
                "id": 108
            },
            "e_invoice": True,
            "ei_data": {
                "payment_method": "MP16"
            },
            "ei_raw": {
                "FatturaElettronicaBody": {
                    "DatiGenerali": {
                        "DatiGeneraliDocumento": {
                            "TipoDocumento": "TD17"
                        }
                    },
                }
            }
        }
    }

    request_parameters = json.dumps(body)
    response = requests.post(url+path, headers=headers, data=request_parameters).json()
    return response

create_invoice(False, "", "2023-10-01")