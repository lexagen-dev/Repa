"""
Oblегченnyj primer: demonstraciya integracii parsera bez fakticheskogo parsinga.
Ispol'zuet mock-dannye dlya bystrogo testirovanniya.
"""

from datetime import datetime
from orders.order import Order, OrderItem
from export.email_formatter import EmailFormatter
from export.text_formatter import format_order_as_text
from export.table_formatter import format_order_as_html_table


# Mock-dannye - takie zhe, chto vozvrashchaet parser
MOCK_CATALOG = [
    {
        "Naimenovanie": "Maslo motornoe 5W-30 sinteticheskoe",
        "Kategoriya": "Motornye masla",
        "Naimenovanie EN": "Synthetic Motor Oil 5W-30",
        "Opisanie": "Vysokokachestvennoe sinteticheskoe maslo dlya sovremennyh avtomobilej. Obespechit maksimal'nую zaschitu dvigatelya pri vysokih temperaturah.",
        "Fasovki": ["0.75 l", "1 l", "5 l"],
        "Ssylka": "https://vitex.pro/catalog/oils/motor-oil-5w30/",
    },
    {
        "Naimenovanie": "Tormoznaya zhidkost' DOT 4",
        "Kategoriya": "Tormoznye zhidkosti",
        "Naimenovanie EN": "Brake Fluid DOT 4",
        "Opisanie": "Tormoznaya zhidkost' s vysokoj temperaturoj kipenya. Sootvetstvuet mezhdunarodno normy. Obespechit nadezhnost' tormoznoj sistemy.",
        "Fasovki": ["0.5 l", "1 l"],
        "Ssylka": "https://vitex.pro/catalog/oils/brake-fluid-dot4/",
    },
    {
        "Naimenovanie": "Antifriz ANTIFREEZE COOLANT",
        "Kategoriya": "Ohlazhdayushchie zhidkosti",
        "Naimenovanie EN": "Antifreeze Coolant",
        "Opisanie": "Universalnaya ohlazhdayushchaya zhidkost' dlya avtomobilej. Predotvrashchaet zamerzanie zimoj i kipenie letom.",
        "Fasovki": ["1 l", "5 l", "10 l"],
        "Ssylka": "https://vitex.pro/catalog/oils/antifreeze-coolant/",
    },
    {
        "Naimenovanie": "Vosk avtomobilnyj zaglyad",
        "Kategoriya": "Avtohimiya i poliroli",
        "Naimenovanie EN": "Car Wax Gloss",
        "Opisanie": "Zashchitnyj vosk dlya kuzova avtomobilya. Obespechit brilliant'nyj blesk i zaschitu ot vneshnih vozdejstvij.",
        "Fasovki": ["200 ml", "500 ml"],
        "Ssylka": "https://vitex.pro/catalog/wax/car-wax-gloss/",
    },
    {
        "Naimenovanie": "Zhidkost' dlya omyvatelja lopastej",
        "Kategoriya": "Zhidkosti ochistki",
        "Naimenovanie EN": "Windshield Washer Fluid",
        "Opisanie": "Speczialnaya zhidkost' dlya ochistki vetrovogo stekla i fov. Efektivno udalyaet gryaz' i nasekomelyh.",
        "Fasovki": ["1 l", "5 l"],
        "Ssylka": "https://vitex.pro/catalog/washer/windshield-washer/",
    },
]


def create_order_from_catalog(
    catalog: list,
    max_items: int = None,
    customer_name: str = "ООО ТехСервис",
    customer_email: str = "zakupki@techservice.ru"
) -> Order:
    """Sozdaet zajavku na osnove kataloga tovarov."""
    
    if max_items is None:
        max_items = len(catalog)
    
    order_id = "ORD-" + datetime.now().strftime("%Y%m%d-%H%M%S")
    order = Order(
        order_id=order_id,
        customer_name=customer_name,
        customer_email=customer_email,
    )
    
    for i, product in enumerate(catalog[:max_items], 1):
        
        # Avtomaticheski zadaem parametry
        quantity = i  # 1, 2, 3...
        price = 500.0 + (i * 150)  # 650, 800, 950...
        
        # Zadaem edinicu iz fasovki
        unit = "sht"
        if product.get("Fasovki"):
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
            notes="Dostupnye fasovki: " + ", ".join(product.get("Fasovki", []))
        )
        
        order.add_item(item)
    
    order.notes = "Avtomaticheski sozdannaya zajavka na osnove kataloga vitex.pro"
    order.calculate_total()
    order.status = "draft"
    
    return order


def print_section(title: str):
    """Vypechatyvaet zaglavok sekczii."""
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def main():
    """Demonstraciya raboty integracii."""
    
    print_section("DEMONSTRACIYA: PARSER + SISTEMA ZAJAVOK")
    
    # 1. Pokazyvaem katalog
    print("\n[1] DOSTUPNYJ KATALOG TOVAROV:")
    print("-" * 80)
    
    for i, product in enumerate(MOCK_CATALOG, 1):
        print(f"\n{i}. {product['Naimenovanie']}")
        print(f"   Kategoriya: {product['Kategoriya']}")
        print(f"   Anglijskoe: {product.get('Naimenovanie EN', '-')}")
        print(f"   Fasovki: {', '.join(product['Fasovki'])}")
        print(f"   Link: {product['Ssylka']}")
    
    # 2. Sozdaem zajavku
    print_section("[2] SOZDANIE ZAJAVKI NA OSNOVE KATALOGA")
    
    order = create_order_from_catalog(
        MOCK_CATALOG,
        max_items=4,
        customer_name="ООО ТехСервис",
        customer_email="zakupki@techservice.ru"
    )
    
    print(f"\nZajavka: {order.order_id}")
    print(f"Zakazchik: {order.customer_name}")
    print(f"Tovarov: {order.get_total_items()}")
    print(f"Summa: {order.total_sum:.2f} rub.")
    
    # 3. Pokazyvaem detali tovarov
    print("\nDetalі tovarov v zajavke:")
    print("-" * 80)
    
    for i, item in enumerate(order.items, 1):
        print(f"\n{i}. {item.product_name}")
        print(f"   Kategoriya: {item.category}")
        print(f"   Kol-vo: {item.quantity} {item.unit}")
        print(f"   Cena: {item.price:.2f} rub/ed")
        print(f"   Summa: {item.price * item.quantity:.2f} rub")
    
    # 4. Sohranenie zajavki
    print_section("[3] SOHRANENIE ZAJAVKI")
    
    from utils.order_manager import OrderManager
    manager = OrderManager()
    manager.save_order(order)
    
    print(f"Zajavka sokhranena v orders_storage/{order.order_id}.json")
    
    # 5. Eksport
    print_section("[4] EKSPORT V RAZLICHNYE FORMATY")
    
    formatter = EmailFormatter()
    files = formatter.export_to_files(order, './exports')
    
    # 6. Pokazyvaem tekstovyj format
    print_section("[5] TEKSTOVYJ FORMAT ZAJAVKI")
    
    text = format_order_as_text(order)
    print(text)
    
    # 7. Pokazyvaem HTML format
    print_section("[6] HTML FORMAT GOTOV DLYa EMAIL")
    
    html = format_order_as_html_table(order)
    print(f"HTML tablica sozhdana ({len(html)} bytes)")
    print("Mozhno otpravit' po email cherez EmailFormatter.send_email()")
    
    # 8. Pokazyvaem vozmozhnosti poiska
    print_section("[7] POISK TOVAROV V ZAJAVKAH")
    
    print("\nPrimer: Poisk zajavok s tovarom 'maslo':")
    results = manager.search_orders(query="maslo")
    for r in results:
        print(f"  - {r.order_id}: {r.customer_name} ({r.get_total_items()} tovarov)")
    
    print_section("[GOTOVO!]")
    
    print(f"""
Summarno v примере:
  - Katalog: {len(MOCK_CATALOG)} tovarov
  - Sozdana zajavka: {order.order_id}
  - Tovarov v zajavke: {order.get_total_items()}
  - Obshchaya summa: {order.total_sum:.2f} rub
  - Sohraneno fajlov: {len(files)}
  - Mesta sohraneniya:
    * Zajavka: orders_storage/{order.order_id}.json
    * Tekst: exports/{order.order_id}.txt
    * CSV: exports/{order.order_id}.csv
    * HTML: exports/{order.order_id}.html

SLEDUUSHCHIE SHAGI:
1. Zapustite parse_catalog() s real'nym URL dlya polucheniya tovarov s vitex.pro
2. Sozdajte zajavku automaticheski na osnove parshennyh tovarov
3. Otpravte zajavku po email cherez EmailFormatter
""")


if __name__ == "__main__":
    main()
