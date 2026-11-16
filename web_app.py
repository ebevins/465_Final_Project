"""Local browser interface for the sports card SQLite application."""

from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import math
from pathlib import Path
import sqlite3
from urllib.parse import parse_qs, urlparse
import webbrowser

import database


HOST = "127.0.0.1"
PORT = 8000
WEB_DIR = Path(__file__).resolve().parent / "web"
MAX_BODY_BYTES = 1_000_000
STATUSES = {"Active", "Sold", "Shipped", "Archived"}


class RequestError(Exception):
    """An input or business-rule error safe to show in the browser."""


def required_text(data, key, label):
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise RequestError(f"{label} is required.")
    return value.strip()


def optional_text(data, key):
    value = data.get(key, "")
    if value is None:
        return ""
    if not isinstance(value, str):
        raise RequestError("Text fields must contain text.")
    return value.strip()


def positive_integer(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        raise RequestError(f"{label} must be a whole number greater than zero.")
    if isinstance(value, str) and not value.strip().isdigit():
        raise RequestError(f"{label} must be a whole number greater than zero.")
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        raise RequestError(f"{label} must be a whole number greater than zero.") from None
    if parsed < 1:
        raise RequestError(f"{label} must be a whole number greater than zero.")
    return parsed


def nonnegative_number(value, label):
    if isinstance(value, bool):
        raise RequestError(f"{label} must be a nonnegative number.")
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        raise RequestError(f"{label} must be a nonnegative number.") from None
    if not math.isfinite(parsed) or parsed < 0:
        raise RequestError(f"{label} must be a nonnegative number.")
    return parsed


def valid_date(value, label):
    text = required_text({"value": value}, "value", label)
    try:
        return date.fromisoformat(text).isoformat()
    except ValueError:
        raise RequestError(f"{label} must use YYYY-MM-DD format.") from None


def row_dict(row):
    return dict(row)


class Handler(BaseHTTPRequestHandler):
    server_version = "SportsCardsLocal/1.0"

    def log_message(self, format_string, *args):
        print(f"[{self.log_date_time_string()}] {format_string % args}")

    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "connect-src 'self'; img-src 'self' data:; object-src 'none'; "
            "base-uri 'none'; frame-ancestors 'none'",
        )
        super().end_headers()

    def send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_error_json(self, message, status):
        self.send_json({"error": message}, status)

    def read_json(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            raise RequestError("Invalid request body length.") from None
        if length < 1 or length > MAX_BODY_BYTES:
            raise RequestError("Request body is empty or too large.")
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise RequestError("Request body must be valid JSON.") from None
        if not isinstance(payload, dict):
            raise RequestError("Request body must be a JSON object.")
        return payload

    def do_GET(self):
        parsed = urlparse(self.path)
        try:
            if parsed.path == "/":
                return self.send_file("index.html", "text/html; charset=utf-8")
            if parsed.path == "/styles.css":
                return self.send_file("styles.css", "text/css; charset=utf-8")
            if parsed.path == "/app.js":
                return self.send_file("app.js", "text/javascript; charset=utf-8")
            if parsed.path == "/api/cards":
                values = parse_qs(parsed.query)
                filters = {
                    key: values.get(query_key, [""])[0].strip()
                    for key, query_key in (
                        ("PlayerName", "player"), ("Sport", "sport"),
                        ("Team", "team"), ("Status", "status"),
                    )
                }
                return self.send_json([row_dict(row) for row in database.search_cards(filters)])
            if parsed.path == "/api/card":
                values = parse_qs(parsed.query)
                card_id = positive_integer(values.get("id", [""])[0], "CardID")
                card = database.get_card_details(card_id)
                if card is None:
                    return self.send_error_json("Card not found.", 404)
                return self.send_json(row_dict(card))
            if parsed.path == "/api/catalogs":
                return self.send_json({
                    "sellers": [row_dict(row) for row in database.get_sellers()],
                    "buyers": [row_dict(row) for row in database.get_buyers()],
                    "active_cards": [row_dict(row) for row in database.get_active_cards()],
                })
            if parsed.path == "/api/summary":
                totals, sports = database.get_summary()
                return self.send_json({
                    "totals": row_dict(totals),
                    "sports": [row_dict(row) for row in sports],
                })
            return self.send_error_json("Page or API route not found.", 404)
        except RequestError as error:
            self.send_error_json(str(error), 400)
        except FileNotFoundError as error:
            self.send_error_json(str(error), 503)
        except sqlite3.Error:
            self.send_error_json("The database request could not be completed.", 500)

    def do_POST(self):
        parsed = urlparse(self.path)
        try:
            data = self.read_json()
            if parsed.path == "/api/purchases":
                return self.add_purchase(data)
            if parsed.path == "/api/cards/update":
                return self.update_card(data)
            if parsed.path == "/api/sales":
                return self.record_sale(data)
            return self.send_error_json("Page or API route not found.", 404)
        except RequestError as error:
            self.send_error_json(str(error), 400)
        except database.DataError as error:
            self.send_error_json(str(error), 409)
        except FileNotFoundError as error:
            self.send_error_json(str(error), 503)
        except sqlite3.IntegrityError:
            self.send_error_json("The change violates a database rule; no changes were saved.", 409)
        except sqlite3.Error:
            self.send_error_json("The change could not be completed; no changes were saved.", 500)

    def add_purchase(self, data):
        seller_id = positive_integer(data.get("seller_id"), "SellerID")
        if not database.seller_exists(seller_id):
            return self.send_error_json("Seller ID does not exist.", 400)
        purchase_date = valid_date(data.get("purchase_date"), "Purchase date")
        payment_type = optional_text(data, "payment_type")
        sport = required_text(data, "sport", "Sport")
        player = required_text(data, "player", "Player name")
        brand = required_text(data, "brand", "Brand")
        raw_year = data.get("year")
        if isinstance(raw_year, bool) or not isinstance(raw_year, (int, str)):
            raise RequestError("Card year must be a whole number from 1900 onward.")
        if isinstance(raw_year, str) and not raw_year.strip().isdigit():
            raise RequestError("Card year must be a whole number from 1900 onward.")
        try:
            year = int(raw_year)
        except (TypeError, ValueError):
            raise RequestError("Card year must be a whole number from 1900 onward.") from None
        if year < 1900:
            raise RequestError("Card year must be a whole number from 1900 onward.")
        condition = data.get("raw_graded")
        if condition not in ("Raw", "Graded"):
            raise RequestError("Condition must be Raw or Graded.")
        grading_company = None
        grade = None
        if condition == "Graded":
            grading_company = required_text(data, "grading_company", "Grading company")
            grade = nonnegative_number(data.get("grade"), "Grade")
            if not 1 <= grade <= 10:
                raise RequestError("Grade must be from 1 to 10.")
        price = nonnegative_number(data.get("purchase_price"), "Purchase price")
        card = {
            "sport": sport,
            "player": player,
            "team": optional_text(data, "team"),
            "year": year,
            "brand": brand,
            "set": optional_text(data, "card_set"),
            "number": optional_text(data, "card_number"),
            "description": optional_text(data, "description"),
            "raw_graded": condition,
            "grading_company": grading_company,
            "grade": grade,
            "serial_number": optional_text(data, "serial_number"),
        }
        card_id, purchase_id = database.add_card_purchase(
            seller_id, purchase_date, payment_type, card, price
        )
        return self.send_json({
            "message": "Purchase saved.", "card_id": card_id, "purchase_id": purchase_id
        }, 201)

    def update_card(self, data):
        card_id = positive_integer(data.get("card_id"), "CardID")
        field = data.get("field")
        if not isinstance(field, str) or field not in {"Status", "Team", "Description", "SerialNumber", "Grade"}:
            raise RequestError("Choose a supported card field to update.")
        card = database.get_card_details(card_id)
        if card is None:
            return self.send_error_json("Card not found.", 404)
        raw_value = data.get("value")
        if field == "Status":
            if not isinstance(raw_value, str) or raw_value not in STATUSES:
                raise RequestError("Choose Active, Sold, Shipped, or Archived.")
            value = raw_value
        elif field == "Grade":
            if raw_value is None or raw_value == "":
                value = None
            else:
                value = nonnegative_number(raw_value, "Grade")
                if not 1 <= value <= 10:
                    raise RequestError("Grade must be from 1 to 10.")
        else:
            if raw_value is not None and not isinstance(raw_value, str):
                raise RequestError("The new value must be text.")
            value = raw_value.strip() or None if isinstance(raw_value, str) else None
        if not database.update_card(card_id, field, value):
            return self.send_error_json("Card not found.", 404)
        return self.send_json({"message": "Card updated successfully."})

    def record_sale(self, data):
        card_id = positive_integer(data.get("card_id"), "CardID")
        buyer_id = positive_integer(data.get("buyer_id"), "BuyerID")
        sale_date = valid_date(data.get("sale_date"), "Sale date")
        payment_type = optional_text(data, "payment_type")
        sale_price = nonnegative_number(data.get("sale_price"), "Sale price")
        fees = nonnegative_number(data.get("fees", 0), "Fees")
        shipping = nonnegative_number(data.get("shipping_cost", 0), "Shipping cost")
        sale_id = database.record_sale(
            card_id, buyer_id, sale_date, payment_type, sale_price, fees, shipping
        )
        return self.send_json({"message": "Sale recorded successfully.", "sale_id": sale_id}, 201)

    def send_file(self, name, content_type):
        file_path = WEB_DIR / name
        try:
            body = file_path.read_bytes()
        except OSError:
            return self.send_error_json("The web interface file is missing.", 404)
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main():
    try:
        with database.connect() as connection:
            connection.execute("SELECT 1").fetchone()
    except FileNotFoundError as error:
        print(error)
        return 1
    except sqlite3.Error as error:
        print(f"Could not open sports_cards.db: {error}")
        return 1

    address = f"http://{HOST}:{PORT}/"
    try:
        server = ThreadingHTTPServer((HOST, PORT), Handler)
    except OSError as error:
        print(f"Could not start the local web server on port {PORT}: {error}")
        return 1
    print("Sports Card Inventory & Sales System")
    print(f"Local web app running at {address}")
    print("Only this computer can connect. Press Ctrl+C to stop.")
    try:
        webbrowser.open(address)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
