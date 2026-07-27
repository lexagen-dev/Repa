## `vitex/parser.py`


from __future__ import annotations

import logging
import re
import time
from typing import Any
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

# Razdely kataloga - zadajte vashi URLs
try:
    from .config import CATALOG_SECTIONS
except (ImportError, ValueError):
    try:
        from config import CATALOG_SECTIONS
    except ImportError:
        CATALOG_SECTIONS = []


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

REQUEST_TIMEOUT = 30
REQUEST_DELAY = 0.4

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
}

session = requests.Session()
session.headers.update(HEADERS)


def fetch_soup(url: str) -> BeautifulSoup:
    """Загружает страницу и возвращает HTML как BeautifulSoup."""
    response = session.get(url, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def normalize_url(url: str) -> str:
    """Удаляет query-параметры и приводит URL к одному виду."""
    parsed = urlparse(url)

    path = re.sub(r"/+", "/", parsed.path).rstrip("/") + "/"

    return f"{parsed.scheme}://{parsed.netloc}{path}"


def text_or_empty(element: Any) -> str:
    """Возвращает текст элемента без лишних пробелов."""
    if not element:
        return ""

    return " ".join(element.get_text(" ", strip=True).split())


def is_internal_url(url: str) -> bool:
    """Проверяет, что ссылка относится к сайту vitex.pro."""
    parsed = urlparse(url)
    return parsed.netloc.lower() in {"vitex.pro", "www.vitex.pro"}


def is_service_url(url: str) -> bool:
    """Проверяет, относится ли ссылка к служебным страницам сайта."""
    path = urlparse(url).path.strip("/").lower()

    forbidden_paths = {
        "",
        "catalog",
        "contacts",
        "blog",
        "vitextherm",
        "search",
        "cart",
        "login",
        "register",
        "privacy-policy",
        "politika-konfidentsialnosti",
    }

    if path in forbidden_paths:
        return True

    forbidden_parts = (
        "/wp-admin/",
        "/wp-content/",
        "/feed/",
        "/tag/",
        "/category/",
        "/author/",
        "/page/",
    )

    url_lower = url.lower()

    return any(part in url_lower for part in forbidden_parts)


def is_product_url(url: str, section_urls: set[str]) -> bool:
    """
    Проверяет, является ли ссылка карточкой товара.

    Формат карточки товара:
    https://vitex.pro/catalog/название-раздела/название-товара/
    """
    if not is_internal_url(url):
        return False

    parsed = urlparse(url)

    if parsed.query or parsed.fragment:
        return False

    if re.search(
        r"\.(pdf|jpg|jpeg|png|webp|gif|svg|doc|docx|xls|xlsx)$",
        parsed.path,
        re.IGNORECASE,
    ):
        return False

    normalized_url = normalize_url(url)

    # Исключаем страницы самих категорий.
    if normalized_url in section_urls:
        return False

    if is_service_url(normalized_url):
        return False

    parts = [part for part in parsed.path.split("/") if part]

    # У товара должно быть ровно три части пути:
    # catalog / category / product-name.
    if len(parts) != 3 or parts[0].lower() != "catalog":
        return False

    # Исключаем справочные страницы:
    # /catalog/info/how-to/
    # /catalog/info/pistopoiiseis_proionton/
    # /catalog/info/regulation-marking/
    if parts[1].lower() == "info":
        return False

    return True


def collect_product_links(section_url: str, section_urls: set[str]) -> list[str]:
    """Собирает ссылки на карточки товаров со страницы категории."""
    soup = fetch_soup(section_url)
    product_links: set[str] = set()

    for anchor in soup.find_all("a", href=True):
        href = anchor["href"].strip()

        if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue

        product_url = normalize_url(urljoin(section_url, href))

        if is_product_url(product_url, section_urls):
            product_links.add(product_url)

    logging.info("В разделе найдено ссылок на товары: %s", len(product_links))

    return sorted(product_links)


def get_category(soup: BeautifulSoup, section_url: str) -> str:
    """Получает категорию товара из хлебных крошек или URL раздела."""
    breadcrumb_selectors = (
        ".breadcrumb a",
        ".breadcrumbs a",
        ".b-breadcrumbs a",
        "[class*='breadcrumb'] a",
        "[class*='crumb'] a",
    )

    ignored = {"главная", "home", "каталог", "catalog", "каталог продукции"}

    for selector in breadcrumb_selectors:
        values = []

        for item in soup.select(selector):
            value = text_or_empty(item)

            if value and value.lower() not in ignored:
                values.append(value)

        if values:
            # Последний элемент обычно название товара.
            # Предпоследний — категория.
            if len(values) >= 2:
                return values[-2]

            return values[-1]

    parts = [part for part in urlparse(section_url).path.split("/") if part]

    if len(parts) >= 2:
        return parts[-1].replace("-", " ").strip()

    return ""


def get_product_name(soup: BeautifulSoup) -> str:
    """Извлекает название товара из H1."""
    return text_or_empty(soup.find("h1"))


def get_english_name(soup: BeautifulSoup) -> str:
    """Пытается извлечь второе, чаще английское, название товара."""
    selectors = (
        ".product__name-en",
        ".product-name-en",
        ".product__subtitle",
        ".product-subtitle",
        ".subtitle",
        ".product-title-en",
        "h1 + p",
        "h1 + div",
    )

    product_name = get_product_name(soup)

    for selector in selectors:
        for element in soup.select(selector):
            value = text_or_empty(element)

            if (
                value
                and value != product_name
                and 2 <= len(value) <= 150
                and re.search(r"[A-Za-z]", value)
            ):
                return value

    return ""


def get_description(soup: BeautifulSoup) -> str:
    """Извлекает описание товара."""
    selectors = (
        ".product__description",
        ".product-description",
        ".product__content",
        ".product-content",
        ".description",
        "[class*='description']",
        "[class*='product-info']",
    )

    for selector in selectors:
        for element in soup.select(selector):
            value = text_or_empty(element)

            if 30 <= len(value) <= 3000:
                return value

    h1 = soup.find("h1")

    if h1:
        for element in h1.find_all_next(["p", "div"]):
            value = text_or_empty(element)

            if 30 <= len(value) <= 1500:
                return value

    return ""


def normalize_package(number: str, unit: str) -> str:
    """Приводит фасовку к формату: 0.75 л, 750 мл, 25 кг."""
    number = number.replace(",", ".").strip()
    unit = unit.lower().strip()

    unit_map = {
        "л": "л",
        "l": "л",
        "мл": "мл",
        "ml": "мл",
        "кг": "кг",
        "г": "г",
        "шт": "шт",
        "pcs": "шт",
    }

    normalized_unit = unit_map.get(unit)

    if not normalized_unit:
        return ""

    return f"{number} {normalized_unit}"


def get_packages(soup: BeautifulSoup) -> list[str]:
    """
    Извлекает фасовки товара из всего текста HTML-страницы.

    Поддерживаются:
    0,75 л
    0.75 л
    750 мл
    2,5 кг
    """
    packages: set[str] = set()

    page_text = soup.get_text(" ", strip=True)

    pattern = re.compile(
        r"(?<![\w.-])"
        r"(\d+(?:[.,]\d+)?)"
        r"\s*"
        r"(л|l|мл|ml|кг|г|шт|pcs)"
        r"(?![\w.-])",
        re.IGNORECASE,
    )

    for number, unit in pattern.findall(page_text):
        package = normalize_package(number, unit)

        if package:
            packages.add(package)

    unit_order = {
        "мл": 0,
        "г": 1,
        "л": 2,
        "кг": 3,
        "шт": 4,
    }

    def package_sort_key(package: str) -> tuple[int, float]:
        number, unit = package.split(" ", maxsplit=1)
        return unit_order.get(unit, 99), float(number)

    return sorted(packages, key=package_sort_key)


def parse_product(product_url: str, section_url: str) -> dict[str, Any]:
    """Собирает данные с одной карточки товара."""
    soup = fetch_soup(product_url)

    return {
        "Категория": get_category(soup, section_url),
        "Наименование": get_product_name(soup),
        "Наименование EN": get_english_name(soup),
        "Описание": get_description(soup),
        "Фасовки": get_packages(soup),
        "Ссылка": product_url,
    }


def parse_catalog(section_urls_input: list = None) -> list[dict[str, Any]]:
    """Skaniruet kategorii i vozvrashcaet seznam tovarov."""
    if section_urls_input is None:
        section_urls_input = CATALOG_SECTIONS
    
    if not section_urls_input:
        logging.error("Oshibka: ne zadany razdely kataloga!")
        return []
    
    section_urls = {normalize_url(url) for url in section_urls_input}

    # Slovar' avtomaticheski ubiraet dubli ssylok.
    product_pages: dict[str, str] = {}

    for raw_section_url in section_urls_input:
        section_url = normalize_url(raw_section_url)

        logging.info("Skanirovanie razdela: %s", section_url)

        try:
            product_links = collect_product_links(section_url, section_urls)

            for product_url in product_links:
                product_pages[product_url] = section_url

        except requests.RequestException as error:
            logging.error(
                "Не удалось загрузить раздел %s: %s",
                section_url,
                error,
            )

        time.sleep(REQUEST_DELAY)

    logging.info("Всего уникальных карточек товаров: %s", len(product_pages))

    products: list[dict[str, Any]] = []

    for number, product_url in enumerate(sorted(product_pages), start=1):
        section_url = product_pages[product_url]

        logging.info(
            "[%s/%s] Обработка товара: %s",
            number,
            len(product_pages),
            product_url,
        )

        try:
            product = parse_product(product_url, section_url)

            if product["Наименование"]:
                products.append(product)
            else:
                logging.warning(
                    "Страница пропущена: у неё отсутствует H1: %s",
                    product_url,
                )

        except requests.RequestException as error:
            logging.error(
                "Не удалось загрузить товар %s: %s",
                product_url,
                error,
            )

        time.sleep(REQUEST_DELAY)

    logging.info("Парсинг завершён. Получено товаров: %s", len(products))

    return products


if __name__ == "__main__":
    # Primer: zadajte vashi razdely kataloga vitex
    EXAMPLE_SECTIONS = [
        "https://vitex.pro/catalog/oils/",
        "https://vitex.pro/catalog/lubricants/",
    ]
    
    catalog = parse_catalog(EXAMPLE_SECTIONS)

    print("\nNajdeno tovarov: " + str(len(catalog)) + "\n")

    for product in catalog:
        packages = ", ".join(product["Fasovki"]) or "ne naideny"

        print("Naimenovanie: " + product["Naimenovanie"])
        print("Kategoriya: " + product["Kategoriya"])
        print("Fasovki: " + packages)
        print("Ssylka: " + product["Ssylka"])
        print("-" * 80)
