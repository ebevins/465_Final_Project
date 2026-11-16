-- COSC 465 Final Project: Sports Card Inventory and Sales System
-- DBMS: SQLite


PRAGMA foreign_keys = ON;

-- This transaction demonstrates recording a sale for CardID 1
-- The sale record, sale item, and card status change should succeed or fail together

BEGIN TRANSACTION;

-- Create a new sale for BuyerID 8

INSERT INTO Sale
(SaleID, BuyerID, SaleDate, PaymentType, Fees, ShippingCost)
VALUES
(9, 8, '2026-11-02', 'PayPal', 15.00, 6.00);

-- Add CardID 1 to the sale

INSERT INTO SaleItem
(SaleItemID, SaleID, CardID, SalePrice)
VALUES
(8, 9, 1, 575.00);

-- Mark the card as sold

UPDATE Card
SET Status = 'Sold'
WHERE CardID = 1;

-- Roll back the demonstration so the grader can run the script without permanently changing the sample data

ROLLBACK;

