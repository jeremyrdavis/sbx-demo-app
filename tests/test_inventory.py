"""Tests for the Inventory class and its Item records (app/inventory.py)."""

import pytest

from app.inventory import Inventory


@pytest.fixture
def inv() -> Inventory:
    """A fresh, empty Inventory for each test."""
    return Inventory()


def test_add_item_returns_item(inv):
    """add_item returns an Item with the sku/name/price/quantity it was given."""
    item = inv.add_item("A1", "Widget", 2.50, 4)
    assert (item.sku, item.name, item.unit_price, item.quantity) == ("A1", "Widget", 2.50, 4)


def test_add_existing_sku_increases_quantity_and_keeps_price(inv):
    """Re-adding an existing SKU bumps its quantity but keeps the original name/price."""
    inv.add_item("A1", "Widget", 2.50, 4)
    item = inv.add_item("A1", "Renamed", 9.99, 1)
    assert item.quantity == 5
    assert item.name == "Widget"
    assert item.unit_price == 2.50


def test_add_item_rejects_negative_price(inv):
    """A negative unit_price fails Item's validation with a ValueError."""
    with pytest.raises(ValueError):
        inv.add_item("A1", "Widget", -1.0)


def test_remove_partial_quantity(inv):
    """Removing fewer units than are in stock just reduces the remaining quantity."""
    inv.add_item("A1", "Widget", 2.0, 5)
    inv.remove_item("A1", 2)
    assert inv.total_value() == 6.0


def test_remove_all_when_quantity_omitted(inv):
    """Omitting quantity removes the SKU entirely, leaving the inventory empty."""
    inv.add_item("A1", "Widget", 2.0, 5)
    inv.remove_item("A1")
    assert inv.total_value() == 0.0


def test_remove_unknown_sku_raises_key_error(inv):
    """Removing a SKU that was never added raises KeyError."""
    with pytest.raises(KeyError):
        inv.remove_item("nope")


def test_remove_more_than_in_stock_raises_value_error(inv):
    """Removing more units than are in stock raises ValueError."""
    inv.add_item("A1", "Widget", 2.0, 1)
    with pytest.raises(ValueError):
        inv.remove_item("A1", 2)


def test_total_value_sums_all_items_and_rounds(inv):
    """total_value sums unit_price * quantity across all items and rounds to cents."""
    inv.add_item("A1", "Widget", 0.10, 3)
    inv.add_item("B2", "Gadget", 1.005, 2)
    assert inv.total_value() == 2.31


def test_total_value_empty(inv):
    """total_value is zero for an inventory with no items."""
    assert inv.total_value() == 0.0
