
-- COSC 465 Final Project: Sports Card Inventory and Sales System
-- DBMS: SQLite

PRAGMA foreign_keys = ON;

-- SELLERS

INSERT INTO Seller
(SellerID, FirstName, LastName, Email, SellerType)
VALUES
(1, 'Mike', 'Turner', 'mturner@example.com', 'Dealer'),
(2, 'Sarah', 'Collins', 'scollins@example.com', 'Individual'),
(3, 'David', 'Nguyen', 'dnguyen@example.com', 'Store'),
(4, 'Emily', 'Brooks', 'ebrooks@example.com', 'Online'),
(5, 'Jason', 'Reed', 'jreed@example.com', 'Dealer'),
(6, 'Laura', 'Mitchell', 'lmitchell@example.com', 'Individual');


-- BUYERS

INSERT INTO Buyer
(BuyerID, FirstName, LastName, Email, BuyerType)
VALUES
(1, 'Ryan', 'Miller', 'rmiller@example.com', 'Individual'),
(2, 'Chris', 'Young', 'cyoung@example.com', 'Dealer'),
(3, 'Amanda', 'Lewis', 'alewis@example.com', 'Individual'),
(4, 'Kevin', 'Hall', 'khall@example.com', 'Store'),
(5, 'Nicole', 'Adams', 'nadams@example.com', 'Online'),
(6, 'Brian', 'Scott', 'bscott@example.com', 'Individual'),
(7, 'Olivia', 'Green', 'ogreen@example.com', 'Dealer'),
(8, 'Ethan', 'Baker', 'ebaker@example.com', 'Individual');


-- CARDS

INSERT INTO Card
(CardID, Sport, PlayerName, Team, CardYear, Brand, CardSet,
 CardNumber, Description, RawGraded, GradingCompany, Grade,
 SerialNumber, Status)
VALUES
(1, 'Football', 'Patrick Mahomes', 'Kansas City Chiefs', 2018, 'Panini', 'Spectra',
 '12', 'Neon Green parallel', 'Graded', 'BGS', 8.5, '148/299', 'Active'),

(2, 'Football', 'Josh Allen', 'Buffalo Bills', 2020, 'Panini', 'Prizm',
 '103', 'Silver Prizm', 'Graded', 'PSA', 10, NULL, 'Sold'),

(3, 'Basketball', 'LeBron James', 'Los Angeles Lakers', 2021, 'Panini', 'Select',
 '25', 'Courtside Silver', 'Graded', 'PSA', 9, NULL, 'Active'),

(4, 'Basketball', 'Stephen Curry', 'Golden State Warriors', 2022, 'Panini', 'Prizm',
 '154', 'Red Ice parallel', 'Raw', NULL, NULL, NULL, 'Active'),

(5, 'Baseball', 'Shohei Ohtani', 'Los Angeles Dodgers', 2024, 'Topps', 'Chrome',
 '1', 'Refractor', 'Graded', 'PSA', 10, NULL, 'Sold'),

(6, 'Baseball', 'Aaron Judge', 'New York Yankees', 2023, 'Topps', 'Series 1',
 '62', 'Gold parallel', 'Raw', NULL, NULL, '1145/2023', 'Active'),

(7, 'Football', 'Joe Burrow', 'Cincinnati Bengals', 2020, 'Panini', 'Mosaic',
 '201', 'Rookie card', 'Graded', 'PSA', 9, NULL, 'Sold'),

(8, 'Football', 'Justin Jefferson', 'Minnesota Vikings', 2020, 'Panini', 'Optic',
 '163', 'Rated Rookie Holo', 'Graded', 'PSA', 10, NULL, 'Active'),

(9, 'Basketball', 'Luka Doncic', 'Dallas Mavericks', 2019, 'Panini', 'Prizm',
 '75', 'Green Prizm', 'Graded', 'PSA', 9, NULL, 'Sold'),

(10, 'Basketball', 'Jayson Tatum', 'Boston Celtics', 2022, 'Panini', 'Select',
 '13', 'Premier Level Blue', 'Raw', NULL, NULL, '22/99', 'Active'),

(11, 'Baseball', 'Ronald Acuna Jr.', 'Atlanta Braves', 2021, 'Topps', 'Chrome',
 '45', 'Pink Refractor', 'Graded', 'PSA', 10, NULL, 'Active'),

(12, 'Baseball', 'Juan Soto', 'New York Mets', 2024, 'Topps', 'Heritage',
 '100', 'Chrome parallel', 'Raw', NULL, NULL, '47/575', 'Sold'),

(13, 'Football', 'Lamar Jackson', 'Baltimore Ravens', 2019, 'Panini', 'Select',
 '88', 'Field Level Silver', 'Graded', 'PSA', 9, NULL, 'Active'),

(14, 'Football', 'C.J. Stroud', 'Houston Texans', 2023, 'Panini', 'Prizm',
 '339', 'Rookie Silver', 'Graded', 'PSA', 10, NULL, 'Sold'),

(15, 'Basketball', 'Victor Wembanyama', 'San Antonio Spurs', 2023, 'Panini', 'Prizm',
 '136', 'Rookie card', 'Graded', 'PSA', 10, NULL, 'Active'),

(16, 'Basketball', 'Anthony Edwards', 'Minnesota Timberwolves', 2020, 'Panini', 'Optic',
 '151', 'Rated Rookie', 'Graded', 'PSA', 9, NULL, 'Active'),

(17, 'Baseball', 'Mookie Betts', 'Los Angeles Dodgers', 2022, 'Topps', 'Chrome',
 '50', 'Purple Refractor', 'Raw', NULL, NULL, '188/250', 'Archived'),

(18, 'Football', 'Brock Purdy', 'San Francisco 49ers', 2022, 'Panini', 'Prizm',
 '353', 'Rookie card', 'Graded', 'PSA', 10, NULL, 'Sold'),

(19, 'Basketball', 'Nikola Jokic', 'Denver Nuggets', 2021, 'Panini', 'Mosaic',
 '15', 'Genesis parallel', 'Graded', 'PSA', 10, NULL, 'Active'),

(20, 'Baseball', 'Bobby Witt Jr.', 'Kansas City Royals', 2022, 'Topps', 'Chrome',
 '221', 'Rookie Refractor', 'Graded', 'PSA', 9, NULL, 'Active');


-- PURCHASES

INSERT INTO Purchase
(PurchaseID, SellerID, PurchaseDate, PaymentType, TotalAmount)
VALUES
(1, 1, '2026-01-10', 'Cash', 950.00),
(2, 2, '2026-02-14', 'PayPal', 620.00),
(3, 3, '2026-03-08', 'Credit Card', 780.00),
(4, 4, '2026-04-20', 'Venmo', 525.00),
(5, 5, '2026-05-16', 'Cash', 1200.00),
(6, 1, '2026-06-05', 'PayPal', 860.00),
(7, 6, '2026-07-11', 'Cash', 475.00),
(8, 3, '2026-08-22', 'Credit Card', 690.00);


-- PURCHASE ITEMS

INSERT INTO PurchaseItem
(PurchaseItemID, PurchaseID, CardID, PurchasePrice)
VALUES
(1, 1, 1, 425.00),
(2, 1, 2, 275.00),
(3, 1, 3, 250.00),

(4, 2, 4, 120.00),
(5, 2, 5, 300.00),
(6, 2, 6, 200.00),

(7, 3, 7, 240.00),
(8, 3, 8, 290.00),
(9, 3, 9, 250.00),

(10, 4, 10, 175.00),
(11, 4, 11, 185.00),
(12, 4, 12, 165.00),

(13, 5, 13, 350.00),
(14, 5, 14, 500.00),
(15, 5, 15, 350.00),

(16, 6, 16, 260.00),
(17, 6, 17, 180.00),
(18, 6, 18, 420.00),

(19, 7, 19, 300.00),
(20, 7, 20, 175.00);


-- SALES

INSERT INTO Sale
(SaleID, BuyerID, SaleDate, PaymentType, Fees, ShippingCost)
VALUES
(1, 1, '2026-02-05', 'PayPal', 18.00, 6.00),
(2, 2, '2026-03-12', 'Cash', 0.00, 0.00),
(3, 3, '2026-04-18', 'Credit Card', 22.00, 7.00),
(4, 1, '2026-06-02', 'PayPal', 30.00, 8.00),
(5, 5, '2026-07-19', 'Venmo', 12.00, 5.00),
(6, 6, '2026-08-04', 'Cash', 0.00, 4.00),
(7, 7, '2026-09-10', 'PayPal', 28.00, 7.00),
(8, 2, '2026-09-28', 'Credit Card', 20.00, 6.00);


-- SALE ITEMS
-- Each physical card appears at most once here

INSERT INTO SaleItem
(SaleItemID, SaleID, CardID, SalePrice)
VALUES
(1, 1, 2, 340.00),
(2, 1, 5, 390.00),

(3, 2, 7, 315.00),

(4, 3, 9, 325.00),
(5, 3, 12, 220.00),

(6, 4, 14, 650.00),

(7, 5, 18, 525.00);

