#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Polnyj primer: Parser -> Excel -> Zajavka -> Pismo
Lakokrasochnyе materialy sistemy
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parsers.catalog_parser_v2 import parse_catalog
from export.catalog_manager import CatalogExcelManager
from export.email_formatter import EmailFormatter
from export.text_formatter import format_order_as_text
from utils.order_manager import OrderManager


def print_header(text: str):
    """Pechatyvaet zaglavok."""
    print("\n" + "=" * 80)
    print(text)
    print("=" * 80)


def main():
    """Polnyj ciklol: Parsing -> Excel -> Zajavka."""
    
    print_header("SISTEMA ZAJAVOK DLYA LAKOKRASOCHNYH MATERIALOV")
    
    # ETAP 1: PARSING KATALOGA
    print_header("[ETAP 1] Parsing kataloga lakokrasochnyh materialov")
    
    print("\nEsli khote use real'nyj parsing, zadajte URL:")
    print("  Primer: https://vitex.pro/catalog/paints/")
    print("")
    
    # Dlya primera - demo-dannye
    demo_catalog = [
        {
            "Kategoriya": "Kraski akrilovy",
            "Naimenovanie RU": "Kraski belyy akril",
            "Naimenovanie EN": "White Acrylic Paint",
            "Opisanie": "Belyaya akrilovaya kraska dlya vnutrennih rabot. Ekologichno bezopasna, bystro sukhnet.",
            "Fasovka": "0.5 l",
            "Ssylka": "https://vitex.pro/catalog/paint/white-acrylic/",
        },
        {
            "Kategoriya": "Kraski akrilovy",
            "Naimenovanie RU": "Kraski belyy akril",
            "Naimenovanie EN": "White Acrylic Paint",
            "Opisanie": "Belyaya akrilovaya kraska dlya vnutrennih rabot. Ekologichno bezopasna, bystro sukhnet.",
            "Fasovka": "1 l",
            "Ssylka": "https://vitex.pro/catalog/paint/white-acrylic/",
        },
        {
            "Kategoriya": "Kraski akrilovy",
            "Naimenovanie RU": "Kraski belyy akril",
            "Naimenovanie EN": "White Acrylic Paint",
            "Opisanie": "Belyaya akrilovaya kraska dlya vnutrennih rabot. Ekologichno bezopasna, bystro sukhnet.",
            "Fasovka": "5 l",
            "Ssylka": "https://vitex.pro/catalog/paint/white-acrylic/",
        },
        {
            "Kategoriya": "Kraski akrilovy",
            "Naimenovanie RU": "Kraski krasny akril",
            "Naimenovanie EN": "Red Acrylic Paint",
            "Opisanie": "Krasnya akrilovaya kraska. Nasyshhennыj tsvet, vysokaya kryyyushchaya sposobnost.",
            "Fasovka": "1 l",
            "Ssylka": "https://vitex.pro/catalog/paint/red-acrylic/",
        },
        {
            "Kategoriya": "Kraski akrilovy",
            "Naimenovanie RU": "Kraski krasny akril",
            "Naimenovanie EN": "Red Acrylic Paint",
            "Opisanie": "Krasnya akrilovaya kraska. Nasyshhennыj tsvet, vysokaya kryyyushchaya sposobnost.",
            "Fasovka": "5 l",
            "Ssylka": "https://vitex.pro/catalog/paint/red-acrylic/",
        },
        {
            "Kategoriya": "Gruntovki",
            "Naimenovanie RU": "Gruntovka akrilova",
            "Naimenovanie EN": "Acrylic Primer",
            "Opisanie": "Profesional'naya gruntovka dlya podgotovki poverkhnosti pod krasku.",
            "Fasovka": "1 l",
            "Ssylka": "https://vitex.pro/catalog/primer/acrylic/",
        },
        {
            "Kategoriya": "Gruntovki",
            "Naimenovanie RU": "Gruntovka akrilova",
            "Naimenovanie EN": "Acrylic Primer",
            "Opisanie": "Profesional'naya gruntovka dlya podgotovki poverkhnosti pod krasku.",
            "Fasovka": "5 l",
            "Ssylka": "https://vitex.pro/catalog/primer/acrylic/",
        },
        {
            "Kategoriya": "Laki",
            "Naimenovanie RU": "Lakirovka mat",
            "Naimenovanie EN": "Matte Varnish",
            "Opisanie": "Mattovaya lakirovka dlya zaschity derevyanyh poverkhnostej.",
            "Fasovka": "0.75 l",
            "Ssylka": "https://vitex.pro/catalog/varnish/matte/",
        },
        {
            "Kategoriya": "Laki",
            "Naimenovanie RU": "Lakirovka glyanczevaya",
            "Naimenovanie EN": "Glossy Varnish",
            "Opisanie": "Glyanczevaya lakirovka s vysokim bleskom.",
            "Fasovka": "0.5 l",
            "Ssylka": "https://vitex.pro/catalog/varnish/glossy/",
        },
        {
            "Kategoriya": "Laki",
            "Naimenovanie RU": "Lakirovka glyanczevaya",
            "Naimenovanie EN": "Glossy Varnish",
            "Opisanie": "Glyanczevaya lakirovka s vysokim bleskom.",
            "Fasovka": "1 l",
            "Ssylka": "https://vitex.pro/catalog/varnish/glossy/",
        },
    ]
    
    print(f"[OK] Katalog: {len(demo_catalog)} pozicij (dlya primiera)")
    print(f"     Kategorii: Kraski, Gruntovki, Laki")
    
    # ETAP 2: EKSPORT V EXCEL
    print_header("[ETAP 2] Eksport v Excel")
    
    manager = CatalogExcelManager()
    excel_file = "lakokrasochnyе_tovarу.xlsx"
    manager.export_catalog_to_excel(demo_catalog, excel_file)
    
    # ETAP 3: SIMULIRUEM ZAPOLNENIE (v real'nosti pol'zovatel' zapolnyaet v Excel)
    print_header("[ETAP 3] Zapolnenie kolichestv (simulyacija)")
    
    print(f"\n! VAZHNO:")
    print(f"  1. Otkrojte fajl: {excel_file}")
    print(f"  2. Zapolnite kolonu 'Kolichestvo' dlya nuzhnyh tovarov")
    print(f"  3. Sokhranite fajl")
    print(f"\nDlya demona - avtomaticheski zapolnyaem:")
    
    # Zagruzhaem i zapolnyaem (dlya primera)
    from openpyxl import load_workbook
    
    wb = load_workbook(excel_file)
    ws = wb.active
    
    # Zapolnyaem sluchaynye kolichestvy
    quantities_to_add = [
        (2, 2),   # Stroka 2: 2 sht
        (3, 5),   # Stroka 3: 5 sht
        (4, 3),   # Stroka 4: 3 sht
        (6, 1),   # Stroka 6: 1 sht
        (8, 10),  # Stroka 8: 10 sht
        (9, 2),   # Stroka 9: 2 sht
    ]
    
    for row, qty in quantities_to_add:
        ws[f'G{row}'] = qty
        print(f"   {ws[f'B{row}'].value} ({ws[f'E{row}'].value}): {qty} sht")
    
    wb.save(excel_file)
    wb.close()
    
    # ETAP 4: SOZDANIE ZAJAVKI
    print_header("[ETAP 4] Sozdanie zajavki iz kataloga")
    
    order = manager.create_order_from_excel(
        excel_file,
        customer_name="OOO PromsYt",
        customer_email="zakupki@promsyt.ru"
    )
    
    if not order:
        print("[ERROR] Ne udalosy sozdaty zajavku!")
        return
    
    # ETAP 5: POKAZYVAEM DETALI
    print_header("[ETAP 5] Detali zajavki")
    
    print(f"\nZajavka: {order.order_id}")
    print(f"Zakazchik: {order.customer_name}")
    print(f"Email: {order.customer_email}")
    print(f"Vsego pozicij: {order.get_total_items()}")
    print(f"Obshchaya summa: {order.total_sum:.2f} RUB")
    
    print("\nPozicii:")
    print("-" * 80)
    
    for i, item in enumerate(order.items, 1):
        print(f"\n{i}. {item.product_name}")
        print(f"   Kategoriya: {item.category}")
        print(f"   Fasovka: {item.quantity} {item.unit}")
        print(f"   Cena: {item.price:.2f} RUB/ed")
        print(f"   Summa: {item.price * item.quantity:.2f} RUB")
        if item.notes:
            print(f"   Primechanie: {item.notes}")
    
    # ETAP 6: SOHRANENIE
    print_header("[ETAP 6] Sohranenie zajavki")
    
    om = OrderManager()
    om.save_order(order)
    
    # ETAP 7: PISMO
    print_header("[ETAP 7] Pismo dlya otpravki")
    
    text_letter = format_order_as_text(order)
    print(text_letter)
    
    # ETAP 8: EKSPORT
    print_header("[ETAP 8] Eksport v razlichnye formaty")
    
    formatter = EmailFormatter()
    files = formatter.export_to_files(order, './exports')
    
    # ETAP 9: VOZMOZHNOSTI
    print_header("[ETAP 9] Sleduyshhie shagi")
    
    print(f"""
[1] Dlya real'nogo parsinga:
    from parsers.catalog_parser_v2 import parse_catalog
    
    katalog = parse_catalog([
        "https://vitex.pro/catalog/paints/",
        "https://vitex.pro/catalog/varnishes/",
    ])
    
    manager.export_catalog_to_excel(katalog, "my_catalog.xlsx")

[2] Dlya otpravki po email:
    formatter = EmailFormatter(
        smtp_host='smtp.gmail.com',
        sender_email='your@gmail.com',
        sender_password='app_password'
    )
    formatter.send_email(order)

[3] Automation:
    - Kazhdyj den' parsing'ova'te novyj katalog
    - Sohranite v baze dannyh
    - Pol'zovateli zapolnyayut kolichestva v Excel
    - Avtomaticheski generiruetsya pismo i otpravljaetsya

[4] Integraciya:
    - Integriruyte s CRM (Bitrix24, 1C)
    - Nastrojte avtomaticheskuyu priem zayavok
    - Osledite status dostavki
""")
    
    print_header("[GOTOVO!]")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[ERROR] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
