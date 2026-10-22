# COSC 465 Final Project

## Sports Card Inventory and Sales System

### DBMS Used

SQLite

## Setup Instructions

1. Open a terminal in the project folder.
2. Start SQLite by running:

```bash
sqlite3 sports_cards.db
```

3. Run the schema file:

```sql
.read schema.sql
```

4. Run the sample data file:

```sql
.read insert_data.sql
```

5. Verify that foreign keys are enabled:

```sql
PRAGMA foreign_keys;
```

6. The database is now ready to use.

## Database View

### `CurrentInventory`

The `CurrentInventory` view displays active sports cards that have been purchased but have not yet been sold.

It combines data from the following tables:

- `Card`
- `PurchaseItem`
- `Purchase`
- `Seller`

This allows current inventory information to be viewed in one place without repeatedly writing the same joins.

## Database Index

### `idx_card_playername`

The database includes an index on:

```sql
Card.PlayerName
```

This index improves performance when searching or filtering cards by player name.

## Design Changes

The original practice ERD included the following entities:

- `Seller`
- `Card`
- `Buyer`
- `Sale`

The final database design was expanded to include:

- `Purchase`
- `PurchaseItem`
- `SaleItem`

`PurchaseItem` connects purchases to individual cards. This allows one purchase transaction to contain multiple cards while still storing an individual purchase price for each card.

`SaleItem` connects sales to individual cards. This allows one sale transaction to contain multiple cards while storing an individual sale price for each card.

This structure better represents real sports card transactions and reduces repeated transaction data.

## Testing

The database was successfully recreated from scratch using only:

- `schema.sql`
- `insert_data.sql`

The following tests were completed successfully:

- All tables were created.
- All sample data loaded successfully.
- Foreign key checks passed.
- The database integrity check returned `ok`.
- The `CurrentInventory` view returned records correctly.
- The `idx_card_playername` index was created successfully.
- CHECK constraints correctly rejected invalid data.

## Database Files

The project currently uses the following files:

- `schema.sql` — creates the database tables, relationships, constraints, view, and index.
- `insert_data.sql` — inserts sample data into the database.
- `README.md` — explains setup, database features, design changes, and testing.
