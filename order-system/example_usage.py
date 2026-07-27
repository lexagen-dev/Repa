"""Пример использования системы заявок на продукцию."""

from orders.order import Order, OrderItem
from export.email_formatter import EmailFormatter
from export.text_formatter import format_order_as_text
from export.table_formatter import format_order_as_html_table
from utils.order_manager import OrderManager


def main():
    """Демонстрация работы системы."""
    
    # 1. Создание заявки
    print("=" * 70)
    print("1. СОЗДАНИЕ ЗАЯВКИ")
    print("=" * 70)
    
    order = Order(
        order_id="ORD-2024-001",
        customer_name="Иван Петров",
        customer_email="ivan@example.com",
    )
    
    # Добавление товаров
    order.add_item(OrderItem(
        product_name="Автомобильное масло",
        category="Масла и жидкости",
        quantity=10,
        unit="л",
        price=250.0,
        product_url="https://vitex.pro/catalog/oils/motor-oil/",
        notes="Срочно нужно"
    ))
    
    order.add_item(OrderItem(
        product_name="Тормозная жидкость",
        category="Масла и жидкости",
        quantity=5,
        unit="л",
        price=180.0,
        product_url="https://vitex.pro/catalog/oils/brake-fluid/",
    ))
    
    order.add_item(OrderItem(
        product_name="Воск для кузова",
        category="Уход за автомобилем",
        quantity=2,
        unit="шт",
        price=450.0,
    ))
    
    # Добавляем примечания и рассчитываем сумму
    order.notes = "Доставить на адрес: ул. Ленина, 10, офис 5"
    order.calculate_total()
    order.status = "sent"
    
    print("[OK] Создана заявка " + order.order_id)
    print("  - Заказчик: " + order.customer_name)
    print("  - Позиций: " + str(order.get_total_items()))
    print("  - Сумма: {:.2f} руб.".format(order.total_sum))
    
    # 2. Сохранение заявки
    print("\n" + "=" * 70)
    print("2. СОХРАНЕНИЕ ЗАЯВКИ")
    print("=" * 70)
    print("")
    
    manager = OrderManager()
    manager.save_order(order)
    
    # 3. Экспорт в разные форматы
    print("\n" + "=" * 70)
    print("3. ЭКСПОРТ В РАЗНЫЕ ФОРМАТЫ")
    print("=" * 70)
    
    # Текстовый формат
    print("\nТекстовый формат:")
    print("-" * 70)
    text_content = format_order_as_text(order)
    print(text_content[:500] + "\n... (сокращено)")
    
    # HTML таблица
    print("\nHTML tablica:")
    print("-" * 70)
    html_content = format_order_as_html_table(order)
    print("[OK] Sozdana HTML tablica dlya email")
    
    # Экспорт в файлы
    print("")
    email_formatter = EmailFormatter()
    files = email_formatter.export_to_files(order, './exports')
    
    # 4. Загрузка сохраненной заявки
    print("\n" + "=" * 70)
    print("4. ЗАГРУЗКА СОХРАНЕННОЙ ЗАЯВКИ")
    print("=" * 70)
    print("")
    
    loaded_order = manager.load_order("ORD-2024-001.json")
    if loaded_order:
        print("[OK] Загруженная заявка:")
        print("  - ID: " + loaded_order.order_id)
        print("  - Заказчик: " + loaded_order.customer_name)
        print("  - Позиций: " + str(loaded_order.get_total_items()))
        print("  - Сумма: {:.2f} руб.".format(loaded_order.total_sum))
    
    # 5. Демонстрация отправки email (конфигурация требуется)
    print("\n" + "=" * 70)
    print("5. ОТПРАВКА ПО EMAIL")
    print("=" * 70)
    
    print("\nДля отправки email требуется конфигурация:")
    print("  email_formatter = EmailFormatter(")
    print("      smtp_host='smtp.gmail.com',")
    print("      smtp_port=587,")
    print("      sender_email='your@email.com',")
    print("      sender_password='app_password'")
    print("  )")
    print("  email_formatter.send_email(order)")
    
    # 6. Поиск заявок
    print("\n" + "=" * 70)
    print("6. ПОИСК ЗАЯВОК")
    print("=" * 70)
    print("")
    
    results = manager.search_orders(query="масло")
    print("По запросу 'масло' найдено заявок: " + str(len(results)))
    for r in results:
        print("  - {}: {}".format(r.order_id, r.customer_name))
    
    print("\n" + "=" * 70)
    print("ГОТОВО!")
    print("=" * 70)


if __name__ == "__main__":
    main()
