

-- COSC 465 Final Project: Sports Card Inventory and Sales System
-- DBMS: SQLite


-- Requirement 1: Filtering and Sorting
-- Shows active graded cards ordered from highest grade to lowest
-- This helps identify the highest-graded cards currently in inventory


SELECT
    CardID,
    PlayerName,
    Team,
    CardYear,
    Brand,
    CardSet,
    Grade
FROM Card
WHERE Status = 'Active'
  AND RawGraded = 'Graded'
ORDER BY Grade DESC, PlayerName ASC;

-- Requirement 2: INNER JOIN
-- Shows every purchased card and the price paid for it
-- This connects card information with its purchase record

SELECT
    c.CardID,
    c.PlayerName,
    c.Sport,
    c.Brand,
    pi.PurchasePrice
FROM Card AS c
INNER JOIN PurchaseItem AS pi
    ON c.CardID = pi.CardID
ORDER BY c.CardID;


-- Requirement 3: LEFT JOIN
-- Shows every buyer and any sales associated with that buyer
-- Buyers who have never made a purchase still appear

SELECT
    b.BuyerID,
    b.FirstName || ' ' || b.LastName AS BuyerName,
    s.SaleID,
    s.SaleDate
FROM Buyer AS b
LEFT JOIN Sale AS s
    ON b.BuyerID = s.BuyerID
ORDER BY b.BuyerID, s.SaleDate;


-- Requirement 4: Three-Table Join
-- Shows each sold card, who purchased it, the date of the sale, and the card's individual sale price

SELECT
    c.PlayerName,
    c.Sport,
    b.FirstName || ' ' || b.LastName AS BuyerName,
    s.SaleDate,
    si.SalePrice
FROM Sale AS s
INNER JOIN Buyer AS b
    ON s.BuyerID = b.BuyerID
INNER JOIN SaleItem AS si
    ON s.SaleID = si.SaleID
INNER JOIN Card AS c
    ON si.CardID = c.CardID
ORDER BY s.SaleDate;


-- Requirement 5: Aggregate Query
-- Summarizes the acquisition cost of the sports-card inventory


SELECT
    COUNT(*) AS NumberOfCardsPurchased,
    ROUND(SUM(PurchasePrice), 2) AS TotalPurchaseCost,
    ROUND(AVG(PurchasePrice), 2) AS AveragePurchasePrice,
    ROUND(MIN(PurchasePrice), 2) AS LowestPurchasePrice,
    ROUND(MAX(PurchasePrice), 2) AS HighestPurchasePrice
FROM PurchaseItem;


-- Requirement 6: GROUP BY and HAVING
-- shows sports represented by more than six cards
-- identifies the sports with the largest representation in the card database while filtering out smaller groups

SELECT
    Sport,
    COUNT(*) AS NumberOfCards
FROM Card
GROUP BY Sport
HAVING COUNT(*) > 6
ORDER BY NumberOfCards DESC;


-- Requirement 7: Subquery
-- Shows cards that cost more than the average purchase price
-- This helps identify higher-cost inventory

SELECT
    c.CardID,
    c.PlayerName,
    c.Sport,
    pi.PurchasePrice
FROM Card AS c
INNER JOIN PurchaseItem AS pi
    ON c.CardID = pi.CardID
WHERE pi.PurchasePrice > (
    SELECT AVG(PurchasePrice)
    FROM PurchaseItem
)
ORDER BY pi.PurchasePrice DESC;

-- Requirement 8: Set Operation
-- Creates one combined list of people who have participated in the business as either sellers or buyers
-- UNION removes duplicate names if someone appears in both roles

SELECT
    FirstName,
    LastName
FROM Seller

UNION

SELECT
    FirstName,
    LastName
FROM Buyer

ORDER BY LastName, FirstName;


-- Requirement 9: View
-- Uses the CurrentInventory view to display currently available cards ordered from highest purchase price to lowest
-- The view avoids rewriting joins between Card, PurchaseItem, Purchase, and Seller.

SELECT
    CardID,
    PlayerName,
    Team,
    CardYear,
    Brand,
    CardSet,
    Grade,
    PurchasePrice,
    SellerName
FROM CurrentInventory
ORDER BY PurchasePrice DESC;


