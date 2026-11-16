"""Interactive command-line interface for the sports card database."""

from datetime import date
import math
import sqlite3

import database


STATUSES = ("Active", "Sold", "Shipped", "Archived")


def prompt_required(label):
    while True:
        value = input(label).strip()
        if value:
            return value
        print("This value is required.")


def prompt_int(label, minimum=None):
    while True:
        try:
            value = int(input(label).strip())
            if minimum is not None and value < minimum:
                raise ValueError
            return value
        except ValueError:
            print("Enter a valid whole number" + (f" of at least {minimum}." if minimum is not None else "."))


def prompt_money(label):
    while True:
        try:
            value = float(input(label).strip())
            if not math.isfinite(value) or value < 0:
                raise ValueError
            return value
        except ValueError:
            print("Enter a valid nonnegative amount.")


def prompt_date(label):
    while True:
        value = prompt_required(label)
        try:
            return date.fromisoformat(value).isoformat()
        except ValueError:
            print("Enter a valid date in YYYY-MM-DD format.")


def print_table(rows):
    if not rows:
        print("No matching cards found.")
        return
    headers = list(rows[0].keys())
    values = [["" if row[h] is None else str(row[h]) for h in headers] for row in rows]
    widths = [min(32, max(len(str(h)), *(len(v[i]) for v in values))) for i, h in enumerate(headers)]
    print(" | ".join(str(h).ljust(widths[i]) for i, h in enumerate(headers)))
    print("-+-".join("-" * w for w in widths))
    for row in values:
        print(" | ".join(value[:widths[i]].ljust(widths[i]) for i, value in enumerate(row)))


def search_browse():
    print("\nSearch / Browse Cards")
    print("Leave a filter blank to skip it.")
    filters = {
        "PlayerName": input("Player name contains: ").strip(),
        "Sport": input("Sport contains: ").strip(),
        "Team": input("Team contains: ").strip(),
        "Status": input("Status contains: ").strip(),
    }
    rows = database.search_cards(filters)
    if rows:
        print_table(rows)
    else:
        print("No matching cards found.")


def show_card_details():
    card_id = prompt_int("CardID: ", 1)
    row = database.get_card_details(card_id)
    if row is None:
        print("Card not found.")
        return
    print("\nCard and Transaction Details")
    for key, value in dict(row).items():
        print(f"{key}: {value if value is not None else 'N/A'}")


def add_purchase():
    print("\nAdd a New Card Purchase")
    seller_id = prompt_int("SellerID: ", 1)
    if not database.seller_exists(seller_id):
        print("Seller ID does not exist.")
        return
    purchase_date = prompt_date("Purchase date (YYYY-MM-DD): ")
    payment_type = input("Payment type (optional): ").strip()
    print("Enter card details:")
    card = {
        "sport": prompt_required("Sport: "),
        "player": prompt_required("Player name: "),
        "team": input("Team (optional): ").strip(),
        "year": prompt_int("Card year (1900 or later): ", 1900),
        "brand": prompt_required("Brand: "),
        "set": input("Card set (optional): ").strip(),
        "number": input("Card number (optional): ").strip(),
        "description": input("Description (optional): ").strip(),
    }
    while True:
        raw_graded = input("Condition (Raw/Graded): ").strip().title()
        if raw_graded in ("Raw", "Graded"):
            break
        print("Enter Raw or Graded.")
    card["raw_graded"] = raw_graded
    card["grading_company"] = None
    card["grade"] = None
    if raw_graded == "Graded":
        card["grading_company"] = prompt_required("Grading company: ")
        while True:
            try:
                grade = float(input("Grade (1-10): ").strip())
                if not math.isfinite(grade) or not 1 <= grade <= 10:
                    raise ValueError
                card["grade"] = grade
                break
            except ValueError:
                print("Invalid grade. Enter a number from 1 to 10.")
    card["serial_number"] = input("Serial number (optional): ").strip()
    price = prompt_money("Purchase price: $")
    try:
        card_id, purchase_id = database.add_card_purchase(
            seller_id, purchase_date, payment_type, card, price
        )
        print(f"Purchase saved. CardID {card_id}; PurchaseID {purchase_id}.")
    except sqlite3.Error:
        print("Purchase could not be completed. No changes were saved.")


def update_card():
    print("\nUpdate a Card")
    card_id = prompt_int("CardID: ", 1)
    if database.get_card_details(card_id) is None:
        print("Card not found.")
        return
    print("1. Status  2. Team  3. Description  4. Serial number  5. Grade")
    choice = input("Field to update: ").strip()
    field_map = {"1": "Status", "2": "Team", "3": "Description", "4": "SerialNumber", "5": "Grade"}
    field = field_map.get(choice)
    if field is None:
        print("Invalid update selection.")
        return
    if field == "Status":
        value = input(f"New status ({'/'.join(STATUSES)}): ").strip().title()
        if value not in STATUSES:
            print("Invalid status. Choose Active, Sold, Shipped, or Archived.")
            return
    elif field == "Grade":
        raw = input("New grade (blank to clear): ").strip()
        if not raw:
            value = None
        else:
            try:
                value = float(raw)
                if not math.isfinite(value) or not 1 <= value <= 10:
                    raise ValueError
            except ValueError:
                print("Invalid grade. Enter a number from 1 to 10.")
                return
    else:
        value = input("New value (blank to clear): ").strip() or None
    try:
        database.update_card(card_id, field, value)
        print("Card updated successfully.")
    except sqlite3.Error:
        print("Card could not be updated. No changes were saved.")


def summary_report():
    totals, sports = database.get_summary()
    print("\nInventory / Sales Summary")
    print(f"Active cards: {totals['active_count']}")
    print(f"Current inventory acquisition cost: ${totals['inventory_cost']:,.2f}")
    print(f"Average current inventory purchase price: ${totals['average_cost']:,.2f}")
    print(f"Sold cards: {totals['sold_count']}")
    print(f"Total sales revenue: ${totals['revenue']:,.2f}")
    print(f"Average sale price: ${totals['average_sale']:,.2f}")
    print("\nCards by Sport")
    print_table(sports)


def record_card_sale():
    print("\nRecord a Card Sale")
    card_id = prompt_int("CardID: ", 1)
    card = database.get_card_details(card_id)
    if card is None:
        print("Card not found.")
        return
    if card["Status"] != "Active":
        if card["SalePrice"] is not None:
            print("That card has already been sold.")
        else:
            print("Only active cards can be sold.")
        return
    buyer_id = prompt_int("BuyerID: ", 1)
    if not database.buyer_exists(buyer_id):
        print("Buyer ID does not exist.")
        return
    sale_date = prompt_date("Sale date (YYYY-MM-DD): ")
    payment_type = input("Payment type (optional): ").strip()
    sale_price = prompt_money("Sale price: $")
    fees = prompt_money("Fees: $")
    shipping = prompt_money("Shipping cost: $")
    try:
        sale_id = database.record_sale(
            card_id, buyer_id, sale_date, payment_type, sale_price, fees, shipping
        )
        print(f"Sale recorded successfully. SaleID {sale_id}; CardID {card_id} is now Sold.")
    except database.DataError as error:
        print(str(error))
    except sqlite3.Error:
        print("Sale could not be completed. No changes were saved.")


def main():
    try:
        with database.connect() as connection:
            connection.execute("SELECT 1").fetchone()
    except FileNotFoundError as error:
        print(error)
        return
    except sqlite3.Error as error:
        print(f"Could not open sports_cards.db: {error}")
        return

    operations = {
        "1": search_browse,
        "2": show_card_details,
        "3": add_purchase,
        "4": update_card,
        "5": summary_report,
        "6": record_card_sale,
    }
    while True:
        print("\n========================================")
        print("Sports Card Inventory & Sales System")
        print("========================================")
        print("1. Search / Browse Cards")
        print("2. View Card Purchase and Sale Details")
        print("3. Add a New Card Purchase")
        print("4. Update a Card")
        print("5. Inventory / Sales Summary Report")
        print("6. Record a Card Sale")
        print("7. Exit")
        choice = input("Enter choice: ").strip()
        if choice == "7":
            print("Goodbye.")
            break
        operation = operations.get(choice)
        if operation is None:
            print("Invalid menu selection. Enter a number from 1 to 7.")
            continue
        try:
            operation()
        except (ValueError, sqlite3.Error) as error:
            print(f"Operation could not be completed: {error}")


if __name__ == "__main__":
    main()
