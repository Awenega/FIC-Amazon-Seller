import requests
import json
import time
from math import ceil

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

def get_supplier(credentials, is_ebay, name):
  
    if is_ebay:
        supplier_id = credentials.get("EBAY_SUPPLIER_ID")
    elif 'ES-AOES' in name:
        supplier_id = credentials.get("PPC_ES_SUPPLIER_ID")
    else:
        supplier_id = credentials.get("DEFAULT_SUPPLIER_ID")

    headers = {'Authorization': f'Bearer {credentials.get("token")}', 
                'accept': 'application/json',
                'content-type': 'application/json'}
    url = 'https://api-v2.fattureincloud.it'
    path = f'/c/{credentials.get("company_id")}/entities/suppliers/{supplier_id}'
    response = requests.get(url+path, headers=headers).json()
    response['data']['ei_code'] = credentials.get("CODICE_DESTINATARIO")
    return response['data']

def get_visible_subject(is_ebay, name):
    if is_ebay:
        return 'Commissioni Ebay'
    elif 'ES-AOES' in name:
        return 'Amazon Marketing Commissioni'
    else:
        return 'Commissioni Amazon'

def get_total_amount(credentials, invoice):
    headers = {'Authorization': f'Bearer {credentials.get("token")}', 
                'accept': 'application/json',
                'content-type': 'application/json'}
    url = 'https://api-v2.fattureincloud.it'
    path = f'/c/{credentials.get("company_id")}/issued_documents/totals'

    request_parameters = json.dumps(invoice)
    response = requests.post(url+path, headers=headers, data=request_parameters).json()
    return response['data']['amount_gross']

def create_invoice(credentials, supplier_entity, visible_subject, name, amount, date, item_description):  
    headers = {'Authorization': f'Bearer {credentials.get("token")}', 
                'accept': 'application/json',
                'content-type': 'application/json'}
    url = 'https://api-v2.fattureincloud.it'
    path = f'/c/{credentials.get("company_id")}/issued_documents'
    
    invoice = {
      "data": {
            "type": "self_supplier_invoice",
            "entity": supplier_entity,
            "numeration": "AF",
            "visible_subject": visible_subject,
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
                "name": item_description,
                "net_price": amount,
                "qty": 1,
                "vat": {
                    "id": 0, #22%
                }
            }],
            "payments_list": [
            {
                "amount": ceil(amount * 122) / 100,
                "due_date": date,
                "paid_date": date,
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
                "payment_method": "MP16",
            },
            "ei_raw": {
                "FatturaElettronicaHeader": {
                    "CedentePrestatore": {
                        "DatiAnagrafici": {
                            "RegimeFiscale": "RF18"
                        }
                    },
                },
                "FatturaElettronicaBody": {
                    "DatiGenerali": {
                        "DatiGeneraliDocumento": {
                            "TipoDocumento": "TD17"
                        },
                        "DatiFattureCollegate":{
                            "IdDocumento": name,
                            "Data": date
                        }
                    },
                }
            }
        }
    }

    total_amount = get_total_amount(credentials, invoice)
    invoice['data']['payments_list'][0]['amount'] = total_amount

    time.sleep(0.5)

    request_parameters = json.dumps(invoice)
    response = requests.post(url+path, headers=headers, data=request_parameters).json()
    return response