"""Форматирование заявки в таблицу (CSV, HTML) для email."""
import csv
from io import StringIO
from orders.order import Order


def format_order_as_html_table(order: Order) -> str:
    """
    Форматирует заявку в HTML таблицу.
    
    Args:
        order: Объект заявки
        
    Returns:
        HTML код таблицы
    """
    html = f"""
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .info {{ margin-bottom: 20px; }}
        table {{ 
            border-collapse: collapse; 
            width: 100%; 
            margin-top: 20px;
        }}
        th, td {{ 
            border: 1px solid #ddd; 
            padding: 10px; 
            text-align: left;
        }}
        th {{ background-color: #4CAF50; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        .total {{ font-weight: bold; background-color: #e8f5e9; }}
        .footer {{ margin-top: 20px; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <h1>Zayavka na produktsiyu</h1>
    
    <div class="info">
        <p><strong>Номер заявки:</strong> {order.order_id}</p>
        <p><strong>Дата:</strong> {order.created_at.strftime('%d.%m.%Y %H:%M')}</p>
        <p><strong>Заказчик:</strong> {order.customer_name}</p>
        <p><strong>Email:</strong> {order.customer_email}</p>
        <p><strong>Статус:</strong> {order.status}</p>
    </div>
    
    <table>
        <thead>
            <tr>
                <th>№</th>
                <th>Название продукта</th>
                <th>Категория</th>
                <th>Количество</th>
                <th>Цена за ед.</th>
                <th>Сумма</th>
                <th>Примечания</th>
            </tr>
        </thead>
        <tbody>
"""
    
    total = 0
    for idx, item in enumerate(order.items, 1):
        price_str = f"{item.price:.2f}" if item.price else "-"
        
        if item.price:
            item_sum = item.price * item.quantity
            total += item_sum
            sum_str = f"{item_sum:.2f}"
        else:
            sum_str = "-"
        
        url_link = f'<a href="{item.product_url}" target="_blank">Ссылка</a>' if item.product_url else "-"
        notes = item.notes or "-"
        
        html += f"""
            <tr>
                <td>{idx}</td>
                <td>{item.product_name}</td>
                <td>{item.category}</td>
                <td>{item.quantity} {item.unit}</td>
                <td>{price_str}</td>
                <td>{sum_str}</td>
                <td>{notes}</td>
            </tr>
"""
    
    html += """
        </tbody>
    </table>
    
    <table style="width: auto; margin-top: 20px;">
        <tr class="total">
            <td>ИТОГО ПОЗИЦИЙ:</td>
            <td style="text-align: center;">""" + str(order.get_total_items()) + """</td>
        </tr>
"""
    
    if total > 0:
        html += f"""
        <tr class="total">
            <td>ИТОГОВАЯ СУММА:</td>
            <td style="text-align: right;">{total:.2f} руб.</td>
        </tr>
"""
    
    if order.notes:
        html += f"""
        <tr>
            <td colspan="2"><strong>Примечания заказа:</strong><br>{order.notes}</td>
        </tr>
"""
    
    html += """
    </table>
    
    <div class="footer">
        <p>Это автоматически сгенерированная заявка. Не отвечайте на это письмо.</p>
    </div>
</body>
</html>
"""
    return html


def format_order_as_csv(order: Order) -> str:
    """
    Форматирует заявку в CSV формат.
    
    Args:
        order: Объект заявки
        
    Returns:
        CSV строка
    """
    output = StringIO()
    writer = csv.writer(output, delimiter=';')
    
    # Заголовок информации
    writer.writerow(['ЗАЯВКА НА ПРОДУКЦИЮ'])
    writer.writerow(['Номер заявки', order.order_id])
    writer.writerow(['Дата', order.created_at.strftime('%d.%m.%Y %H:%M')])
    writer.writerow(['Заказчик', order.customer_name])
    writer.writerow(['Email', order.customer_email])
    writer.writerow(['Статус', order.status])
    writer.writerow([])  # Пустая строка
    
    # Таблица товаров
    writer.writerow([
        '№',
        'Название продукта',
        'Категория',
        'Количество',
        'Единица',
        'Цена за ед.',
        'Сумма',
        'Ссылка',
        'Примечания'
    ])
    
    for idx, item in enumerate(order.items, 1):
        price = item.price or ""
        sum_val = (item.price * item.quantity) if item.price else ""
        
        writer.writerow([
            idx,
            item.product_name,
            item.category,
            item.quantity,
            item.unit,
            price,
            sum_val,
            item.product_url or "",
            item.notes or "",
        ])
    
    writer.writerow([])
    writer.writerow(['ИТОГО ПОЗИЦИЙ:', order.get_total_items()])
    
    if order.total_sum:
        writer.writerow(['ИТОГО СУММА (руб.):', order.total_sum])
    
    return output.getvalue()


def save_csv_to_file(order: Order, filename: str) -> str:
    """Сохраняет заявку в CSV файл."""
    content = format_order_as_csv(order)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return filename


def save_html_to_file(order: Order, filename: str) -> str:
    """Сохраняет заявку в HTML файл."""
    content = format_order_as_html_table(order)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return filename
