import os
from PyPDF2 import PdfReader

AMOUNT_CAPTION = ["TOTALES", "Totali", "GESAMT", "Total", "TOTALE", 'Totale fattura corrente in EUR', "TOTAL"]
DATE_CAPTION = ["Fecha de la factura", "Rechnungsdatum", "Data fattura", "Fecha de emisión de la nota de crédito", "Ausstellungsdatum der Gutschrift", "Data emissione nota di credito"]
NAME_CAPTION = ["Número de la factura", "Rechnungsnr", "Numero fattura:", "Número de nota de crédito", "Gutschriftennummer", "Numero nota di credito:"]
PPC_CAPTION = ['ITAOIT3', 'ES-AOES']
PATH = "fatture"

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
                return f"{giorno}/{mese}/{anno}"

    for elem in text.split("\n"):
        if check_if_contain_caption(elem, DATE_CAPTION):
            return elem.split(": ")[1].strip()

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
                return elem.split(": ")[1].strip()
            except IndexError:
                return text_splitted[text_splitted.index(elem)+1]

def check_if_ebay(reader):
    page = reader.pages[0]
    if 'eBay' in page.extract_text():
        return True
    return False

def test_scrape_pdf():
    for filename in os.scandir(PATH):
        if filename.is_file():
            reader = PdfReader(filename.path)
            is_ebay = check_if_ebay(reader)
            amount = get_amount(reader, is_ebay)
            date_raw = get_date(reader, is_ebay)
            nome_fattura = get_nome_fattura(reader, is_ebay)
            is_ppc = True if check_if_contain_caption(nome_fattura, PPC_CAPTION) else False
            print(f"{filename.name}: {nome_fattura} {date_raw} {amount} {is_ppc}")

test_scrape_pdf()