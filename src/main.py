import os
from pdf import get_info_invoice
from fic import load_credentials, get_supplier, get_visible_subject, create_invoice
from getch import pause

PATH = "fatture"

def main():
    credentials = load_credentials()

    for filename in os.scandir(PATH):
        is_ebay, amount, date, name, item_description = get_info_invoice(filename)
        supplier_entity = get_supplier(credentials, is_ebay, name)
        visible_subject = get_visible_subject(is_ebay, name)

        create_invoice(credentials, supplier_entity, visible_subject, name, amount, date, item_description)
    pause('Press Any Key To Exit')

if __name__ == "__main__":
    main()