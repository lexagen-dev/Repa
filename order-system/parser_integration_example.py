"""
Primer integracii parsera s sistemoj zajavok.
Parsit tovar iz kataloga vitex.pro i sozdaet zajavku.
"""

from datetime import datetime
from orders.order import Order, OrderItem
from export.email_formatter import EmailFormatter
from export.text_formatter import format_order_as_text
from parsers.catalog_parser import parse_catalog


def create_order_from_parsed_products(
    products: list,
    max_items: int = 5,
    customer_name: str = "OOO Kompaniya",
    customer_email: str = "zakupki@company.com"
) -> Order:
    """
    Sozdaet zajavku na osnove parshennyh tovarov.
    
    Args:
        products: Список товаров из парсера
        max_items: Maksimum tovarov v zajavke
        customer_name: Imya zakazchika
        customer_email: Email zakazchika
        
    Returns:
        Ob'ekt Order s tovarami
    """
    
    # Sozdaem zajavku
    order_id = "ORD-" + datetime.now().strftime("%Y%m%d-%H%M%S")
    order = Order(
        order_id=order_id,
        customer_name=customer_name,
        customer_email=customer_email,
    )
    
    # Dobavlyaem tovary iz kataloga
    for i, product in enumerate(products[:max_items], 1):
        
        # Zadaem kol-vo i cenu (primer)
        quantity = i  # 1, 2, 3...
        price = 500.0 + (i * 100)  # 600, 700, 800...
        
        # Poluchaem pervuyu fasovku iz spiska (esli est')
        unit = "sht"
        if product.get("Fasovki"):
            # Izvlekaem edinicu iz pervoj fasovki (naprimer, iz "750 ml" -> "ml")
            first_package = product["Fasovki"][0]
            if " " in first_package:
                _, unit = first_package.rsplit(" ", 1)
        
        item = OrderItem(
            product_name=product["Naimenovanie"],
            category=product["Kategoriya"],
            quantity=quantity,
            unit=unit,
            price=price,
            product_url=product["Ssylka"],
            notes="Fasovki: " + (", ".join(product.get("Fasovki", [])) or "ne ukazany")
        )
        
        order.add_item(item)
        
        print(f"[+] Tovar {i}: {product['Naimenovanie']}")
    
    # Raschet itogoj sumy
    order.notes = f"Avtomaticheski sozdannaya zajavka na osnove parsinga kataloga vitex.pro\nData: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
    order.calculate_total()
    order.status = "draft"
    
    return order


def main():
    """Demontraciya raboty parsera i integracii s zajavkami."""
    
    print("=" * 80)
    print("PRIMER: PARSING KATALOGA VITEX.PRO I SOZDANIE ZAJAVKI")
    print("=" * 80)
    print("")
    
    # 1. PARSING KATALOGA
    print("ETAP 1: PARSING KATALOGA")
    print("-" * 80)
    
    # Zadaem razdely kataloga dlya parsinga
    sections = [
        "https://vitex.pro/catalog/oils/",
        # "https://vitex.pro/catalog/fuel-additives/",  # Rasskomentuiruyte dlya bolshego kataloga
    ]
    
    print("Parsim razdely:")
    for section in sections:
        print(f"  - {section}")
    print("")
    
    # Poluchaem tovary iz kataloga
    print("[...] Zagruzka kataloga (mozhet zanyat' 1-2 minuty)...")
    print("")
    
    products = parse_catalog(sections)
    
    if not products:
        print("[!] Oshibka: ne udalosy poluchit' tovary iz kataloga!")
        print("    Proverite:")
        print("    - Internet soedinenije")
        print("    - Korreknost URL razdolov kataloga")
        print("    - Dostupnost' sajta vitex.pro")
        return
    
    print(f"[OK] Polucheno tovarov: {len(products)}")
    print("")
    
    # 2. PRIVET TOVAROV
    print("ETAP 2: PRIVET POLUCHENNYH TOVAROV")
    print("-" * 80)
    
    for i, product in enumerate(products[:3], 1):  # Pokazyvaem pervyh 3
        print(f"\n{i}. {product['Naimenovanie']}")
        print(f"   Kategoriya: {product['Kategoriya']}")
        if product.get("Fasovki"):
            print(f"   Fasovki: {', '.join(product['Fasovki'][:3])}")
        if product.get("Opisanie"):
            desc = product["Opisanie"][:80]
            print(f"   Opisanie: {desc}...")
        print(f"   URL: {product['Ssylka']}")
    
    if len(products) > 3:
        print(f"\n... i eshhyo {len(products) - 3} tovarov")
    
    print("")
    
    # 3. SOZDANIE ZAJAVKI NA OSNOVE TOVAROV
    print("ETAP 3: SOZDANIE ZAJAVKI NA OSNOVE PARSHENNYH TOVAROV")
    print("-" * 80)
    print("")
    
    order = create_order_from_parsed_products(
        products,
        max_items=5,
        customer_name="ООО ТехСервис",
        customer_email="zakupki@techservice.ru"
    )
    
    print("")
    print(f"[OK] Sozdana zajavka {order.order_id}")
    print(f"    Zakazchik: {order.customer_name}")
    print(f"    Tovarov: {order.get_total_items()}")
    print(f"    Summa: {order.total_sum:.2f} rub.")
    print("")
    
    # 4. SOHRANENIE ZAJAVKI
    print("ETAP 4: SOHRANENIE ZAJAVKI")
    print("-" * 80)
    print("")
    
    from utils.order_manager import OrderManager
    manager = OrderManager()
    manager.save_order(order)
    
    print("")
    
    # 5. EKSPORT V RAZLICHNYE FORMATY
    print("ETAP 5: EKSPORT V RAZLICHNYE FORMATY")
    print("-" * 80)
    print("")
    
    formatter = EmailFormatter()
    files = formatter.export_to_files(order, './exports')
    
    print("")
    
    # 6. POKAZYVАEM TEKSTOVYY FORMAT
    print("ETAP 6: PREVIEW TEKSTOVOGO FORMATA ZAJAVKI")
    print("-" * 80)
    print("")
    
    text_format = format_order_as_text(order)
    print(text_format)
    
    # 7. PRIMER OTPRAVKI EMAIL
    print("ETAP 7: PRIMET OTPRAVKI EMAIL")
    print("-" * 80)
    print("")
    
    print("Dlya otpravki zajavki po email:")
    print("")
    print("  from export.email_formatter import EmailFormatter")
    print("  ")
    print("  formatter = EmailFormatter(")
    print("      smtp_host='smtp.gmail.com',")
    print("      smtp_port=587,")
    print("      sender_email='your@gmail.com',")
    print("      sender_password='app_password'")
    print("  )")
    print("  ")
    print("  formatter.send_email(order)")
    print("")
    print("=" * 80)
    print("[OK] PRIMER ZAVERSHEN!")
    print("=" * 80)


if __name__ == "__main__":
    main()
