# 🎉 СИСТЕМА ЗАЯВОК ЛАКОКРАСОЧНЫХ МАТЕРИАЛОВ — ПОЛНОСТЬЮ РЕАЛИЗОВАНА

## ✅ Статус: PRODUCTION-READY

Система полностью разработана, протестирована и готова к использованию. Все требования пользователя реализованы.

---

## 📋 Реализованные требования

| Требование | Статус | Реализация |
|-----------|--------|-----------|
| Парсинг витекс.про (название EN, описание RU, фасовки) | ✅ | `parsers/catalog_parser_v2.py` |
| Отдельная позиция для КАЖДОЙ фасовки | ✅ | `parse_product()` возвращает list |
| Excel интерфейс для работы с каталогом | ✅ | `export/catalog_manager.py` |
| Пользователь заполняет количества в Excel | ✅ | Колона G "Количество" |
| Автогенерация заявки с позициями > 0 | ✅ | `create_order_from_excel()` |
| Генерация письма/заявки | ✅ | `export/email_formatter.py` |
| Сохранение заявок | ✅ | `utils/order_manager.py` (JSON) |
| Экспорт в разные форматы | ✅ | TXT, CSV, HTML, XLSX |
| Отправка по Email | ✅ | `EmailFormatter` с SMTP |

---

## 🏗️ Архитектура системы

```
order-system/
├── parsers/                      # Парсинг каталога
│   ├── catalog_parser_v2.py     # ✅ НОВОЕ: Парсер (позиция на фасовку)
│   ├── catalog_parser.py        # Базовый парсер
│   └── config.py                # Конфигурация
│
├── export/                       # Экспорт и форматирование
│   ├── catalog_manager.py       # ✅ НОВОЕ: Excel управление
│   ├── email_formatter.py       # Отправка email
│   ├── text_formatter.py        # Текстовый формат
│   └── table_formatter.py       # Таблицы (CSV, HTML)
│
├── orders/                       # Модели данных
│   └── order.py                 # Order, OrderItem классы
│
├── utils/                        # Утилиты
│   └── order_manager.py         # JSON хранилище
│
├── excel_workflow_example.py    # ✅ НОВОЕ: Полный пример
├── EXCEL_WORKFLOW_GUIDE.md      # ✅ НОВОЕ: Подробное руководство
└── requirements.txt             # Зависимости
```

---

## 🚀 Три способа использования

### 1️⃣ БЫСТРЫЙ СТАРТ (Demo режим)

```bash
python excel_workflow_example.py
```

**Что происходит:**
1. Создает демо-каталог (10 товаров с разными фасовками)
2. Экспортирует в `lakokrasochnyе_tovarу.xlsx`
3. Заполняет количества (автоматически)
4. Создает заявку
5. Генерирует письмо в `exports/`

**Результаты:**
- `lakokrasochnyе_tovarу.xlsx` - каталог в Excel
- `exports/ORD-*.html` - письмо красивое
- `orders_storage/ORD-*.json` - сохраненная заявка

---

### 2️⃣ РАБОТА С РЕАЛЬНЫМ КАТАЛОГОМ

```python
from parsers.catalog_parser_v2 import parse_catalog
from export.catalog_manager import CatalogExcelManager

# Парсим витекс.про
catalog = parse_catalog([
    "https://vitex.pro/catalog/paints/",
    "https://vitex.pro/catalog/varnishes/",
])

# Экспортируем в Excel
manager = CatalogExcelManager()
manager.export_catalog_to_excel(catalog, "my_catalog.xlsx")

print("Откройте my_catalog.xlsx и заполните количества")
# Пользователь редактирует Excel...

# Создаем заявку
order = manager.create_order_from_excel(
    "my_catalog.xlsx",
    customer_name="ООО Компания",
    customer_email="email@company.ru"
)
```

---

### 3️⃣ ИНТЕГРАЦИЯ В СВОЮ СИСТЕМУ

```python
from export.catalog_manager import CatalogExcelManager
from export.email_formatter import EmailFormatter

# Ваш каталог
your_catalog = [
    {
        "Kategoriya": "Краски",
        "Naimenovanie RU": "Краска белая",
        "Naimenovanie EN": "White Paint",
        "Opisanie": "Белая краска",
        "Fasovka": "1 l",
        "Ssylka": "https://example.com/paint"
    },
    # ... еще товары
]

# Экспортируем
manager = CatalogExcelManager()
manager.export_catalog_to_excel(your_catalog, "catalog.xlsx")

# Создаем заявку из заполненного Excel
order = manager.create_order_from_excel("catalog.xlsx")

# Отправляем
formatter = EmailFormatter()
formatter.send_email(order)
```

---

## 📊 Структура данных

### Позиция в каталоге

```python
{
    "Kategoriya": "Краски акриловые",
    "Naimenovanie RU": "Краска белая акриловая",
    "Naimenovanie EN": "White Acrylic Paint",
    "Opisanie": "Белая аккриловая краска для внутренних работ...",
    "Fasovka": "0.5 l",              # КАЖДАЯ фасовка = отдельная позиция!
    "Ssylka": "https://vitex.pro/.../",
}
```

**ВАЖНО:** Один товар = несколько позиций (по числу фасовок!)

Пример:
- Товар: "Краска белая"
- Фасовки: 0.5l, 1l, 5l, 10l
- Позиций в каталоге: **4 штуки!**

---

## 💾 Процесс создания заявки

```
ЭТАП 1: Парсинг
  ↓
  parse_catalog(["https://vitex.pro/..."])
  ↓
  catalog = [
      {Fasovka: "0.5l", ...},
      {Fasovka: "1l", ...},
      {Fasovka: "5l", ...},
      ...
  ]
  
ЭТАП 2: Excel экспорт
  ↓
  export_catalog_to_excel(catalog, "file.xlsx")
  ↓
  Пользователь открывает Excel и заполняет "Количество"
  
ЭТАП 3: Создание заявки
  ↓
  create_order_from_excel("file.xlsx")
  ↓
  Берет ТОЛЬКО позиции где Количество > 0
  Создает Order с этими товарами
  
ЭТАП 4: Генерация письма
  ↓
  export_to_files(order) → TXT, CSV, HTML, JSON
  
ЭТАП 5: Отправка (опционально)
  ↓
  send_email(order)
```

---

## 📁 Структура Excel файла

### Колоны:

| # | Наименование | Описание | Примеры |
|---|--------------|---------|---------|
| A | Номер | ID позиции (автоматический) | 1, 2, 3, ... |
| B | Русское Наименование | Название товара RU | Краска белая |
| C | Английское Наименование | Название товара EN | White Paint |
| D | Категория | Категория товара | Краски |
| E | Фасовка | Размер/объем | 0.5 l, 1 l |
| F | Описание | Первые 50 символов | Белая краска для... |
| G | **Количество** | ⭐ ЗАПОЛНЯЕТ ПОЛЬЗОВАТЕЛЬ | 5, 0, 10, ... |
| H | URL | Ссылка на товар | https://vitex.pro/... |

### Заполнение:

```
Русское Наименование: Краска белая акриловая
Английское Наименование: White Acrylic Paint
Категория: Краски акриловые
Фасовка: 0.5 l
Количество: [ПОЛЬЗОВАТЕЛЬ ВВОДИТ ЗДЕСЬ] → 5

Фасовка: 1 l
Количество: [ПОЛЬЗОВАТЕЛЬ ВВОДИТ ЗДЕСЬ] → 10

Фасовка: 5 l
Количество: [ПОЛЬЗОВАТЕЛЬ ВВОДИТ ЗДЕСЬ] → 0  (не нужно)
```

---

## 🔑 Ключевые API

### CatalogExcelManager

```python
manager = CatalogExcelManager()

# Экспорт в Excel
manager.export_catalog_to_excel(
    catalog,                    # list[dict]
    output_file="catalog.xlsx"  # путь для сохранения
)

# Загрузка каталога с количествами
positions = manager.load_catalog_with_quantities(
    "catalog.xlsx"  # путь к заполненному файлу
)
# Возвращает: list[dict] с заполненной колоной Количество

# Создание заявки из Excel
order = manager.create_order_from_excel(
    excel_file="catalog.xlsx",
    customer_name="ООО Компания",
    customer_email="email@company.ru"
)
# Возвращает: Order объект с только позициями где qty > 0
```

### Парсер (v2)

```python
from parsers.catalog_parser_v2 import parse_catalog

# Парсит каталог
catalog = parse_catalog(
    section_urls=[
        "https://vitex.pro/catalog/paints/",
        "https://vitex.pro/catalog/varnishes/",
    ]
)

# Возвращает: list[dict]
# ВАЖНО: Одна позиция для КАЖДОЙ фасовки!
```

### Order & OrderItem

```python
from orders.order import Order, OrderItem

# Создание
order = Order(
    order_id="ORD-001",
    customer_name="ООО Компания",
    customer_email="email@company.ru"
)

# Добавление товара
order.add_item(OrderItem(
    product_name="Краска белая",
    category="Краски",
    quantity=5,
    unit="0.5 l",
    price=1000,
    product_url="https://...",
))

# Расчет
order.calculate_total()
print(f"Итого: {order.total_sum} руб.")
```

---

## 📨 Отправка по Email

```python
from export.email_formatter import EmailFormatter

formatter = EmailFormatter(
    smtp_host='smtp.gmail.com',
    smtp_port=587,
    sender_email='your@gmail.com',
    sender_password='app_specific_password'  # Google App Password
)

# Отправка
formatter.send_email(order)

# Экспорт (без отправки)
files = formatter.export_to_files(order)
print(files)  # ['exports/ORD-*.txt', 'exports/ORD-*.csv', ...]
```

---

## 🛠️ Установка зависимостей

```bash
# Установить все зависимости
pip install -r requirements.txt

# Или отдельно:
pip install requests          # Парсинг
pip install beautifulsoup4    # HTML парсинг
pip install openpyxl>=3.9.0   # Excel работа
```

---

## 📂 Файлы в проекте

### Новые файлы (в этой сессии)

| Файл | Описание | Строк |
|------|---------|-------|
| `parsers/catalog_parser_v2.py` | Модифицированный парсер (позиция на фасовку) | 320+ |
| `export/catalog_manager.py` | CatalogExcelManager для Excel работы | 350+ |
| `excel_workflow_example.py` | Полный пример Excel workflow | 350+ |
| `EXCEL_WORKFLOW_GUIDE.md` | Руководство по Excel системе | ~500 |

### Существующие файлы

| Файл | Описание |
|------|---------|
| `orders/order.py` | Order, OrderItem классы |
| `export/email_formatter.py` | Отправка по email |
| `export/text_formatter.py` | Текстовый формат |
| `export/table_formatter.py` | CSV, HTML форматы |
| `utils/order_manager.py` | JSON хранилище |
| `parsers/catalog_parser.py` | Базовый парсер |

---

## 🎯 Примеры использования

### Пример 1: Полный цикл с Excel

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Полный цикл: Парсинг -> Excel -> Заявка -> Письмо"""

from parsers.catalog_parser_v2 import parse_catalog
from export.catalog_manager import CatalogExcelManager
from export.email_formatter import EmailFormatter
from utils.order_manager import OrderManager

# 1. Парсим каталог
catalog = parse_catalog(["https://vitex.pro/catalog/paints/"])
print(f"Позиций: {len(catalog)}")

# 2. Экспортируем в Excel
manager = CatalogExcelManager()
manager.export_catalog_to_excel(catalog, "catalog.xlsx")
print("Экспортировано в catalog.xlsx")

# 3. (Пользователь заполняет Excel...)

# 4. Создаем заявку
order = manager.create_order_from_excel(
    "catalog.xlsx",
    customer_name="ООО Мой магазин",
    customer_email="info@shop.ru"
)
print(f"Заявка создана: {order.order_id}")

# 5. Сохраняем
om = OrderManager()
om.save_order(order)

# 6. Экспортируем
formatter = EmailFormatter()
files = formatter.export_to_files(order)
print(f"Экспортировано: {files}")

# 7. (Отправляем по email если нужно)
```

### Пример 2: Работа с демо-данными

```python
from export.catalog_manager import CatalogExcelManager

# Создаем Excel с демо-данными
manager = CatalogExcelManager()
manager.create_sample_excel_catalog("sample.xlsx")

# Пользователь редактирует, затем:
order = manager.create_order_from_excel(
    "sample.xlsx",
    customer_name="Демо компания",
    customer_email="demo@company.ru"
)
```

---

## 🐛 Типичные проблемы & решения

### 1. UnicodeEncodeError на Windows

**Проблема:** Кириллица вызывает ошибку

**Решение:**
```python
import sys
sys.stdout.reconfigure(encoding='utf-8')
```

### 2. openpyxl не найден

**Решение:**
```bash
pip install openpyxl>=3.9.0
```

### 3. Excel файл заблокирован

**Решение:** Закройте файл в Excel перед работой программы

### 4. Парсер не работает

**Проверьте:**
- Интернет подключение
- URL правильный
- Сайт витекс.про доступен

---

## 📈 Возможные расширения

1. **Веб-интерфейс** - Flask/Streamlit
2. **API** - FastAPI для интеграций
3. **БД** - SQLite/PostgreSQL для больших объемов
4. **Цены** - Парсинг и обновление цен
5. **Уведомления** - Telegram/Slack оповещения
6. **PDF счета** - ReportLab для красивых счетов
7. **1C интеграция** - Синхронизация с 1С
8. **История** - Отслеживание всех заявок

---

## 📞 Справка

### Типичный workflow:

```
1. python excel_workflow_example.py
   ↓
2. Открыть lakokrasochnyе_tovarу.xlsx
   ↓
3. Заполнить колону "Количество"
   ↓
4. Сохранить файл
   ↓
5. Письмо готово в exports/
```

### Переменные окружения (.env):

```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your@gmail.com
SENDER_PASSWORD=app_password
```

---

## ✨ Особенности

✅ **Отдельная позиция на фасовку** - Один товар может быть 4 позициями (если 4 фасовки)

✅ **Excel интерфейс** - Пользователи работают привычным инструментом

✅ **Автофильтрация** - Только позиции с qty > 0 попадают в заявку

✅ **Модульная архитектура** - Легко расширять и интегрировать

✅ **Множественные форматы** - TXT, CSV, HTML, XLSX, JSON

✅ **Статусы заявок** - Отслеживание draft → sent → completed

✅ **JSON хранилище** - Просто, быстро, читаемо

---

## 🎓 Документация

Подробные руководства:
- 📖 [EXCEL_WORKFLOW_GUIDE.md](EXCEL_WORKFLOW_GUIDE.md) - Полное руководство по Excel системе
- 📖 [PARSER_INTEGRATION_GUIDE.md](PARSER_INTEGRATION_GUIDE.md) - Интеграция с витекс.про
- 📖 [README.md](README.md) - Общая документация

---

## 🚀 Первые шаги

### Шаг 1: Установка

```bash
cd order-system
pip install -r requirements.txt
```

### Шаг 2: Запуск примера

```bash
python excel_workflow_example.py
```

### Шаг 3: Просмотр результатов

- Открыть `lakokrasochnyе_tovarу.xlsx` в Excel
- Посмотреть письмо в `exports/` папке
- Проверить сохраненную заявку в `orders_storage/`

### Шаг 4: Интеграция

Используйте код из примера в своей системе

---

## 📋 Чек-лист готовности

- ✅ Парсинг витекс.про реализован
- ✅ Отдельные позиции для фасовок
- ✅ Excel экспорт готов
- ✅ Excel импорт работает
- ✅ Фильтрация по количеству работает
- ✅ Генерация заявок работает
- ✅ Множественные форматы экспорта
- ✅ Email отправка готова
- ✅ JSON хранилище работает
- ✅ Примеры написаны
- ✅ Документация полная

---

## 📌 Версия

**v2.0** - Excel workflow edition

- Добавлен парсер v2 с позициями на фасовку
- Добавлен CatalogExcelManager для Excel работы
- Добавлены примеры и подробная документация
- Система готова к production использованию

---

## 🎉 Готово!

Система полностью реализована и готова к использованию. Все требования пользователя выполнены.

**Начните с:** `python excel_workflow_example.py`
