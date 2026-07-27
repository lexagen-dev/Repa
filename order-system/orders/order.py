"""Модель заявки на продукцию."""
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, List


@dataclass
class OrderItem:
    """Позиция в заявке."""
    product_name: str
    category: str
    quantity: float
    unit: str
    price: Optional[float] = None
    product_url: Optional[str] = None
    notes: Optional[str] = None

    def to_dict(self):
        """Преобразование в словарь."""
        return asdict(self)


@dataclass
class Order:
    """Заявка на продукцию."""
    order_id: str
    customer_name: str
    customer_email: str
    created_at: datetime = field(default_factory=datetime.now)
    items: List[OrderItem] = field(default_factory=list)
    status: str = "draft"  # draft, sent, confirmed, completed
    notes: Optional[str] = None
    total_sum: Optional[float] = None

    def add_item(self, item: OrderItem) -> None:
        """Добавить позицию в заявку."""
        self.items.append(item)

    def remove_item(self, index: int) -> None:
        """Удалить позицию из заявки."""
        if 0 <= index < len(self.items):
            self.items.pop(index)

    def get_total_items(self) -> int:
        """Получить количество позиций."""
        return len(self.items)

    def calculate_total(self) -> float:
        """Рассчитать общую сумму."""
        total = 0.0
        for item in self.items:
            if item.price:
                total += item.price * item.quantity
        self.total_sum = total
        return total

    def to_dict(self) -> dict:
        """Преобразование в словарь."""
        return {
            "order_id": self.order_id,
            "customer_name": self.customer_name,
            "customer_email": self.customer_email,
            "created_at": self.created_at.isoformat(),
            "items": [item.to_dict() for item in self.items],
            "status": self.status,
            "notes": self.notes,
            "total_sum": self.total_sum,
        }
