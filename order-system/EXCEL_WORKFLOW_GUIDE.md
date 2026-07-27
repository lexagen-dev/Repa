## СИСТЕМА ЗАЯВОК ДЛЯ ЛАКОКРАСОЧНЫХ МАТЕРИАЛОВ

Полная система создания и управления заявками на лакокрасочные материалы с интеграцией парсера и Excel.

---

## 🎯 Основной цикл работы

```
1. ПАРСИНГ КАТАЛОГА
   ↓
2. ЭКСПОРТ В EXCEL
   ↓
3. ЗАПОЛНЕНИЕ КОЛИЧЕСТВ (пользователем в Excel)
   ↓
4. СОЗДАНИЕ ЗАЯВКИ
   ↓
5. ГЕНЕРАЦИЯ ПИСЬМА
   ↓
6. ОТПРАВКА ПО EMAIL
```

---

## 📋 Структура данных

### Из парсера (для КАЖДОЙ ФАСОВКИ отдельная позиция):

```python
{
    "Kategoriya": "Краски акриловые",
    "Naimenovanie RU": "Краска белая акриловая",
    "Naimenovanie EN": "White Acrylic Paint",
    "Opisanie": "Белая акриловая краска для внутренних работ...",
    "Fasovka": "0.5 l",           # КАЖДАЯ фасовка = отдельная позиция!
    "Ssylka": "https://vitex.pro/...",
}
```

**Важно:** Если товар имеет 3 фасовки (0.5л, 1л, 5л), то в каталоге будет 3 позиции!

### В Excel:

| Номер | Русское Наименование | Английское Наименование | Категория | Фасовка | Описание | Количество | URL |
|-------|---------------------|------------------------|-----------|---------|---------|------------|-----|
| 1 | Краска белая акриловая | White Acrylic Paint | Краски | 0.5 l | Белая краска... | **[заполнить]** | ... |
| 2 | Краска белая акриловая | White Acrylic Paint | Краски | 1 l | Белая краска... | **[заполнить]** | ... |
| 3 | Краска белая акриловая | White Acrylic Paint | Краски | 5 l | Белая краска... | **[заполнить]** | ... |

---

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Запуск основного примера

```bash
python excel_workflow_example.py
```

Этот скрипт демонстрирует полный цикл:
- Создает демо-каталог лакокрасочных материалов
- Экспортирует в Excel
- Заполняет количества
- Создает заявку
- Генерирует письмо

### 3. Результаты

После запуска создаются файлы:
- `lakokrasochnyе_tovarу.xlsx` - каталог в Excel
- `exports/ORD-*.txt` - письмо (текст)
- `exports/ORD-*.csv` - письмо (таблица)
- `exports/ORD-*.html` - письмо (красивое для email)
- `orders_storage/ORD-*.json` - сохраненная заявка

---

## 💻 Использование в коде

### Шаг 1: Парсинг каталога

```python
from parsers.catalog_parser_v2 import parse_catalog

# Парсим каталог витекс.про
catalog = parse_catalog([
    "https://vitex.pro/catalog/paints/",
    "https://vitex.pro/catalog/varnishes/",
])

# Результат: список позиций
# Для каждой фасовки - отдельная позиция!
print(f"Позиций в каталоге: {len(catalog)}")

# Пример позиции:
# {
#     "Kategoriya": "Краски",
#     "Naimenovanie RU": "Краска белая",
#     "Naimenovanie EN": "White Paint",
#     "Opisanie": "...",
#     "Fasovka": "0.5 l",
#     "Ssylka": "https://..."
# }
```

### Шаг 2: Экспорт в Excel

```python
from export.catalog_manager import CatalogExcelManager

manager = CatalogExcelManager()

# Экспортируем каталог
manager.export_catalog_to_excel(
    catalog,
    output_file="my_catalog.xlsx"
)
```

Пользователь открывает файл и заполняет колону "Количество".

### Шаг 3: Создание заявки из Excel

```python
# После того как пользователь заполнил Excel...

order = manager.create_order_from_excel(
    "my_catalog.xlsx",
    customer_name="ООО ТехСервис",
    customer_email="zakupki@techservice.ru"
)

# Автоматически:
# - Учитываются только позиции с количеством > 0
# - Создается заявка
# - Рассчитывается сумма
```

### Шаг 4: Сохранение и экспорт

```python
from utils.order_manager import OrderManager
from export.email_formatter import EmailFormatter

# Сохраняем заявку
manager = OrderManager()
manager.save_order(order)

# Экспортируем в разные форматы
formatter = EmailFormatter()
files = formatter.export_to_files(order)

# Создаются:
# - exports/ORD-*.txt - текст
# - exports/ORD-*.csv - таблица
# - exports/ORD-*.html - HTML для email
```

### Шаг 5: Отправка по Email

```python
formatter = EmailFormatter(
    smtp_host='smtp.gmail.com',
    smtp_port=587,
    sender_email='your@gmail.com',
    sender_password='app_specific_password'
)

formatter.send_email(order)
# Письмо отправляется в email заказчика
```

---

## 📊 Пример полного скрипта

```python
from parsers.catalog_parser_v2 import parse_catalog
from export.catalog_manager import CatalogExcelManager
from export.email_formatter import EmailFormatter
from utils.order_manager import OrderManager

# 1. Парсим каталог
print("Парсим каталог...")
catalog = parse_catalog(["https://vitex.pro/catalog/paints/"])

# 2. Экспортируем в Excel
print("Экспортируем в Excel...")
manager = CatalogExcelManager()
manager.export_catalog_to_excel(catalog, "catalog.xlsx")

print("\nОтредактируйте 'catalog.xlsx' и заполните колону 'Количество'")
input("Нажмите Enter когда готово...")

# 3. Создаем заявку из Excel
print("Создаем заявку...")
order = manager.create_order_from_excel(
    "catalog.xlsx",
    customer_name="ООО Мой магазин",
    customer_email="info@shop.ru"
)

# 4. Сохраняем
print("Сохраняем заявку...")
om = OrderManager()
om.save_order(order)

# 5. Экспортируем
print("Экспортируем в форматы...")
formatter = EmailFormatter()
formatter.export_to_files(order)

# 6. Отправляем (если настроено SMTP)
# formatter.send_email(order)

print("Готово!")
```

---

## 🔑 Ключевые функции

### CatalogExcelManager

```python
manager = CatalogExcelManager()

# Экспорт каталога в Excel
manager.export_catalog_to_excel(catalog, "output.xlsx")

# Загрузка позиций с количествами
positions = manager.load_catalog_with_quantities("input.xlsx")

# Создание заявки из Excel
order = manager.create_order_from_excel("input.xlsx")
```

### parse_catalog (v2)

```python
# Парсит каталог витекс.про
catalog = parse_catalog(section_urls)

# ВАЖНО: Возвращает позицию для КАЖДОЙ ФАСОВКИ!
# Если товар имеет 3 фасовки, вернет 3 позиции
```

---

## 📁 Новые файлы

| Файл | Описание |
|------|---------|
| `parsers/catalog_parser_v2.py` | Модифицированный парсер (позиция на фасовку) |
| `export/catalog_manager.py` | Управление Excel каталогом |
| `excel_workflow_example.py` | Полный пример работы с Excel |
| `requirements.txt` | Обновлен (добавлен openpyxl) |

---

## 🎨 Структура Excel файла

### Заголовки колон:

1. **Номер** - ID позиции (автоматический)
2. **Русское Наименование** - Название товара на русском
3. **Английское Наименование** - Название товара на английском
4. **Категория** - Категория товара (Краски, Лак, Грунтовка и т.д.)
5. **Фасовка** - Объем/размер (0.5l, 1l, 5l и т.д.)
6. **Описание** - Краткое описание (первые 50 символов)
7. **Количество** - ⭐ **ЗАПОЛНЯЕТСЯ ПОЛЬЗОВАТЕЛЕМ**
8. **URL** - Ссылка на товар на сайте

### Процесс заполнения:

1. Пользователь открывает файл в Excel
2. Видит полный каталог со всеми фасовками
3. В колоне "Количество" вводит нужные значения
4. Оставляет 0 или пусто для ненужных позиций
5. Сохраняет файл

### Результат после сохранения:

- Функция `create_order_from_excel()` читает файл
- Берет только позиции где Количество > 0
- Создает заявку с этими товарами
- Генерирует письмо только для выбранных товаров

---

## 🔄 Пример письма

```
======================================================================
ЗАЯВКА НА ПРОДУКЦИЮ
======================================================================
Номер заявки: ORD-20260726-154230
Дата создания: 26.07.2026 15:42:30
Статус: draft

ДАННЫЕ ЗАКАЗЧИКА:
  Имя: ООО ТехСервис
  Email: zakupki@techservice.ru

ПОЗИЦИИ ЗАЯВКИ:
----------------------------------------------------------------------

1. Краска белая акриловая
   Категория: Краски акриловые
   Количество: 2 0.5 l
   Цена за единицу: 1000.00 руб.
   Сумма: 2000.00 руб.
   EN: White Acrylic Paint

2. Краска белая акриловая
   Категория: Краски акриловые
   Количество: 5 1 l
   Цена за единицу: 1000.00 руб.
   Сумма: 5000.00 руб.
   EN: White Acrylic Paint

3. Грунтовка акриловая
   Категория: Грунтовки
   Количество: 1 1 l
   Цена за единицу: 1000.00 руб.
   Сумма: 1000.00 руб.
   EN: Acrylic Primer

----------------------------------------------------------------------
Итого позиций: 3
ИТОГО СУММА: 8000.00 руб.
======================================================================
```

---

## ⚙️ Конфигурация

### Для SMTP (отправка email):

Откройте `export/email_formatter.py` и настройте:

```python
formatter = EmailFormatter(
    smtp_host='smtp.gmail.com',        # SMTP сервер
    smtp_port=587,                      # Порт
    sender_email='your@gmail.com',      # Email отправителя
    sender_password='app_password'      # App password (Google)
)
```

**Для Gmail:**
1. Включите 2FA
2. Создайте App Password: https://myaccount.google.com/apppasswords
3. Используйте 16-символьный пароль

---

## 💡 Идеи для расширения

1. **Веб-интерфейс** - Flask/Streamlit для работы без Excel
2. **Интеграция с CRM** - Bitrix24, 1C, Salesforce
3. **Автопарсинг** - Каждый день парсит новый каталог
4. **Цены из каталога** - Парсит и добавляет актуальные цены
5. **История заказов** - Сохраняет все заявки в БД
6. **Уведомления** - Telegram/Slack оповещения
7. **PDF счета** - Генерирует красивые PDF документы

---

## 📞 Типичные задачи

### Создать заявку вручную

```python
from orders.order import Order, OrderItem

order = Order(
    order_id="ORD-001",
    customer_name="ООО Компания",
    customer_email="email@company.ru",
)

order.add_item(OrderItem(
    product_name="Краска белая",
    category="Краски",
    quantity=2,
    unit="0.5 l",
    price=1000,
))

order.calculate_total()
```

### Найти заявки

```python
from utils.order_manager import OrderManager

manager = OrderManager()

# Поиск по названию товара
results = manager.search_orders(query="краска")

# Все заявки
all_orders = manager.list_orders()

# Загрузить конкретную
order = manager.load_order("ORD-001.json")
```

### Отправить письмо

```python
from export.text_formatter import format_order_as_text

text = format_order_as_text(order)

# Копируйте в письмо и отправьте
print(text)
```

---

## 🐛 Решение проблем

### UnicodeEncodeError на Windows

**Решение:** Используйте простые ASCII символы или добавьте:
```python
import sys
sys.stdout.reconfigure(encoding='utf-8')
```

### openpyxl не установлен

```bash
pip install openpyxl>=3.9.0
```

### Excel файл не открывается

- Проверьте что используете .xlsx формат
- Не переименовывайте файлы во время работы программы
- Закройте файл в Excel перед загрузкой в программу

---

## 🎯 Следующие шаги

1. ✅ Запустите `excel_workflow_example.py`
2. ✅ Отредактируйте `lakokrasochnyе_tovarу.xlsx`
3. ✅ Посмотрите созданное письмо
4. 🔄 Интегрируйте с вашей системой
5. 📧 Настройте отправку по email

Готово! Система полностью функциональна. 🎉
