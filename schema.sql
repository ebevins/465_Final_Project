

-- COSC 465 Final Project: Sports Card Inventory and Sales System
-- DBMS: SQLite

-- Enable foreign-key enforcement in SQLite
PRAGMA foreign_keys = ON;


-- CLEANUP
-- Allows the database to be recreated from scratch

DROP VIEW IF EXISTS CurrentInventory;

DROP TABLE IF EXISTS SaleItem;
DROP TABLE IF EXISTS Sale;
DROP TABLE IF EXISTS PurchaseItem;
DROP TABLE IF EXISTS Purchase;
DROP TABLE IF EXISTS Card;
DROP TABLE IF EXISTS Buyer;
DROP TABLE IF EXISTS Seller;


-- SELLER
-- Stores people or businesses cards are purchased from

CREATE TABLE Seller (
    SellerID INTEGER PRIMARY KEY,
    FirstName TEXT NOT NULL,
    LastName TEXT NOT NULL,
    Email TEXT,
    SellerType TEXT NOT NULL DEFAULT 'Individual'
        CHECK (SellerType IN ('Individual', 'Dealer', 'Store', 'Online'))
);


-- BUYER
-- Stores customers who purchase cards

CREATE TABLE Buyer (
    BuyerID INTEGER PRIMARY KEY,
    FirstName TEXT NOT NULL,
    LastName TEXT NOT NULL,
    Email TEXT,
    BuyerType TEXT NOT NULL DEFAULT 'Individual'
        CHECK (BuyerType IN ('Individual', 'Dealer', 'Store', 'Online'))
);


-- CARD
-- Stores information about each individual sports card

CREATE TABLE Card (
    CardID INTEGER PRIMARY KEY,
    Sport TEXT NOT NULL,
    PlayerName TEXT NOT NULL,
    Team TEXT,
    CardYear INTEGER NOT NULL
        CHECK (CardYear >= 1900),
    Brand TEXT NOT NULL,
    CardSet TEXT,
    CardNumber TEXT,
    Description TEXT,
    RawGraded TEXT NOT NULL DEFAULT 'Raw'
        CHECK (RawGraded IN ('Raw', 'Graded')),
    GradingCompany TEXT,
    Grade REAL
        CHECK (Grade IS NULL OR (Grade >= 1 AND Grade <= 10)),
    SerialNumber TEXT,
    Status TEXT NOT NULL DEFAULT 'Active'
        CHECK (Status IN ('Active', 'Sold', 'Shipped', 'Archived'))
);


-- PURCHASE
-- Represents an overall transaction with a seller


CREATE TABLE Purchase (
    PurchaseID INTEGER PRIMARY KEY,
    SellerID INTEGER NOT NULL,
    PurchaseDate TEXT NOT NULL,
    PaymentType TEXT,
    TotalAmount REAL NOT NULL
        CHECK (TotalAmount >= 0),

    FOREIGN KEY (SellerID)
        REFERENCES Seller(SellerID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);


-- PURCHASE ITEM
-- Junction table connecting purchases and cards
-- Stores the price assigned to each card in a purchase


CREATE TABLE PurchaseItem (
    PurchaseItemID INTEGER PRIMARY KEY,
    PurchaseID INTEGER NOT NULL,
    CardID INTEGER NOT NULL,
    PurchasePrice REAL NOT NULL
        CHECK (PurchasePrice >= 0),

    FOREIGN KEY (PurchaseID)
        REFERENCES Purchase(PurchaseID)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    FOREIGN KEY (CardID)
        REFERENCES Card(CardID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    UNIQUE (PurchaseID, CardID)
);


-- SALE
-- Represents an overall transaction with a buyer


CREATE TABLE Sale (
    SaleID INTEGER PRIMARY KEY,
    BuyerID INTEGER NOT NULL,
    SaleDate TEXT NOT NULL,
    PaymentType TEXT,
    Fees REAL NOT NULL DEFAULT 0
        CHECK (Fees >= 0),
    ShippingCost REAL NOT NULL DEFAULT 0
        CHECK (ShippingCost >= 0),

    FOREIGN KEY (BuyerID)
        REFERENCES Buyer(BuyerID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);


-- SALE ITEM
-- Junction table connecting sales and cards
-- Stores the sale price of each card in a transaction

CREATE TABLE SaleItem (
    SaleItemID INTEGER PRIMARY KEY,
    SaleID INTEGER NOT NULL,
    CardID INTEGER NOT NULL,
    SalePrice REAL NOT NULL
        CHECK (SalePrice >= 0),

    FOREIGN KEY (SaleID)
        REFERENCES Sale(SaleID)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    FOREIGN KEY (CardID)
        REFERENCES Card(CardID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    UNIQUE (SaleID, CardID)
);


-- VIEW: CURRENT INVENTORY
-- Shows active cards that have been purchased but have not been sold


CREATE VIEW CurrentInventory AS
SELECT
    c.CardID,
    c.Sport,
    c.PlayerName,
    c.Team,
    c.CardYear,
    c.Brand,
    c.CardSet,
    c.CardNumber,
    c.Description,
    c.RawGraded,
    c.GradingCompany,
    c.Grade,
    c.SerialNumber,
    c.Status,
    pi.PurchasePrice,
    p.PurchaseDate,
    s.FirstName || ' ' || s.LastName AS SellerName
FROM Card c
JOIN PurchaseItem pi
    ON c.CardID = pi.CardID
JOIN Purchase p
    ON pi.PurchaseID = p.PurchaseID
JOIN Seller s
    ON p.SellerID = s.SellerID
WHERE c.Status = 'Active'
  AND NOT EXISTS (
      SELECT 1
      FROM SaleItem si
      WHERE si.CardID = c.CardID
  );



-- INDEX
-- Speeds up common searches for cards by player name


CREATE INDEX idx_card_playername
ON Card(PlayerName);



