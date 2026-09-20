import re
from sqlalchemy.orm import Session
from app.models import MenuItem


def find_menu_item(db: Session, item_name: str):
    """
    Menu mein item search karta hai.
    """

    item_name = item_name.lower().strip()

    menu_items = (
        db.query(MenuItem)
        .filter(MenuItem.available == True)
        .all()
    )

    for item in menu_items:
        if item.name.lower() in item_name:
            return item

    for item in menu_items:
        if item_name in item.name.lower():
            return item

    return None


def parse_order(message: str, db: Session):
    """
    Customer ke message ko order items mein convert karta hai.
    """

    message_lower = message.lower()

    menu_items = (
        db.query(MenuItem)
        .filter(MenuItem.available == True)
        .all()
    )

    order_items = []

    for menu_item in menu_items:

        item_name = menu_item.name.lower()

        if item_name in message_lower:

            # Item se pehle quantity search karo
            pattern = rf"(\d+)\s*(?:x|×)?\s*{re.escape(item_name)}"

            match = re.search(pattern, message_lower)

            if match:
                quantity = int(match.group(1))
            else:
                quantity = 1

            order_items.append({
                "menu_item_id": menu_item.id,
                "name": menu_item.name,
                "quantity": quantity,
                "unit_price": menu_item.price,
                "total": quantity * menu_item.price
            })

    return order_items


def calculate_order_total(order_items, delivery_charges=0):

    subtotal = sum(
        item["total"]
        for item in order_items
    )

    total = subtotal + delivery_charges

    return {
        "subtotal": subtotal,
        "delivery_charges": delivery_charges,
        "total": total
    }