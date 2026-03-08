import enum
from datetime import datetime, timezone
from app.extensions import db

class OrderStatus(enum.Enum):
    """
    Enum defining the state machine for an Order.
    - pending      : Order placed, awaiting admin review/payment.
    - confirmed    : Admin accepted the order and payment secured.
    - in_progress  : Work is currently being executed.
    - quality_check: Work is done, pending internal QA or client review.
    - completed    : Final deliverables handed over.
    - cancelled    : Order aborted (by admin or client).
    """
    pending = "pending"
    confirmed = "confirmed"
    in_progress = "in_progress"
    quality_check = "quality_check"
    completed = "completed"
    cancelled = "cancelled"


class Order(db.Model):
    """
    Represents a client's transaction for one or more services.
    
    Relationships:
      - Belongs to a User (Many-to-One).
      - Has many OrderItems (One-to-Many).
    """
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    
    status = db.Column(db.Enum(OrderStatus), default=OrderStatus.pending, nullable=False)
    total_price = db.Column(db.Numeric(10, 2), default=0.00, nullable=False)
    
    # Timestamps for auditing
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = db.relationship("User", backref=db.backref("orders", lazy=True, cascade="all, delete-orphan"))
    items = db.relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    def calculate_total(self):
        """
        Iterates over child OrderItems, ensuring each line item is calculated,
        then sums them to update the Order's total_price.
        """
        total = 0
        for item in self.items:
            item.calculate_subtotal()
            if item.subtotal:
                total += item.subtotal
        self.total_price = total

    def __repr__(self):
        return f"<Order #{self.id} | User {self.user_id} | {self.status.name}>"


class OrderItem(db.Model):
    """
    A line-item representing a specific service within an Order.
    
    Snapshot Pricing Rule:
    The `unit_price` MUST be copied from the Service's `base_price` at the 
    exact moment the order is created. This ensures historical orders do 
    not change price if the admin updates the catalog pricing layer later.
    """
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey("sahal_services.id"), nullable=False)
    
    quantity = db.Column(db.Integer, nullable=False, default=1)
    
    # Snapshot at time of booking
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)

    # Relationships
    order = db.relationship("Order", back_populates="items")
    service = db.relationship("Service") # We don't necessarily need backref on service here.

    def calculate_subtotal(self):
        """
        Computes subtotal = quantity * unit_price.
        Ensures Decimal types are handled cleanly.
        """
        if self.quantity and self.unit_price:
            self.subtotal = self.quantity * self.unit_price
        else:
            self.subtotal = 0.00

    def __repr__(self):
        return f"<OrderItem: Order #{self.order_id} | Service {self.service_id} | Qty {self.quantity}>"
