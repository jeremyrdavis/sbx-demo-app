"""A tiny in-memory inventory.

Provides an `Item` model for a single SKU's stock record and an `Inventory`
class that tracks a collection of `Item`s keyed by SKU.
"""

from pydantic import BaseModel, Field


class Item(BaseModel):
    """A single SKU's stock record.

    `unit_price` and `quantity` must both be non-negative (enforced by the
    `Field(ge=0)` validators); pydantic raises a validation error otherwise.
    """

    sku: str
    name: str
    unit_price: float = Field(ge=0)
    quantity: int = Field(ge=0)


class Inventory:
    """An in-memory store of `Item`s, keyed by SKU."""

    def __init__(self) -> None:
        """Start with no items in stock."""
        self._items: dict[str, Item] = {}

    def add_item(self, sku: str, name: str, unit_price: float, quantity: int = 1) -> Item:
        """Add stock for a SKU.

        Adding a SKU that already exists increases its quantity; the stored
        name and unit price are kept. Adding a brand-new SKU creates a new
        `Item` using the given name and unit price.
        """
        existing = self._items.get(sku)
        if existing is not None:
            item = Item(
                sku=sku,
                name=existing.name,
                unit_price=existing.unit_price,
                quantity=existing.quantity + quantity,
            )
        else:
            item = Item(sku=sku, name=name, unit_price=unit_price, quantity=quantity)
        self._items[sku] = item
        return item

    def remove_item(self, sku: str, quantity: int | None = None) -> None:
        """Remove `quantity` units of a SKU, or the whole SKU if quantity is None.

        If `quantity` matches the current stock exactly (or is omitted), the
        SKU is deleted entirely. Otherwise the stock is reduced by
        `quantity`, keeping the rest of the item unchanged.

        Raises KeyError for an unknown SKU and ValueError if there is not
        enough stock.
        """
        item = self._items[sku]
        if quantity is None or quantity == item.quantity:
            del self._items[sku]
            return
        if quantity < 0 or quantity > item.quantity:
            raise ValueError(f"cannot remove {quantity} of {sku}; {item.quantity} in stock")
        self._items[sku] = item.model_copy(update={"quantity": item.quantity - quantity})

    def total_value(self) -> float:
        """Total stock value, rounded to cents.

        Sums `unit_price * quantity` across every item currently in stock.
        """
        return round(sum(i.unit_price * i.quantity for i in self._items.values()), 2)
