import os
from PyPDF2 import PdfReader
from datetime import datetime

AMOUNT_CAPTION = ["TOTALES", "Totali", "GESAMT", "Total", "TOTALE", 'Totale fattura corrente in EUR', "TOTAL"]
DATE_CAPTION = ["Fecha de la factura", "Rechnungsdatum", "Data fattura", "Fecha de emisión de la nota de crédito", "Ausstellungsdatum der Gutschrift", "Data emissione nota di credito"]
NAME_CAPTION = ["Número de la factura", "Rechnungsnr", "Numero fattura:", "Número de nota de crédito", "Gutschriftennummer", "Numero nota di credito:"]
ALL_ITEM_DESCRIPTIONS = [
    "Commissioni per la gestione logistica da parte di Amazon",
    "Commissioni al venditore",
    "Commissioni per la gestione logistica da parte di Amazon",
    "Commissioni rimborsate",
    "Comisión por servicios FBA",
    "Gastos de vendedor",
    "Gastos reembolsados",
    "Gebühren im Zusammenhang mit \"Versand durch Amazon\"",
    "Verkaeufergebuehren",
    "Erstattung von Verkaeufergebuehren"
]
PATH_TEST = "fatture"

def check_if_contain_caption(elem, type_caption):
    for caption in type_caption:
        if caption in elem:
            return True
    return False

def get_amount(reader, is_ebay):
        
    page = reader.pages[0] if is_ebay else reader.pages[len(reader.pages)-1]
    text = page.extract_text()
    if len(text) < 150 and not is_ebay:
        page = reader.pages[len(reader.pages)-2]
        text = page.extract_text()
    
    elems = []
    for elem in text.split("\n"):
        if elem.replace(".", "").isnumeric() or check_if_contain_caption(elem, AMOUNT_CAPTION):
            elems.append(elem)
    
    if len(elems) <= 0 and not is_ebay:
        page = reader.pages[len(reader.pages)-2]
        text = page.extract_text()
        for elem in text.split("\n"):
            if elem.replace(".", "").isnumeric() or check_if_contain_caption(elem, AMOUNT_CAPTION):
                elems.append(elem)


    tmp = elems[len(elems)-1].split(" ")
    if is_ebay:
        return float(tmp[1].replace(",", "."))
    
    for elem in tmp:
        if elem.replace(".", "").isnumeric():
            return -float(elem) if "-EUR" in tmp else float(elem)

def get_date(reader, is_ebay):
    page = reader.pages[0]
    text = page.extract_text()
    if is_ebay:
        for elem in text.split("\n"):
            if 'Numero della fattura' in elem:
                data = elem.replace("Numero della fattura","").split(" ")
                mesi = {'gen': '01','feb': '02', 'mar': '03', 'apr': '04', 'mag': '05', 'giu': '06', 'lug': '07', 'ago': '08', 'set': '09', 'ott': '10', 'nov': '11', 'dic': '12'}
                giorno, mese, anno = data[0], mesi[data[1]], data[2]
                return f"{anno}-{mese}-{giorno}"

    for elem in text.split("\n"):
        if check_if_contain_caption(elem, DATE_CAPTION):
            date = datetime.strftime(datetime.strptime(elem.split(": ")[1].strip(), "%d/%m/%Y"), "%Y-%m-%d")
            return date

def get_nome_fattura(reader, is_ebay):
    page = reader.pages[0]
    text = page.extract_text()
    if is_ebay:
        for elem in text.split("\n"):
            if 'FNE' in elem:
                return elem
            
    text_splitted = text.split("\n")
    for elem in text_splitted:
        if check_if_contain_caption(elem, NAME_CAPTION):
            try:
                ret = elem.split(": ")[1].strip()
                if '-CN' in ret:
                    return ret.replace("LU-", "")
                return ret
            except IndexError:
                return text_splitted[text_splitted.index(elem)+1]

def check_if_ppc(name):
    if 'ES-AOES' in name:
        return True
    return False

def check_if_ebay(reader):
    page = reader.pages[0]
    if 'eBay' in page.extract_text():
        return True
    return False

def get_item_description(reader, is_ebay, is_ppc, name):
    if is_ebay:
        return "Tariffe piattaforma"
    elif is_ppc and 'ES' in name:
        return "Comisiónes"
    
    for page in reader.pages:
        text = page.extract_text().replace("\n", " ")
        for item_description in ALL_ITEM_DESCRIPTIONS:
            if item_description in text:
                return item_description

def get_info_invoice(filename):
    reader = PdfReader(filename.path)
    is_ebay = check_if_ebay(reader)
    amount = get_amount(reader, is_ebay)
    date = get_date(reader, is_ebay)
    name = get_nome_fattura(reader, is_ebay)
    is_ppc = check_if_ppc(name)
    item_description = get_item_description(reader, is_ebay, is_ppc, name)
    print(f"{filename.name}: {is_ebay} {name} {date} {amount} {item_description}")
    return is_ebay, amount, date, name, item_description

def test_scrape_pdf():
    for filename in os.scandir(PATH_TEST):
        if filename.is_file():
            reader = PdfReader(filename.path)
            is_ebay = check_if_ebay(reader)
            amount = get_amount(reader, is_ebay)
            date = get_date(reader, is_ebay)
            name = get_nome_fattura(reader, is_ebay)
            is_ppc = check_if_ppc(name)
            item_description = get_item_description(reader, is_ebay, is_ppc, name)
            print(f"{filename.name}: {is_ebay} {name} {date} {amount} {item_description}")

