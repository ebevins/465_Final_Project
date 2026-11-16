# COSC 465 Final Project
## Sports Card Inventory and Sales System

## Project Overview

This SQLite application helps a small sports card business track cards, purchases from sellers, sales to buyers, and current inventory. A user can browse cards, review their transaction history, add purchases, update card details, review summary reports, and record sales.

## DBMS

SQLite. The command-line application is written in Python and uses the built-in `sqlite3` module. It requires no third-party Python packages.

## Repository Contents

- `schema.sql` creates the seven tables, keys, constraints, `CurrentInventory` view, and player-name index.
- `insert_data.sql` loads the sample sellers, buyers, cards, purchases, and sales.
- `queries.sql` contains the nine Deliverable 4 query examples.
- `transaction.sql` demonstrates a sale transaction and rolls it back to preserve sample data.
- `run_queries.sh` recreates the local database, runs `queries.sql`, and runs `transaction.sql`.
- `app.py` provides the interactive six-operation command-line menu.
- `database.py` contains the SQLite connection helper and parameterized database operations.
- `web_app.py` serves the optional local browser interface and JSON API using Python's built-in HTTP server.
- `web/index.html`, `web/styles.css`, and `web/app.js` provide the browser interface without third-party packages.
- `Database ER diagram (crow's foot).pdf` is the project ER diagram.
- `.gitignore` excludes the generated local database and Python cache files.
- `sports_cards.db` is generated locally by the setup commands and is not required in the repository.

## Database Setup

Run these commands from the repository root, in this order:

```bash
rm -f sports_cards.db
sqlite3 sports_cards.db < schema.sql
sqlite3 sports_cards.db < insert_data.sql
```

`schema.sql` creates the structure before `insert_data.sql` loads rows. Both SQL files enable SQLite foreign-key enforcement with `PRAGMA foreign_keys = ON`. The application enables foreign keys separately on every connection. SQLite foreign-key enforcement is connection-specific.

## SQL Testing

Run:

```bash
bash run_queries.sh
```

The script recreates `sports_cards.db` from the two SQL setup files, executes the nine queries with column headings, and runs the transaction demonstration. The demonstration rolls back its sample sale so the sample data remains intact. The script requires Bash and the SQLite command-line tool (`sqlite3`); set `SQLITE` to the executable path if it is not on `PATH`.

## Application Setup

Use Python 3 and its built-in `sqlite3` module; no third-party package installation is required. First create `sports_cards.db` as shown above. Both application entry points look for the database beside the project files, report setup instructions if it is missing, and never replace it automatically. Python 3 must be installed and available to your terminal.

Launch from Windows Git Bash with:

```bash
python app.py
```

On macOS or Linux, use:

```bash
python3 app.py
```

## Graphical Interface

The project also includes a browser-based interface that uses Python's built-in HTTP server, plain HTML/CSS/JavaScript, and the same SQLite operations as the CLI. It is an optional front end; the CLI remains available and functional.

Start it from the repository root. On Windows Git Bash:

```bash
python web_app.py
```

On macOS or Linux, run `python3 web_app.py`.

The server opens the interface at `http://127.0.0.1:8000` and listens only on this computer. Keep the terminal open while using the page; press `Ctrl+C` there to stop the server. The interface requires the same existing `sports_cards.db` file as the CLI.

## Major Application Operations

1. **Search / Browse Cards** — search by partial player name, sport, team, or status; leave filters blank to browse all.
2. **View Card Purchase and Sale Details** — show card attributes and joined purchase, seller, sale, and buyer details.
3. **Add a New Card Purchase** — transactionally create a purchase, card, and purchase-item link.
4. **Update a Card** — change status, team, description, serial number, or grade.
5. **Inventory / Sales Summary Report** — show inventory and sales aggregates and cards grouped by sport.
6. **Record a Card Sale** — transactionally create the sale and sale-item rows and mark the card sold.

## Database Design

The seven-table relational design is `Seller`, `Purchase`, `PurchaseItem`, `Card`, `SaleItem`, `Sale`, and `Buyer`. A seller can be associated with purchases; each purchase is linked to cards through `PurchaseItem`, which records each card's acquisition price. A buyer can be associated with sales; `SaleItem` links each sale to its cards and records each card's sale price.

Primary and foreign keys connect the records. Foreign-key enforcement prevents references to missing sellers, buyers, purchases, cards, or sales. CHECK constraints restrict seller and buyer types, card condition, status, year, grade range, and nonnegative amounts. `CurrentInventory` is a view that joins active, unsold cards to their purchase prices and sellers. `idx_card_playername` indexes `Card.PlayerName` for common player searches.

## Transactions

`transaction.sql` demonstrates inserting a sale, its sale item, and a status update in one transaction, then rolling the example back. The application's purchase and sale operations also group related writes in one transaction; an error rolls back the entire operation. User-provided values are passed through SQLite placeholders.

## Testing

The SQL files were run against a database recreated from `schema.sql` and `insert_data.sql`; all nine queries completed, the transaction demonstration rolled back, `PRAGMA integrity_check` returned `ok`, and `PRAGMA foreign_key_check` returned no violations. The CLI passed 53 interactive checks covering its menu operations, filtering, validation, connection handling, persistence, and transaction rollback. The browser API passed 20 checks covering static files, search, details, report data, purchase/update/sale writes, validation, and rollback after a simulated database error. Python and JavaScript syntax checks also passed, and the CLI still starts normally. The test database was isolated from the local sample database.

## Known Limitations

- The application records one card per purchase and one card per sale operation. The database design supports multiple cards in each transaction through the item tables.
- Purchase `TotalAmount` is recorded as the purchase price entered for the single card added by the app.
- Summary revenue is the sum of sale-item prices; fees and shipping are displayed in card details but are not included in the revenue total.
- Profit is not reported because the schema does not define how fees, shipping, or shared purchase totals should be allocated to individual cards.
- The browser server is a local course/demo tool. It binds to `127.0.0.1` and is not intended for public hosting.

## Reproduction Instructions

After cloning the repository, change into its root directory and run:

```bash
rm -f sports_cards.db
sqlite3 sports_cards.db < schema.sql
sqlite3 sports_cards.db < insert_data.sql
bash run_queries.sh
python app.py
```

For the browser interface, run `python web_app.py` instead.

No repository URL is specified here because the canonical remote URL is not part of the project files.

## Demonstration Guide

1. Explain that the project tracks sports cards, acquisitions, buyers, and sales.
2. Show `Database ER diagram (crow's foot).pdf` and explain the purchase and sale item tables.
3. Launch `python web_app.py` in Windows Git Bash (`python3 web_app.py` on macOS or Linux) to demonstrate the browser interface. The CLI remains available with `python app.py`.
4. Browse cards and search for a partial player name.
5. Show joined purchase and sale details for one active and one sold card.
6. Update a card or add a card purchase.
7. Show the inventory and sales summary.
8. Record a sale and show that the card status and sale records were saved together.
9. Recreate the database from the SQL files after the demonstration to restore sample data.

## Key Design Decisions

- `Purchase` stores transaction-level details; `PurchaseItem` stores each card and its individual acquisition price. This lets a purchase contain multiple cards without repeating the transaction fields.
- `Sale` stores buyer and transaction details; `SaleItem` stores the cards and individual sale prices in that sale.
- Foreign keys keep transaction records connected to valid sellers, buyers, and cards.
- `CurrentInventory` centralizes a useful join for active cards that have not been sold.
- `idx_card_playername` supports player-name searches.
- Parameterized SQL keeps typed values separate from SQL commands.
- A sale uses a transaction so its sale, sale item, and card status update either all persist or all roll back.
