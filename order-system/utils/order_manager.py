"""Управление заявками - сохранение, загрузка, поиск."""
import json
from pathlib import Path
from typing import List, Optional
from orders.order import Order, OrderItem
from datetime import datetime


class OrderManager:
    """Менеджер для управления заявками."""
    
    def __init__(self, storage_dir: str = './orders_storage'):
        """
        Инициализация менеджера заявок.
        
        Args:
            storage_dir: Директория для хранения заявок
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def save_order(self, order: Order, filename: str = None) -> str:
        """
        Sokhranyaet zayavku v JSON fajl.
        
        Args:
            order: Ob'ekt zayavki
            filename: Imya fajla (esli None, ispolzuetsya order_id)
            
        Returns:
            Put' k sokhranennomu fajlu
        """
        if filename is None:
            filename = f"{order.order_id}.json"
        
        file_path = self.storage_dir / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(order.to_dict(), f, ensure_ascii=False, indent=2)
        
        print("[OK] Zayavka sokhranena: " + str(file_path))
        return str(file_path)
    
    def load_order(self, filename: str) -> Optional[Order]:
        """
        Zagruzhaet zayavku iz JSON fajla.
        
        Args:
            filename: Imya fajla
            
        Returns:
            Ob'ekt Order ili None
        """
        file_path = self.storage_dir / filename
        
        if not file_path.exists():
            print("[ERROR] Fajl ne nayden: " + str(file_path))
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Vosstanovlenie ob'ekta Order
            order = Order(
                order_id=data['order_id'],
                customer_name=data['customer_name'],
                customer_email=data['customer_email'],
                status=data['status'],
                notes=data.get('notes'),
                total_sum=data.get('total_sum'),
            )
            
            order.created_at = datetime.fromisoformat(data['created_at'])
            
            for item_data in data.get('items', []):
                item = OrderItem(
                    product_name=item_data['product_name'],
                    category=item_data['category'],
                    quantity=item_data['quantity'],
                    unit=item_data['unit'],
                    price=item_data.get('price'),
                    product_url=item_data.get('product_url'),
                    notes=item_data.get('notes'),
                )
                order.add_item(item)
            
            return order
            
        except Exception as e:
            print("[ERROR] Oshibka pri zagruzke zayavki: " + str(e))
            return None
    
    def list_orders(self) -> List[str]:
        """
        Получает список всех сохраненных заявок.
        
        Returns:
            Список имен файлов заявок
        """
        files = list(self.storage_dir.glob('*.json'))
        return [f.name for f in sorted(files)]
    
    def delete_order(self, filename: str) -> bool:
        """
        Udalyaet zayavku.
        
        Args:
            filename: Imya fajla
            
        Returns:
            True esli udaleno uspeshno
        """
        file_path = self.storage_dir / filename
        
        try:
            file_path.unlink()
            print("[OK] Zayavka udalena: " + str(file_path))
            return True
        except Exception as e:
            print("[ERROR] Oshibka pri udalenii: " + str(e))
            return False
    
    def search_orders(self, query: str = None, status: str = None) -> List[Order]:
        """
        Поиск заявок по критериям.
        
        Args:
            query: Поиск в названии продукта или заказчика
            status: Фильтр по статусу
            
        Returns:
            Список найденных заявок
        """
        results = []
        
        for filename in self.list_orders():
            order = self.load_order(filename)
            if order is None:
                continue
            
            # Фильтр по статусу
            if status and order.status != status:
                continue
            
            # Поиск в заказчике
            if query and query.lower() in order.customer_name.lower():
                results.append(order)
                continue
            
            # Поиск в товарах
            if query:
                for item in order.items:
                    if (query.lower() in item.product_name.lower() or 
                        query.lower() in item.category.lower()):
                        results.append(order)
                        break
        
        return results
