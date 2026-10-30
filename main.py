import csv
import json
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

DATA_FILE = Path("inventory.csv")
SALES_FILE = Path("sales.csv")
JSON_FILE = Path("inventory_export.json")


class Item:
    """Represents one item in the inventory."""

    def __init__(self, item_id, name, category, quantity, price, reorder_threshold=10):
        self.item_id = str(item_id)
        self.name = str(name)
        self.category = str(category)
        self.quantity = int(quantity)
        self.price = float(price)
        self.reorder_threshold = int(reorder_threshold)

        if self.quantity < 0 or self.price < 0 or self.reorder_threshold < 0:
            raise ValueError("Quantity, price, and reorder threshold cannot be negative.")

    def stock_in(self, amount):
        """Add stock after validating the quantity."""
        amount = self._validate_amount(amount)
        self.quantity += amount

    def stock_out(self, amount):
        """Sell/remove stock, rejecting invalid amounts and stock-outs."""
        amount = self._validate_amount(amount)
        if amount > self.quantity:
            raise ValueError(
                f"Stock-out: only {self.quantity} unit(s) of {self.name} available."
            )
        self.quantity -= amount

    @staticmethod
    def _validate_amount(amount):
        if isinstance(amount, bool):
            raise ValueError("Quantity must be a positive whole number.")
        try:
            number = int(amount)
        except (TypeError, ValueError):
            raise ValueError("Quantity must be a positive whole number.")
        if str(number) != str(amount).strip() or number <= 0:
            raise ValueError("Quantity must be a positive whole number.")
        return number

    def needs_reorder(self, threshold=None):
        """Return True when quantity is at or below the selected threshold."""
        if threshold is None:
            threshold = self.reorder_threshold
        return self.quantity <= threshold

    def to_dict(self):
        return {
            "item_id": self.item_id,
            "name": self.name,
            "category": self.category,
            "quantity": self.quantity,
            "price": self.price,
            "reorder_threshold": self.reorder_threshold,
        }


def load_inventory(filename=DATA_FILE):
    items = []
    if not filename.exists():
        return items
    with filename.open("r", newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            items.append(Item(
                row["item_id"], row["name"], row["category"],
                int(row["quantity"]), float(row["price"]),
                int(row["reorder_threshold"])
            ))
    return items


def save_inventory(items, filename=DATA_FILE):
    fields = ["item_id", "name", "category", "quantity", "price", "reorder_threshold"]
    with filename.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        for item in items:
            writer.writerow(item.to_dict())


def save_sale(item, amount, filename=SALES_FILE):
    """Append a sale record so monthly/category reports can be generated."""
    file_exists = filename.exists()
    with filename.open("a", newline="", encoding="utf-8") as file:
        fields = ["date", "item_id", "item_name", "category", "quantity_sold",
                  "unit_price", "sales_amount"]
        writer = csv.DictWriter(file, fieldnames=fields)
        if not file_exists or filename.stat().st_size == 0:
            writer.writeheader()
        writer.writerow({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "item_id": item.item_id,
            "item_name": item.name,
            "category": item.category,
            "quantity_sold": amount,
            "unit_price": item.price,
            "sales_amount": round(amount * item.price, 2),
        })


def export_json(items, filename=JSON_FILE):
    with filename.open("w", encoding="utf-8") as file:
        json.dump([item.to_dict() for item in items], file, indent=4)
    print(f"Inventory exported to {filename}.")


def show_inventory(items):
    if not items:
        print("Inventory is empty.")
        return
    print("\nID    Item                 Category        Qty   Price     Status")
    print("-" * 72)
    for item in items:
        status = "REORDER" if item.needs_reorder() else "OK"
        print(f"{item.item_id:<5} {item.name:<20} {item.category:<15} "
              f"{item.quantity:<5} ₹{item.price:<8.2f} {status}")


def consumption_summary():
    if not SALES_FILE.exists():
        print("No sales records yet.")
        return
    sales = pd.read_csv(SALES_FILE)
    if sales.empty:
        print("No sales records yet.")
        return
    quantities = sales["quantity_sold"].to_numpy()
    print("\nConsumption summary (units sold):")
    print(f"Total units sold : {np.sum(quantities)}")
    print(f"Average per sale : {np.mean(quantities):.2f}")
    print(f"Highest sale     : {np.max(quantities)}")
    print(f"Lowest sale      : {np.min(quantities)}")


def reports_and_graphs(items):
    if SALES_FILE.exists():
        sales = pd.read_csv(SALES_FILE)
        if not sales.empty:
            sales["date"] = pd.to_datetime(sales["date"])
            sales["month"] = sales["date"].dt.to_period("M").astype(str)

            print("\nSales by category:")
            print(sales.groupby("category")["sales_amount"].sum().to_string())

            print("\nSales by month:")
            print(sales.groupby("month")["sales_amount"].sum().to_string())

            category_sales = sales.groupby("category")["sales_amount"].sum()
            category_sales.plot(kind="bar", title="Sales by Category", ylabel="Sales (₹)")
            plt.tight_layout()
            plt.savefig("sales_by_category.png")
            plt.show()

    if items:
        names = [item.name for item in items]
        levels = [item.quantity for item in items]
        plt.figure()
        plt.bar(names, levels)
        plt.title("Current Stock Levels")
        plt.xlabel("Item")
        plt.ylabel("Quantity")
        plt.xticks(rotation=25, ha="right")
        plt.tight_layout()
        plt.savefig("stock_levels.png")
        plt.show()


def compare_thresholds(items, threshold_one=5, threshold_two=10):
    print(f"\nReorder threshold comparison ({threshold_one} vs {threshold_two}):")
    print(f"{'Item':<22}{'Stock':<8}{f'At {threshold_one}':<14}{f'At {threshold_two}':<14}")
    for item in items:
        first = "REORDER" if item.needs_reorder(threshold_one) else "OK"
        second = "REORDER" if item.needs_reorder(threshold_two) else "OK"
        print(f"{item.name:<22}{item.quantity:<8}{first:<14}{second:<14}")


def add_item(items):
    item_id = input("Item ID: ").strip()
    if any(item.item_id == item_id for item in items):
        print("That item ID already exists.")
        return
    name = input("Item name: ").strip()
    category = input("Category: ").strip()
    try:
        quantity = int(input("Opening quantity: "))
        price = float(input("Unit price (₹): "))
        threshold = int(input("Reorder threshold [10]: ") or "10")
        item = Item(item_id, name, category, quantity, price, threshold)
        if not item_id or not name or not category:
            raise ValueError("ID, name, and category cannot be blank.")
        items.append(item)
        save_inventory(items)
        print("Item added.")
    except ValueError as error:
        print(f"Invalid input: {error}")


def main():
    items = load_inventory()
    if not items:
        # Starter sample data; save it to CSV on first run.
        items = [
            Item("E101", "Resistor Pack", "Components", 50, 20.0, 10),
            Item("E102", "LED Pack", "Components", 8, 35.0, 10),
            Item("E103", "Digital Multimeter", "Instruments", 5, 650.0, 3),
            Item("E104", "Breadboard", "Tools", 15, 120.0, 5),
        ]
        save_inventory(items)

    while True:
        print("\n========== INVENTORY AND REORDER TRACKER ==========")
        print("1. View inventory")
        print("2. Stock-in (purchase/restock)")
        print("3. Stock-out (sale)")
        print("4. Add new item")
        print("5. Consumption summary (NumPy)")
        print("6. Category/month reports and graphs (Pandas)")
        print("7. Compare reorder thresholds")
        print("8. Export inventory to JSON")
        print("9. Save and exit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            show_inventory(items)
        elif choice in ("2", "3"):
            show_inventory(items)
            item_id = input("Enter item ID: ").strip()
            item = next((x for x in items if x.item_id == item_id), None)
            if item is None:
                print("Item ID not found.")
                continue
            try:
                amount = int(input("Enter quantity: "))
                if choice == "2":
                    item.stock_in(amount)
                    save_inventory(items)
                    print(f"Stock updated. New quantity: {item.quantity}")
                else:
                    item.stock_out(amount)
                    save_sale(item, amount)
                    save_inventory(items)
                    print(f"Sale recorded. Remaining quantity: {item.quantity}")
            except ValueError as error:
                print(f"Operation failed: {error}")
        elif choice == "4":
            add_item(items)
        elif choice == "5":
            consumption_summary()
        elif choice == "6":
            reports_and_graphs(items)
        elif choice == "7":
            try:
                first = int(input("First threshold [5]: ") or "5")
                second = int(input("Second threshold [10]: ") or "10")
                if first < 0 or second < 0:
                    raise ValueError("Thresholds cannot be negative.")
                compare_thresholds(items, first, second)
            except ValueError as error:
                print(f"Invalid threshold: {error}")
        elif choice == "8":
            export_json(items)
        elif choice == "9":
            save_inventory(items)
            print("Inventory saved. Goodbye!")
            break
        else:
            print("Please choose a number from 1 to 9.")


if __name__ == "__main__":
    main()
