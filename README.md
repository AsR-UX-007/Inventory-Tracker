# Inventory and Reorder Tracker

## Aim
To build a Python program to manage stock quantities and sales for a small electronics shop/laboratory.

## Features
- `Item` class with stock-in, stock-out, and reorder checks.
- CSV files for inventory and sales records.
- NumPy consumption summary.
- Pandas category-wise and month-wise sales reports.
- JSON inventory export.
- Bar graphs for category sales and current stock.
- Comparison of two reorder thresholds.
- Validation for invalid quantities and stock-outs.

## Requirements
Python 3.9 or later is recommended.

Install the libraries:
```bash
python -m pip install -r requirements.txt
```

Run:
```bash
python main.py
```

## Files created
- `inventory.csv`: current stock records.
- `sales.csv`: sales transactions.
- `inventory_export.json`: JSON export created from menu option 8.
- `sales_by_category.png`: category sales graph when sales exist.
- `stock_levels.png`: current stock graph.

## Example test cases
1. Stock-in 5 units of E102: quantity should change from 8 to 13.
2. Stock-out 3 units of E101: quantity should change from 50 to 47 and a sale record should be written.
3. Stock-out 999 units of E102: operation should fail with a stock-out message and quantity should remain unchanged.
4. Stock-in 0 or -2 units: operation should fail because quantity must be positive.
5. Compare thresholds 5 and 10: an item with quantity 8 should be marked REORDER at threshold 10, but OK at threshold 5.
6. Export JSON: `inventory_export.json` should contain all inventory item records.

## Algorithm
1. Start the program and load inventory records from CSV.
2. Display the menu.
3. Accept the user's operation.
4. Validate the item ID and quantity.
5. Update stock and save the CSV file, or record a sale.
6. Use NumPy and Pandas for summaries and reports.
7. Export JSON or create graphs when requested.
8. Repeat until the user chooses Save and Exit.

## Discussion
A lower reorder threshold produces fewer reorder alerts but may increase the chance of stock-outs. A higher threshold provides earlier warnings but may lead to holding more stock. The best threshold depends on supplier lead time, item demand, and storage cost.
