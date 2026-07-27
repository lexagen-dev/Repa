## Интеграция Парсера Витекс с Системой Заявок

Полный гайд по использованию парсера каталога витекс.про для создания заявок на продукцию.

### Основные возможности

- ✅ Парсинг каталога товаров с vitex.pro
- ✅ Извлечение названий, описаний, фасовок
- ✅ Автоматическое создание заявок из товаров
- ✅ Экспорт в TXT, CSV, HTML
- ✅ Отправка по email

---

## Быстрый старт

### 1. Настройка парсера

Откройте `parsers/config.py` и добавьте разделы каталога:

```python
# parsers/config.py
CATALOG_SECTIONS = [
    "https://vitex.pro/catalog/oils/",
    "https://vitex.pro/catalog/fuel-additives/",
    "https://vitex.pro/catalog/lubricants/",
]
```

### 2. Парсинг каталога

```python
from parsers.catalog_parser import parse_catalog

# Способ 1: Использование config.py
catalog = parse_catalog()

# Способ 2: Передача URL напрямую
catalog = parse_catalog([
    "https://vitex.pro/catalog/oils/",
])

# Результат - список словарей:
# [
#     {
#         "Naimenovanie": "Масло 5W-30",
#         "Kategoriya": "Моторные масла",
#         "Naimenovanie EN": "Motor Oil 5W-30",
#         "Opisanie": "Описание товара...",
#         "Fasovki": ["0.75 l", "1 l", "5 l"],
#         "Ssylka": "https://vitex.pro/...",
#     },
#     ...
# ]
```

### 3. Создание заявки из товаров

```python
from orders.order import Order, OrderItem
from parsers.catalog_parser import parse_catalog

# Получаем товары
products = parse_catalog(["https://vitex.pro/catalog/oils/"])

# Создаем заявку
order = Order(
    order_id="ORD-001",
    customer_name="ООО ТехСервис",
    customer_email="zakupki@techservice.ru",
)

# Добавляем товары из каталога
for i, product in enumerate(products[:5], 1):  # Первые 5 товаров
    
    # Получаем единицу из фасовки
    unit = "sht"
    if product.get("Fasovki"):
        first_package = product["Fasovki"][0]
        if " " in first_package:
            _, unit = first_package.rsplit(" ", 1)
    
    item = OrderItem(
        product_name=product["Naimenovanie"],
        category=product["Kategoriya"],
        quantity=i,  # 1, 2, 3...
        unit=unit,
        price=500 + (i * 100),  # 600, 700, 800...
        product_url=product["Ssylka"],
        notes=f"Fasovki: {', '.join(product['Fasovki'])}"
    )
    
    order.add_item(item)

# Завершаем заявку
order.calculate_total()
order.status = "draft"

print(f"Создана заявка {order.order_id} с {order.get_total_items()} товарами")
print(f"Итого: {order.total_sum:.2f} руб.")
```

### 4. Сохранение заявки

```python
from utils.order_manager import OrderManager

manager = OrderManager()
manager.save_order(order)

# Сохраняется в orders_storage/{order_id}.json
```

### 5. Экспорт заявки

```python
from export.email_formatter import EmailFormatter

formatter = EmailFormatter()

# Экспорт во все форматы
files = formatter.export_to_files(order, './exports')

# Результат:
# {
#     'text': 'exports/ORD-001.txt',
#     'csv': 'exports/ORD-001.csv',
#     'html': 'exports/ORD-001.html',
# }
```

### 6. Отправка по Email

```python
formatter = EmailFormatter(
    smtp_host='smtp.gmail.com',
    smtp_port=587,
    sender_email='your@gmail.com',
    sender_password='app_password'
)

formatter.send_email(order)
```

---

## Полный пример скрипта

```python
"""
Полный пример: Парсинг каталога → Создание заявки → Экспорт
"""

from datetime import datetime
from parsers.catalog_parser import parse_catalog
from orders.order import Order, OrderItem
from export.email_formatter import EmailFormatter
from utils.order_manager import OrderManager


def create_order_from_catalog():
    """Создает заявку из товаров каталога."""
    
    print("Этап 1: Парсинг каталога витекс.про...")
    
    # Парсим каталог
    products = parse_catalog([
        "https://vitex.pro/catalog/oils/",
    ])
    
    if not products:
        print("Ошибка: товары не найдены!")
        return
    
    print(f"Получено товаров: {len(products)}")
    
    # Создаем заявку
    print("\nЭтап 2: Создание заявки...")
    
    order = Order(
        order_id="ORD-" + datetime.now().strftime("%Y%m%d-%H%M"),
        customer_name="ООО ТехСервис",
        customer_email="zakupki@techservice.ru",
    )
    
    # Добавляем товары
    for i, product in enumerate(products[:5], 1):
        
        unit = "sht"
        if product.get("Fasovki"):
            first_package = product["Fasovki"][0]
            if " " in first_package:
                _, unit = first_package.rsplit(" ", 1)
        
        item = OrderItem(
            product_name=product["Naimenovanie"],
            category=product["Kategoriya"],
            quantity=i,
            unit=unit,
            price=500 + (i * 100),
            product_url=product["Ssylka"],
            notes=f"Fasovki: {', '.join(product['Fasovki'][:3])}"
        )
        
        order.add_item(item)
    
    order.calculate_total()
    
    print(f"Создана заявка {order.order_id}")
    print(f"Позиций: {order.get_total_items()}")
    print(f"Сумма: {order.total_sum:.2f} руб.")
    
    # Сохраняем
    print("\nЭтап 3: Сохранение заявки...")
    
    manager = OrderManager()
    manager.save_order(order)
    
    # Экспортируем
    print("\nЭтап 4: Экспорт...")
    
    formatter = EmailFormatter()
    files = formatter.export_to_files(order)
    
    print("\nГотово! Файлы сохранены:")
    for fmt, path in files.items():
        print(f"  - {fmt.upper()}: {path}")


if __name__ == "__main__":
    create_order_from_catalog()
```

---

## Структура данных из парсера

Каждый товар из парсера содержит:

```python
{
    "Naimenovanie": "Масло моторное 5W-30",           # Русское название
    "Kategoriya": "Моторные масла",                  # Категория
    "Naimenovanie EN": "Synthetic Motor Oil 5W-30",  # Английское название
    "Opisanie": "Синтетическое масло...",            # Описание
    "Fasovki": ["0.75 l", "1 l", "5 l"],            # Доступные объемы
    "Ssylka": "https://vitex.pro/catalog/oils/..."   # URL товара
}
```

---

## Поиск товаров после сохранения

```python
from utils.order_manager import OrderManager

manager = OrderManager()

# Поиск по названию товара
results = manager.search_orders(query="масло")

# Поиск по статусу
drafts = manager.search_orders(status="draft")

# Список всех заявок
all_orders = manager.list_orders()
```

---

## Примеры скриптов

### parser_demo_fast.py
- Быстрый пример с демо-данными (не требует интернета)
- Показывает полный цикл: парсинг → заявка → экспорт
- **Запуск:** `python parser_demo_fast.py`

### parser_integration_example.py
- Полный пример с реальным парсингом vitex.pro
- Может занять 1-2 минуты на парсинг
- **Запуск:** `python parser_integration_example.py`

### example_usage.py
- Базовый пример системы заявок (без парсера)
- Создание вручную
- **Запуск:** `python example_usage.py`

---

## Частые ошибки

### 1. UnicodeEncodeError

**Проблема:** Ошибка при выводе Unicode символов на Windows

**Решение:** Используйте простые ASCII символы или добавьте:
```python
import sys
sys.stdout.reconfigure(encoding='utf-8')
```

### 2. Парсер не находит товары

**Проблема:** `parse_catalog()` возвращает пустой список

**Решение:**
- Проверьте интернет соединение
- Убедитесь что URL раздела правильный
- Проверьте доступность vitex.pro в браузере
- Увеличьте REQUEST_TIMEOUT в parsers/config.py

### 3. Товары создаются с одинаковой ценой

**Решение:** Подставьте реальные цены с сайта или используйте API витекс (если доступен)

---

## Интеграция с вашей системой

### Вариант 1: CLI утилита

```python
# cli_tool.py
import sys
from parsers.catalog_parser import parse_catalog
from orders.order import Order, OrderItem

if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1]
        products = parse_catalog([url])
        print(f"Найдено товаров: {len(products)}")
```

**Запуск:** `python cli_tool.py "https://vitex.pro/catalog/oils/"`

### Вариант 2: Flask приложение

```python
# web_app.py
from flask import Flask, request, jsonify
from parsers.catalog_parser import parse_catalog
from orders.order import Order

app = Flask(__name__)

@app.route('/api/parse', methods=['POST'])
def parse_endpoint():
    data = request.json
    catalog = parse_catalog(data.get('sections', []))
    return jsonify({"products": catalog, "count": len(catalog)})

@app.route('/api/order', methods=['POST'])
def create_order():
    data = request.json
    # Создание заявки...
    return jsonify({"status": "created"})
```

### Вариант 3: Scheduler для автопарсинга

```python
# scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from parsers.catalog_parser import parse_catalog

def update_catalog():
    products = parse_catalog()
    # Сохранить в БД или файл...
    print(f"Updated: {len(products)} products")

scheduler = BackgroundScheduler()
scheduler.add_job(update_catalog, 'interval', hours=1)
scheduler.start()
```

---

## Производительность

### Время парсинга (примерно)

| Раздел | Товаров | Время |
|--------|---------|-------|
| 1 раздел (масла) | 20-30 | 2-3 мин |
| 2 раздела | 50-60 | 5-6 мин |
| Весь каталог | 200+ | 15-20 мин |

### Оптимизация

1. **Параллельный парсинг** - используйте `concurrent.futures`
2. **Кеширование** - сохраняйте товары в БД
3. **Incremental update** - парсьте только новые товары
4. **API вместо парсинга** - запросите API витекс

---

Готово! Система полностью интегрирована и работает. 🎯
