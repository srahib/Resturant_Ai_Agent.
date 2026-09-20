from fastapi import FastAPI, Depends, Request, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

import json

from app.config import APP_NAME, RESTAURANT_NAME, WHATSAPP_VERIFY_TOKEN
from app.database import engine, get_db, Base
from app.models import MenuItem, Customer, Order
from app.schemas import MenuItemCreate, MenuItemResponse
from app.order_engine import parse_order, calculate_order_total

# Create database tables
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title=APP_NAME,
    description="AI-powered WhatsApp restaurant order-taking system",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "status": "success",
        "message": f"{RESTAURANT_NAME} AI Order Agent is running!"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/restaurant")
def restaurant():
    return {
        "restaurant": RESTAURANT_NAME,
        "service": "WhatsApp AI Ordering",
        "status": "active"
    }


# -----------------------------
# MENU APIs
# -----------------------------

@app.post("/menu", response_model=MenuItemResponse)
def create_menu_item(
    item: MenuItemCreate,
    db: Session = Depends(get_db)
):
    new_item = MenuItem(
        name=item.name,
        category=item.category,
        description=item.description,
        price=item.price,
        available=item.available
    )

    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return new_item


@app.get("/menu", response_model=list[MenuItemResponse])
def get_menu(
    db: Session = Depends(get_db)
):
    return db.query(MenuItem).all()

# -----------------------------
# AI ORDER ENGINE
# -----------------------------

class OrderMessage(BaseModel):
    message: str
    delivery_charges: float = 0


@app.post("/order/parse")
def parse_customer_order(
    order: OrderMessage,
    db: Session = Depends(get_db)
):
    items = parse_order(
        order.message,
        db
    )

    if not items:
        return {
            "success": False,
            "message": "Sorry, menu item nahi mila.",
            "items": [],
            "total": 0
        }

    totals = calculate_order_total(
        items,
        order.delivery_charges
    )

    return {
        "success": True,
        "customer_message": order.message,
        "items": items,
        "subtotal": totals["subtotal"],
        "delivery_charges": totals["delivery_charges"],
        "total": totals["total"]
    }
class CreateOrderRequest(BaseModel):
    customer_name: str
    phone: str
    message: str

    order_type: str = "delivery"
    payment_method: str = "cash"

    delivery_address: str = ""

    delivery_charges: float = 150

@app.post("/order/create")
def create_order(
    order_data: CreateOrderRequest,
    db: Session = Depends(get_db)
):
    # --------------------------------
    # STEP 1: Parse customer message
    # --------------------------------

    items = parse_order(
        order_data.message,
        db
    )

    if not items:
        return {
            "success": False,
            "message": "Menu item nahi mila."
        }

    # --------------------------------
    # STEP 2: Calculate total
    # --------------------------------

    totals = calculate_order_total(
        items,
        order_data.delivery_charges
    )

    # --------------------------------
    # STEP 3: Find existing customer
    # --------------------------------

    customer = (
        db.query(Customer)
        .filter(Customer.phone == order_data.phone)
        .first()
    )

    # --------------------------------
    # STEP 4: Create customer
    # --------------------------------

    if not customer:

        customer = Customer(
            name=order_data.customer_name,
            phone=order_data.phone,
            address=order_data.delivery_address
        )

        db.add(customer)
        db.commit()
        db.refresh(customer)

    else:

        customer.name = order_data.customer_name

        if order_data.delivery_address:
            customer.address = order_data.delivery_address

        db.commit()
        db.refresh(customer)

    # --------------------------------
    # STEP 5: Save order
    # --------------------------------

    new_order = Order(
        customer_id=customer.id,

        items=json.dumps(items),

        subtotal=totals["subtotal"],

        delivery_charges=totals[
            "delivery_charges"
        ],

        total=totals["total"],

        order_type=order_data.order_type,

        payment_method=order_data.payment_method,

        status="new",

        delivery_address=order_data.delivery_address
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    # --------------------------------
    # STEP 6: Response
    # --------------------------------

    return {
        "success": True,

        "order_id": new_order.id,

        "status": new_order.status,

        "customer": {
            "id": customer.id,
            "name": customer.name,
            "phone": customer.phone
        },

        "items": items,

        "subtotal": totals["subtotal"],

        "delivery_charges": totals[
            "delivery_charges"
        ],

        "total": totals["total"],

        "order_type": new_order.order_type,

        "payment_method": new_order.payment_method,

        "delivery_address": new_order.delivery_address,

        "message": (
            f"Order #{new_order.id} successfully created."
        )
    }
# --------------------------------
# WHATSAPP WEBHOOK
# --------------------------------
@app.get("/webhook")
def verify_whatsapp_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge")
):

    if (
        hub_mode == "subscribe"
        and hub_verify_token == WHATSAPP_VERIFY_TOKEN
    ):
        return int(hub_challenge)

    return {
        "success": False,
        "message": "Webhook verification failed"
    }
@app.post("/webhook")
async def whatsapp_webhook(request: Request):

    data = await request.json()

    print("\n========== WHATSAPP MESSAGE ==========")
    print(data)
    print("======================================\n")

    return {
        "success": True
    }