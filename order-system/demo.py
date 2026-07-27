#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Privet: Polnaya integracija parsera s sistemoj zajavok.
Primechatelnaya: Prostoj vyvod, sovmestimyj s Windows
"""

import sys
import os
from datetime import datetime

# Dobavlyaem papku v sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from orders.order import Order, OrderItem
from export.email_formatter import EmailFormatter
from utils.order_manager import OrderManager


def print_header(text):
    print("\n" + "=" * 80)
    print(text)
    print("=" * 80)


def demo_with_mock_data():
    """Demo s mock-dannymi (ne trebuet interneta)"""
    
    print_header("DEMO: PARSER + SISTEMA ZAJAVOK (Mock-dannye)")
    
    # Mock-katalog (takie zhe dannye vozvrashchaet parser)
    catalog = [
        {
            "name": "Motor Oil 5W-30",
            "category": "Oils",
            "price_base": 600,
            "packages": ["0.75L", "1L", "5L"],
            "url": "https://vitex.pro/catalog/oils/motor-oil-5w30/",
        },
        {
            "name": "Brake Fluid DOT 4",
            "category": "Fluids",
            "price_base": 400,
            "packages": ["0.5L", "1L"],
            "url": "https://vitex.pro/catalog/brake-fluid-dot4/",
        },
        {
            "name": "Antifreeze Coolant",
            "category": "Coolant",
            "price_base": 300,
            "packages": ["1L", "5L"],
            "url": "https://vitex.pro/catalog/antifreeze/",
        },
    ]
    
    print("\n[STEP 1] Catalog products (from parser):")
    print("-" * 80)
    
    for i, product in enumerate(catalog, 1):
        print(f"\n{i}. {product['name']}")
        print(f"   Category: {product['category']}")
        print(f"   Available: {', '.join(product['packages'])}")
        print(f"   URL: {product['url']}")
    
    # Sozdaem zajavku
    print_header("[STEP 2] Create order from catalog")
    
    order = Order(
        order_id="ORD-" + datetime.now().strftime("%Y%m%d-%H%M%S"),
        customer_name="TechService LLC",
        customer_email="zakupki@techservice.ru",
    )
    
    # Dobavlyaem tovary
    for i, product in enumerate(catalog, 1):
        item = OrderItem(
            product_name=product["name"],
            category=product["category"],
            quantity=i,
            unit="pcs",
            price=product["price_base"] + (i * 50),
            product_url=product["url"],
            notes=f"Available: {', '.join(product['packages'])}"
        )
        order.add_item(item)
    
    order.calculate_total()
    order.notes = "Auto-created from catalog parser"
    order.status = "draft"
    
    print(f"\nOrder created: {order.order_id}")
    print(f"Items: {order.get_total_items()}")
    print(f"Total: {order.total_sum:.2f} RUB")
    
    # Pokazyvaem tovary v zajavke
    print("\nItems in order:")
    print("-" * 80)
    
    for i, item in enumerate(order.items, 1):
        print(f"\n{i}. {item.product_name}")
        print(f"   Qty: {item.quantity} {item.unit} @ {item.price:.2f} RUB")
        print(f"   Total: {item.price * item.quantity:.2f} RUB")
        print(f"   Notes: {item.notes}")
    
    # Sohranenie
    print_header("[STEP 3] Save order")
    
    manager = OrderManager()
    manager.save_order(order)
    print(f"[OK] Order saved")
    
    # Eksport
    print_header("[STEP 4] Export formats")
    
    formatter = EmailFormatter()
    files = formatter.export_to_files(order, './exports')
    
    # Pokazyvaem tekstovyj format
    print_header("[STEP 5] Text format preview")
    
    from export.text_formatter import format_order_as_text
    text = format_order_as_text(order)
    print(text)
    
    # Pokazyvaem vozmozhnosti
    print_header("[STEP 6] Available operations")
    
    print("""
[1] Search orders:
    results = manager.search_orders(query="Oil")
    
[2] Send by email:
    formatter = EmailFormatter(
        smtp_host='smtp.gmail.com',
        sender_email='your@gmail.com',
        sender_password='app_password'
    )
    formatter.send_email(order)

[3] Load saved order:
    order = manager.load_order("ORD-xxx.json")

[4] Export formats:
    - TXT: exports/ORD-xxx.txt
    - CSV: exports/ORD-xxx.csv
    - HTML: exports/ORD-xxx.html
""")
    
    print_header("[COMPLETE!]")
    
    print(f"""
Summary:
  - Products in catalog: {len(catalog)}
  - Order created: {order.order_id}
  - Items in order: {order.get_total_items()}
  - Total sum: {order.total_sum:.2f} RUB
  - Files saved: {len(files)}
""")


if __name__ == "__main__":
    try:
        demo_with_mock_data()
    except Exception as e:
        print(f"\n[ERROR] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
