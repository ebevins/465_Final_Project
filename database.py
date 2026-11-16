"""Database access and SQL operations for the sports card application."""

from contextlib import contextmanager
from pathlib import Path
import sqlite3


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "sports_cards.db"


class DataError(Exception):
    """A user-facing database operation error."""


@contextmanager
def connect():
    """Open the project database and enable foreign-key enforcement."""
    if not DATABASE_PATH.is_file():
        raise FileNotFoundError(
            "sports_cards.db was not found. Recreate it with:\n"
            "  sqlite3 sports_cards.db < schema.sql\n"
            "  sqlite3 sports_cards.db < insert_data.sql"
        )
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    try:
        connection.execute("PRAGMA foreign_keys = ON")
        with connection:
            yield connection
    finally:
        connection.close()


def search_cards(filters=None):
    filters = filters or {}
    sql = """SELECT CardID, PlayerName, Sport, Team, CardYear, Brand,
                    CardSet, CardNumber, Grade, Status
             FROM Card"""
    clauses, values = [], []
    for key in ("PlayerName", "Sport", "Team", "Status"):
        value = filters.get(key)
        if value:
            clauses.append(f"{key} LIKE ?")
            values.append(f"%{value}%")
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY PlayerName COLLATE NOCASE, CardYear DESC, CardID"
    with connect() as connection:
        return connection.execute(sql, values).fetchall()


def get_card_details(card_id):
    sql = """SELECT c.CardID, c.PlayerName, c.Sport, c.Team, c.CardYear,
                    c.Brand, c.CardSet, c.CardNumber, c.Description,
                    c.RawGraded, c.GradingCompany, c.Grade, c.SerialNumber,
                    c.Status, p.PurchasePrice, pu.PurchaseDate,
                    se.FirstName || ' ' || se.LastName AS SellerName,
                    si.SalePrice, sa.SaleDate,
                    bu.FirstName || ' ' || bu.LastName AS BuyerName
             FROM Card AS c
             LEFT JOIN PurchaseItem AS p ON p.CardID = c.CardID
             LEFT JOIN Purchase AS pu ON pu.PurchaseID = p.PurchaseID
             LEFT JOIN Seller AS se ON se.SellerID = pu.SellerID
             LEFT JOIN SaleItem AS si ON si.CardID = c.CardID
             LEFT JOIN Sale AS sa ON sa.SaleID = si.SaleID
             LEFT JOIN Buyer AS bu ON bu.BuyerID = sa.BuyerID
             WHERE c.CardID = ?"""
    with connect() as connection:
        return connection.execute(sql, (card_id,)).fetchone()


def seller_exists(seller_id):
    with connect() as connection:
        return connection.execute(
            "SELECT 1 FROM Seller WHERE SellerID = ?", (seller_id,)
        ).fetchone() is not None


def buyer_exists(buyer_id):
    with connect() as connection:
        return connection.execute(
            "SELECT 1 FROM Buyer WHERE BuyerID = ?", (buyer_id,)
        ).fetchone() is not None


def add_card_purchase(seller_id, purchase_date, payment_type, card, price):
    """Insert purchase, card, and purchase item atomically."""
    with connect() as connection:
        cursor = connection.cursor()
        cursor.execute("BEGIN")
        try:
            cursor.execute(
                "INSERT INTO Purchase (SellerID, PurchaseDate, PaymentType, TotalAmount) "
                "VALUES (?, ?, ?, ?)",
                (seller_id, purchase_date, payment_type or None, price),
            )
            purchase_id = cursor.lastrowid
            cursor.execute(
                """INSERT INTO Card
                   (Sport, PlayerName, Team, CardYear, Brand, CardSet,
                    CardNumber, Description, RawGraded, GradingCompany,
                    Grade, SerialNumber, Status)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Active')""",
                (
                    card["sport"], card["player"], card["team"] or None,
                    card["year"], card["brand"], card["set"] or None,
                    card["number"] or None, card["description"] or None,
                    card["raw_graded"], card["grading_company"] or None,
                    card["grade"], card["serial_number"] or None,
                ),
            )
            card_id = cursor.lastrowid
            cursor.execute(
                "INSERT INTO PurchaseItem (PurchaseID, CardID, PurchasePrice) "
                "VALUES (?, ?, ?)",
                (purchase_id, card_id, price),
            )
            connection.commit()
            return card_id, purchase_id
        except Exception:
            connection.rollback()
            raise


def update_card(card_id, field, value):
    allowed = {"Status", "Team", "Description", "SerialNumber", "Grade"}
    if field not in allowed:
        raise ValueError("Unsupported card field.")
    with connect() as connection:
        cursor = connection.execute(
            f"UPDATE Card SET {field} = ? WHERE CardID = ?", (value, card_id)
        )
        return cursor.rowcount > 0


def get_summary():
    with connect() as connection:
        totals = connection.execute(
            """SELECT
                 (SELECT COUNT(*) FROM CurrentInventory) AS active_count,
                 (SELECT COALESCE(SUM(PurchasePrice), 0) FROM CurrentInventory) AS inventory_cost,
                 (SELECT COALESCE(AVG(PurchasePrice), 0) FROM CurrentInventory) AS average_cost,
                 (SELECT COUNT(*) FROM SaleItem) AS sold_count,
                 (SELECT COALESCE(SUM(SalePrice), 0) FROM SaleItem) AS revenue,
                 (SELECT COALESCE(AVG(SalePrice), 0) FROM SaleItem) AS average_sale"""
        ).fetchone()
        sports = connection.execute(
            "SELECT Sport, COUNT(*) AS CardCount FROM Card "
            "GROUP BY Sport ORDER BY CardCount DESC, Sport"
        ).fetchall()
        return totals, sports


def record_sale(card_id, buyer_id, sale_date, payment_type, sale_price, fees, shipping):
    """Record a sale and update card status as one transaction."""
    with connect() as connection:
        cursor = connection.cursor()
        cursor.execute("BEGIN")
        try:
            card = cursor.execute(
                "SELECT Status FROM Card WHERE CardID = ?", (card_id,)
            ).fetchone()
            if card is None:
                raise DataError("Card not found.")
            if cursor.execute(
                "SELECT 1 FROM SaleItem WHERE CardID = ?", (card_id,)
            ).fetchone():
                raise DataError("That card has already been sold.")
            if card["Status"] != "Active":
                raise DataError("Only active cards can be sold.")
            if cursor.execute(
                "SELECT 1 FROM Buyer WHERE BuyerID = ?", (buyer_id,)
            ).fetchone() is None:
                raise DataError("Buyer ID does not exist.")
            cursor.execute(
                "INSERT INTO Sale (BuyerID, SaleDate, PaymentType, Fees, ShippingCost) "
                "VALUES (?, ?, ?, ?, ?)",
                (buyer_id, sale_date, payment_type or None, fees, shipping),
            )
            sale_id = cursor.lastrowid
            cursor.execute(
                "INSERT INTO SaleItem (SaleID, CardID, SalePrice) VALUES (?, ?, ?)",
                (sale_id, card_id, sale_price),
            )
            cursor.execute("UPDATE Card SET Status = 'Sold' WHERE CardID = ?", (card_id,))
            connection.commit()
            return sale_id
        except Exception:
            connection.rollback()
            raise
