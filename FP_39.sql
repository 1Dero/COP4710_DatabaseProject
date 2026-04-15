DROP DATABASE IF EXISTS RestaurantSales;
CREATE DATABASE RestaurantSales;
USE RestaurantSales;

CREATE TABLE Restaurant(
	rid INT PRIMARY KEY NOT NULL DEFAULT 1 CHECK (rid = 1),
	name VARCHAR(50)
);

CREATE TABLE Employees(
	eid INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50),
    role VARCHAR(50),
    email VARCHAR(50),
    rid INT,
    phone INT,
    FOREIGN KEY (rid) REFERENCES Restaurant(rid)
);

CREATE TABLE PartTime(
	eid INT PRIMARY KEY,
	hours INT,
    pay FLOAT,
	FOREIGN KEY (eid) REFERENCES Employees(eid)
		ON DELETE CASCADE
);

CREATE TABLE FullTime(
	eid INT PRIMARY KEY,
	salary INT UNSIGNED,
	FOREIGN KEY (eid) REFERENCES Employees(eid)
		ON DELETE CASCADE
);


CREATE TABLE Menu(
	mid INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50),
    price FLOAT,
    rid INT,
    FOREIGN KEY (rid) REFERENCES Restaurant(rid)
);

CREATE TABLE Item(
	iid INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50),
    cost FLOAT UNSIGNED,
    quantity INT UNSIGNED
);

CREATE TABLE Ingredients(
	iid INT PRIMARY KEY,
    FOREIGN KEY (iid) REFERENCES Item(iid)
        On DELETE CASCADE
);

CREATE TABLE Appliances(
	aid INT PRIMARY KEY,
    FOREIGN KEY (aid) REFERENCES Item(iid)
        On DELETE CASCADE
);


CREATE TABLE Orders(
	oid INT AUTO_INCREMENT PRIMARY KEY,
    price FLOAT,
    tip FLOAT DEFAULT 0,
    o_date DATE,
    rid INT,
    FOREIGN KEY (rid) REFERENCES Restaurant(rid)
);


CREATE TABLE OrderMenuItem(
	oid INT,
    mid INT,
    FOREIGN KEY (mid) REFERENCES Menu(mid),
    FOREIGN KEY (oid) REFERENCES Orders(oid)
		ON DELETE CASCADE
);

CREATE TABLE MenuItemUses(
	mid INT,
    iid INT,
    FOREIGN KEY (mid) REFERENCES Menu(mid),
    FOREIGN KEY (iid) REFERENCES Ingredients(iid)
);

CREATE TABLE RestaurantStock(
	rid INT,
    iid INT,
    FOREIGN KEY (rid) REFERENCES Restaurant(rid),
    FOREIGN KEY (iid) REFERENCES Item(iid)
);

CREATE VIEW EmployeeView AS
-- Part 1: Select Full-Time Employees
SELECT 
    e.name, 
    e.role, 
    e.phone,
    e.email,
    'Full-Time' AS employment_type, 
    f.salary AS annual_pay_or_hourly_rate, 
    NULL AS weekly_hours
FROM Employees e
JOIN FullTime f ON e.eid = f.eid

UNION ALL

-- Part 2: Select Part-Time Employees
SELECT 
    e.name, 
    e.role, 
    e.phone,
    e.email,
    'Part-Time' AS employment_type, 
    p.pay AS annual_pay_or_hourly_rate, 
    p.hours AS weekly_hours
FROM Employees e
JOIN PartTime p ON e.eid = p.eid;

CREATE VIEW RestaurantSummary AS
SELECT
    r.name AS restaurant,
    COALESCE(rev.revenue, 0) AS revenue,
    COALESCE(emp.employee_cost, 0) + COALESCE(ing.ingredient_cost, 0) AS cost,
    COALESCE(cap.capital_values, 0) AS capital_values
FROM Restaurant r

LEFT JOIN (
    SELECT
        o.rid,
        SUM(o.price + o.tip) AS revenue
    FROM Orders o
    GROUP BY o.rid
) rev ON r.rid = rev.rid

LEFT JOIN (
    SELECT
        e.rid,
        COALESCE(SUM(f.salary), 0) + COALESCE(SUM(p.hours * p.pay), 0) AS employee_cost
    FROM Employees e
    LEFT JOIN FullTime f ON e.eid = f.eid
    LEFT JOIN PartTime p ON e.eid = p.eid
    GROUP BY e.rid
) emp ON r.rid = emp.rid

LEFT JOIN (
    SELECT
        rs.rid,
        SUM(i.cost * i.quantity) AS ingredient_cost
    FROM RestaurantStock rs
    JOIN Ingredients g ON rs.iid = g.iid
    JOIN Item i ON g.iid = i.iid
    GROUP BY rs.rid
) ing ON r.rid = ing.rid

LEFT JOIN (
    SELECT
        rs.rid,
        SUM(i.cost * i.quantity) AS capital_values
    FROM RestaurantStock rs
    JOIN Item i ON rs.iid = i.iid
    GROUP BY rs.rid
) cap ON r.rid = cap.rid;

-- =========================================
-- Example Data for RestaurantSales
-- =========================================

-- Restaurant
INSERT INTO Restaurant (rid, name)
VALUES (1, 'Knight Bites');

-- =========================================
-- Employees
-- =========================================

INSERT INTO Employees (name, role, email, rid, phone)
VALUES
('Alice Chen', 'Manager', 'alice@knightbites.com', 1, 4071111001),
('Bob Smith', 'Chef', 'bob@knightbites.com', 1, 4071111002),
('Carol Davis', 'Waiter', 'carol@knightbites.com', 1, 4071111003),
('David Lee', 'Cashier', 'david@knightbites.com', 1, 4071111004),
('Emma Brown', 'Dishwasher', 'emma@knightbites.com', 1, 4071111005),
('Frank Green', 'Waiter', 'frank@knightbites.com', 1, 4071111006);

-- Full-time employees
INSERT INTO FullTime (eid, salary)
VALUES
(1, 60000),
(2, 50000);

-- Part-time employees
INSERT INTO PartTime (eid, hours, pay)
VALUES
(3, 25, 15.50),
(4, 20, 14.00),
(5, 18, 13.50),
(6, 22, 15.00);

-- =========================================
-- Menu
-- =========================================

INSERT INTO Menu (name, price, rid)
VALUES
('Classic Burger', 10.99, 1),
('Cheese Pizza', 14.50, 1),
('Chicken Wrap', 9.75, 1),
('Caesar Salad', 8.25, 1),
('French Fries', 3.99, 1),
('Milkshake', 4.50, 1);

-- =========================================
-- Item
-- cost = purchase cost per unit
-- quantity = how many units currently in stock
-- =========================================

INSERT INTO Item (name, cost, quantity)
VALUES
('Burger Bun', 0.50, 100),          -- iid = 1
('Beef Patty', 2.00, 80),           -- iid = 2
('Cheese Slice', 0.30, 120),        -- iid = 3
('Pizza Dough', 1.50, 40),          -- iid = 4
('Tomato Sauce', 0.80, 50),         -- iid = 5
('Chicken Breast', 2.50, 60),       -- iid = 6
('Tortilla', 0.40, 70),             -- iid = 7
('Romaine Lettuce', 1.20, 30),      -- iid = 8
('Potato', 0.25, 200),              -- iid = 9
('Milk', 1.00, 40),                 -- iid = 10
('Ice Cream Mix', 2.20, 25),        -- iid = 11
('Blender', 75.00, 2),              -- iid = 12
('Oven', 900.00, 1),                -- iid = 13
('Deep Fryer', 250.00, 1),          -- iid = 14
('Grill', 600.00, 1);               -- iid = 15

-- =========================================
-- Ingredients
-- These are Item subtypes
-- =========================================

INSERT INTO Ingredients (iid)
VALUES
(1), (2), (3), (4), (5),
(6), (7), (8), (9), (10), (11);

-- =========================================
-- Appliances
-- These are Item subtypes
-- =========================================

INSERT INTO Appliances (aid)
VALUES
(12), (13), (14), (15);

-- =========================================
-- RestaurantStock
-- What items belong to the restaurant
-- =========================================

INSERT INTO RestaurantStock (rid, iid)
VALUES
(1, 1), (1, 2), (1, 3), (1, 4), (1, 5),
(1, 6), (1, 7), (1, 8), (1, 9), (1, 10),
(1, 11), (1, 12), (1, 13), (1, 14), (1, 15);

-- =========================================
-- MenuItemUses
-- Which ingredients each menu item uses
-- =========================================

-- Classic Burger (mid = 1)
INSERT INTO MenuItemUses (mid, iid)
VALUES
(1, 1),  -- bun
(1, 2),  -- beef patty
(1, 3);  -- cheese slice

-- Cheese Pizza (mid = 2)
INSERT INTO MenuItemUses (mid, iid)
VALUES
(2, 4),  -- pizza dough
(2, 5),  -- tomato sauce
(2, 3);  -- cheese slice

-- Chicken Wrap (mid = 3)
INSERT INTO MenuItemUses (mid, iid)
VALUES
(3, 6),  -- chicken breast
(3, 7),  -- tortilla
(3, 8);  -- lettuce

-- Caesar Salad (mid = 4)
INSERT INTO MenuItemUses (mid, iid)
VALUES
(4, 8),  -- lettuce
(4, 3);  -- cheese slice

-- French Fries (mid = 5)
INSERT INTO MenuItemUses (mid, iid)
VALUES
(5, 9);  -- potato

-- Milkshake (mid = 6)
INSERT INTO MenuItemUses (mid, iid)
VALUES
(6, 10), -- milk
(6, 11); -- ice cream mix

-- =========================================
-- Orders
-- =========================================

INSERT INTO Orders (price, tip, o_date, rid)
VALUES
(10.99, 2.00, '2026-04-10', 1),  -- oid = 1
(18.49, 3.50, '2026-04-10', 1),  -- oid = 2
(14.25, 0.00, '2026-04-11', 1),  -- oid = 3
(28.24, 5.00, '2026-04-11', 1),  -- oid = 4
(8.25, 1.25, '2026-04-12', 1),   -- oid = 5
(19.49, 4.00, '2026-04-12', 1);  -- oid = 6

-- =========================================
-- OrderMenuItem
-- Which menu items were included in each order
-- =========================================

-- Order 1: Classic Burger
INSERT INTO OrderMenuItem (oid, mid)
VALUES
(1, 1);

-- Order 2: Cheese Pizza + Milkshake
INSERT INTO OrderMenuItem (oid, mid)
VALUES
(2, 2),
(2, 6);

-- Order 3: Chicken Wrap + French Fries + Milkshake
INSERT INTO OrderMenuItem (oid, mid)
VALUES
(3, 3),
(3, 5),
(3, 6);

-- Order 4: 2 Burgers + 1 Caesar Salad + 1 Fries
INSERT INTO OrderMenuItem (oid, mid)
VALUES
(4, 1),
(4, 1),
(4, 4),
(4, 5);

-- Order 5: Caesar Salad
INSERT INTO OrderMenuItem (oid, mid)
VALUES
(5, 4);

-- Order 6: Cheese Pizza + French Fries + Milkshake
INSERT INTO OrderMenuItem (oid, mid)
VALUES
(6, 2),
(6, 5),
(6, 6);

