# Система управления заявками на продукцию

Полнофункциональная система для создания, управления и экспорта заявок на продукцию с интеграцией парсера каталога, форматированием для email и поддержкой различных форматов экспорта.

## 🎯 Возможности

- ✅ **Создание заявок** - управление позициями и данными заказчика
- ✅ **Парсинг каталога** - интеграция с существующим парсером vitex.pro
- ✅ **Экспорт в форматы**:
  - Текстовый формат (.txt)
  - HTML таблица для email
  - CSV для таблиц
- ✅ **Отправка по email** - с поддержкой SMTP
- ✅ **Управление заявками** - сохранение, загрузка, поиск в JSON

## 📁 Структура проекта

```
order-system/
├── parsers/              # Парсеры каталогов
│   ├── __init__.py
│   └── catalog_parser.py # Интегрировать парсер vitex отсюда
├── orders/               # Модели заявок
│   ├── __init__.py
│   └── order.py          # Классы Order и OrderItem
├── export/               # Форматирование и экспорт
│   ├── __init__.py
│   ├── text_formatter.py    # Текстовый формат
│   ├── table_formatter.py   # HTML и CSV таблицы
│   └── email_formatter.py   # Отправка по email
├── utils/                # Утилиты
│   ├── __init__.py
│   └── order_manager.py  # Управление заявками
├── example_usage.py      # Пример использования
├── requirements.txt      # Зависимости
└── README.md            # Документация
```

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Интеграция парсера

Скопируйте ваш парсер из `C:\Users\Николай\PycharmProjects\PythonProject\Vitex\vitex\parser.py` в `parsers/catalog_parser.py`:

```python
# parsers/catalog_parser.py
# Вставьте содержимое вашего parser.py сюда
```

### 3. Запуск примера

```bash
python example_usage.py
```

## 📝 Основное использование

### Создание заявки

```python
from orders.order import Order, OrderItem

order = Order(
    order_id="ORD-2024-001",
    customer_name="Иван Петров",
    customer_email="ivan@example.com",
)

order.add_item(OrderItem(
    product_name="Автомасло",
    category="Масла",
    quantity=10,
    unit="л",
    price=250.0,
    product_url="https://vitex.pro/catalog/.../",
))

order.calculate_total()
```

### Экспорт в разные форматы

```python
from export.email_formatter import EmailFormatter

formatter = EmailFormatter()
files = formatter.export_to_files(order, './exports')
# Создает: exports/ORD-2024-001.txt
#          exports/ORD-2024-001.html
#          exports/ORD-2024-001.csv
```

### Текстовый формат

```python
from export.text_formatter import format_order_as_text

text = format_order_as_text(order)
print(text)
```

**Вывод:**
```
======================================================================
ЗАЯВКА НА ПРОДУКЦИЮ
======================================================================
Номер заявки: ORD-2024-001
Дата создания: 26.07.2024 15:30:45
Статус: sent

ДАННЫЕ ЗАКАЗЧИКА:
  Имя: Иван Петров
  Email: ivan@example.com

ПОЗИЦИИ ЗАЯВКИ:
----------------------------------------------------------------------
1. Автомасло
   Категория: Масла
   Количество: 10 л
   Цена за единицу: 250.00 руб.
   Сумма: 2500.00 руб.
...
```

### HTML таблица для email

```python
from export.table_formatter import format_order_as_html_table

html = format_order_as_html_table(order)
# Готовая HTML таблица с стилями для красивого отображения
```

### Отправка по email

```python
from export.email_formatter import EmailFormatter

formatter = EmailFormatter(
    smtp_host='smtp.gmail.com',
    smtp_port=587,
    sender_email='your@gmail.com',
    sender_password='app_specific_password'  # Генерируется в аккаунте Google
)

formatter.send_email(order, format_type='html')
```

### Управление заявками

```python
from utils.order_manager import OrderManager

manager = OrderManager()

# Сохранение
manager.save_order(order)

# Загрузка
loaded_order = manager.load_order("ORD-2024-001.json")

# Список всех заявок
all_orders = manager.list_orders()

# Поиск
results = manager.search_orders(query="масло", status="sent")

# Удаление
manager.delete_order("ORD-2024-001.json")
```

## 📧 Настройка отправки email

### Gmail

1. Включите 2FA в аккаунте Google
2. Создайте App Password: https://myaccount.google.com/apppasswords
3. Используйте его вместо пароля:

```python
formatter = EmailFormatter(
    smtp_host='smtp.gmail.com',
    smtp_port=587,
    sender_email='your@gmail.com',
    sender_password='xxxx xxxx xxxx xxxx'
)
```

### Yandex Mail

```python
formatter = EmailFormatter(
    smtp_host='smtp.yandex.ru',
    smtp_port=587,
    sender_email='your@yandex.ru',
    sender_password='your_password'
)
```

### Собственный SMTP сервер

```python
formatter = EmailFormatter(
    smtp_host='mail.example.com',
    smtp_port=587,
    sender_email='no-reply@example.com',
    sender_password='password'
)
```

## 🔍 Интеграция парсера

Ваш парсер можно использовать для автоматического извлечения информации о товарах:

```python
from parsers.catalog_parser import (
    fetch_soup,
    get_product_name,
    get_description,
    collect_product_links,
)
from orders.order import Order, OrderItem

# Получение ссылок на товары из категории
product_urls = collect_product_links(
    "https://vitex.pro/catalog/oils/",
    section_urls=set()
)

# Создание заявки с товарами из каталога
for url in product_urls[:5]:  # Первые 5 товаров
    soup = fetch_soup(url)
    
    item = OrderItem(
        product_name=get_product_name(soup),
        category="Масла",
        quantity=1,
        unit="л",
        product_url=url,
    )
    
    order.add_item(item)
```

## 💾 Форматы сохранения

### JSON (по умолчанию)

```json
{
  "order_id": "ORD-2024-001",
  "customer_name": "Иван Петров",
  "customer_email": "ivan@example.com",
  "created_at": "2024-07-26T15:30:45.123456",
  "items": [
    {
      "product_name": "Автомасло",
      "category": "Масла",
      "quantity": 10,
      "unit": "л",
      "price": 250.0,
      "product_url": "https://vitex.pro/...",
      "notes": null
    }
  ],
  "status": "sent",
  "notes": "Доставить...",
  "total_sum": 2500.0
}
```

### Экспортируемые форматы

- **TXT** - для просмотра и архивирования
- **HTML** - для отправки красивых email
- **CSV** - для импорта в Excel и другие таблицы

## 🛠️ Идеи для расширения

1. **Веб-интерфейс** - Flask/FastAPI приложение для создания заявок через UI
2. **Парсинг цен** - автоматическое получение актуальных цен из каталога
3. **Интеграция с БД** - PostgreSQL/SQLite вместо JSON
4. **Уведомления** - Telegram/Slack оповещения при создании заявок
5. **Шаблоны email** - кастомные HTML шаблоны с логотипом
6. **Подписи** - электронные подписи и PDF
7. **Статистика** - аналитика по заявкам (тренды, популярные товары)
8. **Интеграция с CRM** - ExcelCRM, BitrixCRM
9. **REST API** - для третьих приложений
10. **Автоматическая переотправка** - напоминания при неподтвержденных заявках

## 📋 Методы класса Order

| Метод | Описание |
|-------|---------|
| `add_item(item)` | Добавить товар в заявку |
| `remove_item(index)` | Удалить товар по индексу |
| `get_total_items()` | Количество товаров |
| `calculate_total()` | Рассчитать сумму |
| `to_dict()` | Преобразование в словарь |

## 📋 Методы класса OrderManager

| Метод | Описание |
|-------|---------|
| `save_order(order)` | Сохранить заявку |
| `load_order(filename)` | Загрузить заявку |
| `list_orders()` | Список всех заявок |
| `delete_order(filename)` | Удалить заявку |
| `search_orders(query, status)` | Поиск по критериям |

## 📋 Методы класса EmailFormatter

| Метод | Описание |
|-------|---------|
| `create_message()` | Создать email сообщение |
| `send_email()` | Отправить заявку |
| `export_to_files()` | Экспортировать в файлы |

## ⚙️ Требования

- Python 3.8+
- requests
- beautifulsoup4
- python-dotenv (опционально)

## 📞 Поддержка

Для вопросов по интеграции парсера создайте issue в проекте.

## 📄 Лицензия

MIT
