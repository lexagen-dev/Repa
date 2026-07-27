# 📌 БЫСТРЫЕ ССЫЛКИ И НАЧАЛО РАБОТЫ

## ⚡ ЗАПУСК В 30 СЕКУНД

```bash
cd c:\Users\Николай\VSC_Projects\order-system
python excel_workflow_example.py
```

**Готово!** Система создаст:
- ✅ Каталог в Excel
- ✅ Заполненную заявку  
- ✅ Письмо в формате HTML

---

## 📚 Документация

| Документ | Цель | Для кого |
|----------|------|---------|
| [SYSTEM_COMPLETE.md](SYSTEM_COMPLETE.md) | **Полное резюме проекта** | Менеджеры, архитекторы |
| [EXCEL_WORKFLOW_GUIDE.md](EXCEL_WORKFLOW_GUIDE.md) | **Подробное руководство по Excel** | Пользователи, разработчики |
| [PARSER_INTEGRATION_GUIDE.md](PARSER_INTEGRATION_GUIDE.md) | **Интеграция с витекс.про** | Разработчики |
| [README.md](README.md) | **Общая документация** | Все |

---

## 💾 Новые файлы

### Парсер (v2) — для отдельных позиций на фасовку
📄 [parsers/catalog_parser_v2.py](parsers/catalog_parser_v2.py) (320+ строк)

```python
catalog = parse_catalog(["https://vitex.pro/catalog/paints/"])
# Возвращает: list позиций, ОДНА позиция = ОДНА фасовка!
```

### Excel Управление — CatalogExcelManager
📄 [export/catalog_manager.py](export/catalog_manager.py) (350+ строк)

```python
manager = CatalogExcelManager()
manager.export_catalog_to_excel(catalog, "file.xlsx")
order = manager.create_order_from_excel("file.xlsx")
```

### Полный пример — от парсинга до письма
📄 [excel_workflow_example.py](excel_workflow_example.py) (350+ строк)

```bash
python excel_workflow_example.py
```

---

## 🔑 Три сценария использования

### Сценарий 1️⃣: Я хочу просто попробовать

```bash
python excel_workflow_example.py
```

**Результаты в:**
- `lakokrasochnyе_tovarу.xlsx` — каталог в Excel
- `exports/ORD-*.html` — письмо готово
- `orders_storage/` — сохраненные заявки

---

### Сценарий 2️⃣: Я хочу понять как это работает

1. Прочитайте [EXCEL_WORKFLOW_GUIDE.md](EXCEL_WORKFLOW_GUIDE.md) (15 минут)
2. Запустите `excel_workflow_example.py`
3. Посмотрите результаты

---

### Сценарий 3️⃣: Я хочу интегрировать в свою систему

```python
# Ваш скрипт:
from export.catalog_manager import CatalogExcelManager
from export.email_formatter import EmailFormatter

# Ваш каталог
catalog = [...]  # Ваши товары

# Экспортируем
manager = CatalogExcelManager()
manager.export_catalog_to_excel(catalog, "catalog.xlsx")

# Создаем заявку
order = manager.create_order_from_excel("catalog.xlsx")

# Отправляем
formatter = EmailFormatter()
formatter.send_email(order)
```

---

## 📊 Основные классы

### CatalogExcelManager

```python
manager = CatalogExcelManager()

# Основные методы:
manager.export_catalog_to_excel(catalog, "file.xlsx")
positions = manager.load_catalog_with_quantities("file.xlsx")
order = manager.create_order_from_excel("file.xlsx", customer_name, email)
manager.create_sample_excel_catalog("sample.xlsx")
```

### Order

```python
from orders.order import Order, OrderItem

order = Order(order_id="ORD-001", customer_name="...", customer_email="...")
order.add_item(OrderItem(...))
order.calculate_total()
```

### EmailFormatter

```python
formatter = EmailFormatter(
    smtp_host='smtp.gmail.com',
    smtp_port=587,
    sender_email='your@gmail.com',
    sender_password='password'
)

formatter.send_email(order)
files = formatter.export_to_files(order)
```

---

## 🗂️ Структура проекта

```
order-system/
│
├─ parsers/
│  ├─ catalog_parser_v2.py    ← НОВОЕ (парсер v2)
│  ├─ catalog_parser.py
│  ├─ config.py
│  └─ __init__.py
│
├─ export/
│  ├─ catalog_manager.py      ← НОВОЕ (Excel)
│  ├─ email_formatter.py
│  ├─ text_formatter.py
│  ├─ table_formatter.py
│  └─ __init__.py
│
├─ orders/
│  ├─ order.py
│  └─ __init__.py
│
├─ utils/
│  ├─ order_manager.py
│  └─ __init__.py
│
├─ excel_workflow_example.py  ← НОВОЕ (пример)
│
├─ SYSTEM_COMPLETE.md         ← НОВОЕ (резюме)
├─ EXCEL_WORKFLOW_GUIDE.md    ← НОВОЕ (руководство)
├─ PARSER_INTEGRATION_GUIDE.md
├─ README.md
└─ requirements.txt
```

---

## 🎯 Рабочий процесс

```
┌─────────────────────────────────────────────────────────┐
│ ШАГИ РАБОТЫ СИСТЕМЫ                                     │
└─────────────────────────────────────────────────────────┘

1. ПАРСИНГ КАТАЛОГА
   ↓
   parse_catalog(urls) → list[dict позиций]
   (Одна позиция = одна фасовка!)
   
2. ЭКСПОРТ В EXCEL
   ↓
   export_catalog_to_excel(catalog, "file.xlsx")
   (Создается красиво отформатированный файл)
   
3. ПОЛЬЗОВАТЕЛЬ ЗАПОЛНЯЕТ (в Excel)
   ↓
   Открыть файл → Заполнить колону "Количество"
   
4. СОЗДАНИЕ ЗАЯВКИ
   ↓
   order = create_order_from_excel("file.xlsx")
   (Берет только позиции где qty > 0)
   
5. СОХРАНЕНИЕ
   ↓
   order_manager.save_order(order)
   (JSON в orders_storage/)
   
6. ЭКСПОРТ ФОРМАТОВ
   ↓
   formatter.export_to_files(order)
   (TXT, CSV, HTML, JSON)
   
7. ОТПРАВКА (опционально)
   ↓
   formatter.send_email(order)
   (SMTP)
```

---

## ✨ Ключевые особенности

| Особенность | Описание | Файл |
|------------|---------|------|
| **Отдельная позиция на фасовку** | Один товар → N позиций (по фасовкам) | `catalog_parser_v2.py` |
| **Excel интерфейс** | Привычный интерфейс для пользователей | `catalog_manager.py` |
| **Автофильтрация** | Только qty > 0 → в заявку | `create_order_from_excel()` |
| **Множественные форматы** | TXT, CSV, HTML, XLSX, JSON | `export/` |
| **Email интеграция** | SMTP с поддержкой различных сервисов | `email_formatter.py` |
| **JSON хранилище** | Просто и быстро | `order_manager.py` |

---

## 🚀 Для первого запуска

### Требования:
```bash
pip install -r requirements.txt
```

### Запуск:
```bash
python excel_workflow_example.py
```

### Проверка результатов:
1. Откройте `lakokrasochnyе_tovarу.xlsx` в Excel
2. Посмотрите письмо в `exports/ORD-*.html`
3. Проверьте сохраненную заявку `orders_storage/`

---

## 📞 Типичные команды

### Парсинг каталога
```python
from parsers.catalog_parser_v2 import parse_catalog
catalog = parse_catalog(["https://vitex.pro/catalog/paints/"])
```

### Экспорт в Excel
```python
from export.catalog_manager import CatalogExcelManager
manager = CatalogExcelManager()
manager.export_catalog_to_excel(catalog, "my_catalog.xlsx")
```

### Создание заявки
```python
order = manager.create_order_from_excel("my_catalog.xlsx", "Компания", "email@com.ru")
```

### Отправка письма
```python
from export.email_formatter import EmailFormatter
formatter = EmailFormatter(...)
formatter.send_email(order)
```

### Сохранение
```python
from utils.order_manager import OrderManager
om = OrderManager()
om.save_order(order)
```

---

## 🎓 Рекомендуемый порядок обучения

1. **Этап 0** (5 минут) → Запустить `python excel_workflow_example.py`
2. **Этап 1** (15 минут) → Прочитать [EXCEL_WORKFLOW_GUIDE.md](EXCEL_WORKFLOW_GUIDE.md)
3. **Этап 2** (30 минут) → Изучить код в примерах
4. **Этап 3** (1 час) → Создать свой скрипт

---

## 📋 Чек-лист готовности

- ✅ Все файлы созданы
- ✅ Все зависимости установлены
- ✅ Парсер работает
- ✅ Excel экспорт работает
- ✅ Excel импорт работает
- ✅ Фильтрация по количеству работает
- ✅ Заявки создаются
- ✅ Письма генерируются
- ✅ Email отправка готова
- ✅ Документация полная
- ✅ Примеры написаны

---

## 🎉 СИСТЕМА ГОТОВА К ИСПОЛЬЗОВАНИЮ!

**Начните сейчас:**

```bash
python excel_workflow_example.py
```

Вопросы? Смотрите документацию выше ⬆️
