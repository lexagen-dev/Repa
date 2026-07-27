"""Форматирование заявки в текстовый формат для email."""
from orders.order import Order
from datetime import datetime


def format_order_as_text(order: Order) -> str:
    """
    Форматирует заявку в текстовый формат.
    
    Args:
        order: Объект заявки
        
    Returns:
        Отформатированная текстовая строка
    """
    lines = [
        "=" * 70,
        "ЗАЯВКА НА ПРОДУКЦИЮ",
        "=" * 70,
        f"Номер заявки: {order.order_id}",
        f"Дата создания: {order.created_at.strftime('%d.%m.%Y %H:%M:%S')}",
        f"Статус: {order.status}",
        "",
        "ДАННЫЕ ЗАКАЗЧИКА:",
        f"  Имя: {order.customer_name}",
        f"  Email: {order.customer_email}",
        "",
        "ПОЗИЦИИ ЗАЯВКИ:",
        "-" * 70,
    ]
    
    for idx, item in enumerate(order.items, 1):
        lines.extend([
            f"\n{idx}. {item.product_name}",
            f"   Категория: {item.category}",
            f"   Количество: {item.quantity} {item.unit}",
        ])
        
        if item.price:
            total_price = item.price * item.quantity
            lines.append(f"   Цена за единицу: {item.price:.2f} руб.")
            lines.append(f"   Сумма: {total_price:.2f} руб.")
        
        if item.product_url:
            lines.append(f"   Ссылка: {item.product_url}")
        
        if item.notes:
            lines.append(f"   Примечания: {item.notes}")
    
    lines.extend([
        "",
        "-" * 70,
        f"Итого позиций: {order.get_total_items()}",
    ])
    
    if order.total_sum:
        lines.append(f"ИТОГО СУММА: {order.total_sum:.2f} руб.")
    
    if order.notes:
        lines.extend([
            "",
            "ОБЩИЕ ПРИМЕЧАНИЯ:",
            order.notes,
        ])
    
    lines.extend([
        "",
        "=" * 70,
    ])
    
    return "\n".join(lines)


def save_text_to_file(order: Order, filename: str) -> str:
    """
    Сохраняет заявку в текстовый файл.
    
    Args:
        order: Объект заявки
        filename: Путь к файлу для сохранения
        
    Returns:
        Путь к сохраненному файлу
    """
    content = format_order_as_text(order)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return filename
