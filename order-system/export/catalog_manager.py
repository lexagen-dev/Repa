"""
Rabota s katalogom v formate Excel.
Zagruzka kataloga v XL, zapolnenie kolichestv, sozdanie zajavki.
"""

import os
from typing import List, Optional
from datetime import datetime

try:
    from openpyxl import Workbook, load_workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
except ImportError:
    raise ImportError("Trebuetsya openpyxl: pip install openpyxl")

from orders.order import Order, OrderItem


class CatalogExcelManager:
    """Menedzher dlya raboty s katalogom v Excel."""
    
    def __init__(self, filename: str = "catalog.xlsx"):
        """
        Inicializacija.
        
        Args:
            filename: Imya Excel fajla
        """
        self.filename = filename
        self.workbook = None
        self.worksheet = None
    
    def export_catalog_to_excel(self, catalog: List[dict], output_file: str = None) -> str:
        """
        Eksportiruet katalog v Excel fajl.
        
        Args:
            catalog: Spisok tovarov iz parsera
            output_file: Imya vyhodno fajla (esli None, ispolzuetsya self.filename)
            
        Returns:
            Put' k sohranennomy fajlu
        """
        if output_file is None:
            output_file = self.filename
        
        # Sozdaem novуy workbook
        self.workbook = Workbook()
        self.worksheet = self.workbook.active
        self.worksheet.title = "Katalog"
        
        # Zaglavok tablicy
        headers = [
            "Nomer",
            "Russkoe Naimenovanie",
            "Anglijskoe Naimenovanie",
            "Kategoriya",
            "Fasovka",
            "Opisanie",
            "Kolichestvo",
            "URL",
        ]
        
        self.worksheet.append(headers)
        
        # Stil zaglavka
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF")
        header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        
        for cell in self.worksheet[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = header_alignment
        
        # Dobavlyaem dannye
        for i, position in enumerate(catalog, 1):
            row = [
                i,
                position.get("Naimenovanie RU", ""),
                position.get("Naimenovanie EN", ""),
                position.get("Kategoriya", ""),
                position.get("Fasovka", ""),
                position.get("Opisanie", "")[:50],  # Pervyh 50 simvolov
                "",  # Kolichestvo - ostaetsya pustym dlya zapolneniya
                position.get("Ssylka", ""),
            ]
            self.worksheet.append(row)
        
        # Avtomaticheskij razmer kolonok
        self.worksheet.column_dimensions['A'].width = 6
        self.worksheet.column_dimensions['B'].width = 25
        self.worksheet.column_dimensions['C'].width = 25
        self.worksheet.column_dimensions['D'].width = 15
        self.worksheet.column_dimensions['E'].width = 12
        self.worksheet.column_dimensions['F'].width = 40
        self.worksheet.column_dimensions['G'].width = 12
        self.worksheet.column_dimensions['H'].width = 40
        
        # Visota zagolovka
        self.worksheet.row_dimensions[1].height = 30
        
        # Centrirovka dlya kolichestv
        for row in range(2, len(catalog) + 2):
            self.worksheet[f'G{row}'].alignment = Alignment(horizontal="center")
        
        # Sohranenie
        self.workbook.save(output_file)
        
        print(f"[OK] Katalog eksportirovan: {output_file}")
        print(f"     Tovarov: {len(catalog)}")
        
        return output_file
    
    def load_catalog_with_quantities(self, excel_file: str) -> List[dict]:
        """
        Zagruzhaet katalog iz Excel fajla s zapolnennymi kolichestyami.
        
        Args:
            excel_file: Imya Excel fajla
            
        Returns:
            Spisok pozicij s kolichestyami
        """
        if not os.path.exists(excel_file):
            print(f"[ERROR] Fajl ne najden: {excel_file}")
            return []
        
        workbook = load_workbook(excel_file)
        worksheet = workbook.active
        
        positions = []
        
        for row_idx, row in enumerate(worksheet.iter_rows(min_row=2, values_only=False), start=2):
            try:
                # Poluchaem znachenia
                nomer = row[0].value
                name_ru = row[1].value
                name_en = row[2].value
                category = row[3].value
                fasovka = row[4].value
                opisanie = row[5].value
                quantity = row[6].value
                url = row[7].value
                
                # Konvertiruem kolichestvo v int
                try:
                    quantity = int(quantity) if quantity else 0
                except (ValueError, TypeError):
                    quantity = 0
                
                position = {
                    "Nomer": nomer,
                    "Naimenovanie RU": name_ru or "",
                    "Naimenovanie EN": name_en or "",
                    "Kategoriya": category or "",
                    "Fasovka": fasovka or "",
                    "Opisanie": opisanie or "",
                    "Kolichestvo": quantity,
                    "Ssylka": url or "",
                }
                
                positions.append(position)
                
            except Exception as e:
                print(f"[WARNING] Oshibka pri chtenii stroki {row_idx}: {e}")
                continue
        
        workbook.close()
        
        return positions
    
    def create_order_from_excel(
        self,
        excel_file: str,
        customer_name: str = "TechService LLC",
        customer_email: str = "zakupki@company.ru"
    ) -> Optional[Order]:
        """
        Sozdaet zajavku iz Excel kataloga (gde zapolneny kolichestya).
        
        Args:
            excel_file: Imya Excel fajla s zapolnennymi kolichestyami
            customer_name: Imya zakazchika
            customer_email: Email zakazchika
            
        Returns:
            Ob'ekt Order ili None
        """
        # Zagruzhaem pozicii s kolichestyami
        positions = self.load_catalog_with_quantities(excel_file)
        
        if not positions:
            print("[ERROR] Ne udalosy zagruzit pozicii iz Excel!")
            return None
        
        # Filtruem - tolko gde kolichestvo > 0
        selected = [p for p in positions if p["Kolichestvo"] > 0]
        
        if not selected:
            print("[WARNING] Net pozicij s kolichestvom > 0!")
            return None
        
        # Sozdaem zajavku
        order = Order(
            order_id="ORD-" + datetime.now().strftime("%Y%m%d-%H%M%S"),
            customer_name=customer_name,
            customer_email=customer_email,
        )
        
        # Dobavlyaem pozicii
        for position in selected:
            
            # Zadaem default cenu (mozhno dobavit' v Excel)
            price = 1000.0  # Default cena
            
            item = OrderItem(
                product_name=position["Naimenovanie RU"],
                category=position["Kategoriya"],
                quantity=position["Kolichestvo"],
                unit=position["Fasovka"],
                price=price,
                product_url=position["Ssylka"],
                notes=f"EN: {position['Naimenovanie EN']}"
            )
            
            order.add_item(item)
        
        order.notes = f"Zajavka sozdana iz kataloga Excel\nData: {datetime.now().strftime('%d.%m.%Y %H:%M')}\nIsbrano tovarov: {len(selected)}"
        order.calculate_total()
        
        print(f"[OK] Zajavka sozdana: {order.order_id}")
        print(f"     Pozicij: {order.get_total_items()}")
        print(f"     Summa: {order.total_sum:.2f}")
        
        return order


# Vspomogatel'nye funkcii

def create_sample_excel_catalog(output_file: str = "sample_catalog.xlsx"):
    """Sozdaet sample Excel katalog dlya testirovaniя."""
    
    manager = CatalogExcelManager()
    
    # Sample tovarи
    sample_catalog = [
        {
            "Naimenovanie RU": "Kraski belyy akril",
            "Naimenovanie EN": "White Acrylic Paint",
            "Kategoriya": "Kraski",
            "Fasovka": "0.5 l",
            "Opisanie": "Belyaya akrilovaya kraska dlya vnutrennih rabot",
            "Ssylka": "https://vitex.pro/catalog/paint/white-acrylic-05/",
        },
        {
            "Naimenovanie RU": "Kraski belyy akril",
            "Naimenovanie EN": "White Acrylic Paint",
            "Kategoriya": "Kraski",
            "Fasovka": "1 l",
            "Opisanie": "Belyaya akrilovaya kraska dlya vnutrennih rabot",
            "Ssylka": "https://vitex.pro/catalog/paint/white-acrylic-1l/",
        },
        {
            "Naimenovanie RU": "Kraski belyy akril",
            "Naimenovanie EN": "White Acrylic Paint",
            "Kategoriya": "Kraski",
            "Fasovka": "5 l",
            "Opisanie": "Belyaya akrilovaya kraska dlya vnutrennih rabot",
            "Ssylka": "https://vitex.pro/catalog/paint/white-acrylic-5l/",
        },
        {
            "Naimenovanie RU": "Gruntovka akril",
            "Naimenovanie EN": "Acrylic Primer",
            "Kategoriya": "Gruntovki",
            "Fasovka": "1 l",
            "Opisanie": "Gruntovka dlya podgotovki poverkhnosti",
            "Ssylka": "https://vitex.pro/catalog/primer/acrylic-1l/",
        },
        {
            "Naimenovanie RU": "Gruntovka akril",
            "Naimenovanie EN": "Acrylic Primer",
            "Kategoriya": "Gruntovki",
            "Fasovka": "5 l",
            "Opisanie": "Gruntovka dlya podgotovki poverkhnosti",
            "Ssylka": "https://vitex.pro/catalog/primer/acrylic-5l/",
        },
        {
            "Naimenovanie RU": "Lakirovka mat",
            "Naimenovanie EN": "Matte Varnish",
            "Kategoriya": "Lak",
            "Fasovka": "0.75 l",
            "Opisanie": "Mattovaya lakirovka dlya derevyanyh poverkhnostej",
            "Ssylka": "https://vitex.pro/catalog/varnish/matte-075/",
        },
    ]
    
    manager.export_catalog_to_excel(sample_catalog, output_file)
    
    print(f"\n[!] Dlya testa:")
    print(f"    1. Otkrojte {output_file}")
    print(f"    2. Zapolnite kolonu 'Kolichestvo' dlya nuzhnyh pozicij")
    print(f"    3. Sokhranite fajl")
    print(f"    4. Zapustite: python -c \"from export.catalog_manager import CatalogExcelManager; "
          f"m = CatalogExcelManager(); order = m.create_order_from_excel('{output_file}'); "
          f"print('Zajavka gotova!')\"")
    
    return output_file


if __name__ == "__main__":
    # Primer: Sozdaem sample katalog
    create_sample_excel_catalog()
