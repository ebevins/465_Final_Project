COSC 465 Final Project
Sports Card Inventory and Sales System

DBMS Used: SQLite

Setup Instructions:
1. Open a terminal in the project folder.
2. Start SQLite with:
   sqlite3 sports_cards.db
3. Run:
   .read schema.sql
4. Run:
   .read insert_data.sql
5. Verify foreign keys are enabled with:
   PRAGMA foreign_keys;
6. The database is now ready to use.


Database View: CurrentInventory

The CurrentInventory view displays active sports cards that have been purchased but have not yet been sold. It combines data from the Card, PurchaseItem, Purchase, and Seller tables so that current inventory can be viewed in one place.

Database Index: idx_card_playername

This index is created on Card.PlayerName to improve performance when searching or filtering cards by player name.

Design Changes:
The original practice ERD used Seller, Card, Buyer, and Sale. The final design was expanded to include Purchase, PurchaseItem, and SaleItem.

PurchaseItem connects purchases to individual cards, allowing one purchase to contain multiple cards.

SaleItem connects sales to individual cards, allowing one sale to contain multiple cards.

This structure better represents real sports card transactions and reduces repeated transaction data.

Testing:
The database was recreated from scratch using only schema.sql and insert_data.sql.

The following tests were completed successfully:
- All tables were created.
- All sample data loaded successfully.
- Foreign key checks passed.
- Database integrity check returned "ok".
- The CurrentInventory view returned records correctly.
- The player-name index was created.
- CHECK constraints correctly rejected invalid data.
