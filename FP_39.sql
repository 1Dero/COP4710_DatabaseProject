DROP DATABASE IF EXISTS RestaurantSales;
CREATE DATABASE RestaurantSales;
USE RestaurantSales;

-- The singleton table remains, but acts only to store the restaurant's global configuration/name.
CREATE TABLE Restaurant(
    rid INT PRIMARY KEY NOT NULL DEFAULT 1 CHECK (rid = 1),
    name VARCHAR(50)
);

-- Removed 'rid' and its foreign key
CREATE TABLE Employees(
    eid INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50),
    role VARCHAR(50),
    email VARCHAR(50),
    phone VARCHAR(50)
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

-- Removed 'rid' and its foreign key
CREATE TABLE Menu(
    mid INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50),
    price FLOAT
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
        ON DELETE CASCADE
);

CREATE TABLE Appliances(
    iid INT PRIMARY KEY,
    FOREIGN KEY (iid) REFERENCES Item(iid)
        ON DELETE CASCADE
);

-- Removed 'rid' and its foreign key
CREATE TABLE Orders(
    oid INT AUTO_INCREMENT PRIMARY KEY,
    price FLOAT,
    tip FLOAT DEFAULT 0,
    o_date DATE
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

-- View remains unchanged as it did not rely on 'rid'
CREATE VIEW EmployeeView AS
-- Part 1: Select Full-Time Employees
SELECT 
    e.name, 
    e.role, 
    e.phone,
    e.email,
    'Full-Time' AS employment_type, 
    f.salary AS annual_pay, 
    NULL AS hourly_rate,
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
    NULL AS annual_pay,
    p.pay AS annual_pay_or_hourly_rate, 
    p.hours AS weekly_hours
FROM Employees e
JOIN PartTime p ON e.eid = p.eid;

-- View completely refactored to remove 'rid' groupings and the undefined RestaurantStock table
CREATE VIEW RestaurantSummary AS
SELECT
    r.name AS restaurant,
    ROUND(COALESCE(rev.revenue, 0), 2) AS revenue,
    ROUND(COALESCE(emp.employee_cost, 0) + COALESCE(ing.ingredient_cost, 0), 2) AS cost,
    ROUND(COALESCE(cap.capital_values, 0), 2) AS capital_values
FROM Restaurant r

-- Global revenue aggregation
CROSS JOIN (
    SELECT
        SUM(price + tip) AS revenue
    FROM Orders
) rev

-- Global employee cost aggregation
CROSS JOIN (
    SELECT
        COALESCE(SUM(f.salary), 0) + COALESCE(SUM(p.hours * p.pay), 0) AS employee_cost
    FROM Employees e
    LEFT JOIN FullTime f ON e.eid = f.eid
    LEFT JOIN PartTime p ON e.eid = p.eid
) emp

-- Global ingredient cost aggregation
CROSS JOIN (
    SELECT
        SUM(i.cost * i.quantity) AS ingredient_cost
    FROM Ingredients g
    JOIN Item i ON g.iid = i.iid
) ing

-- Global capital value aggregation
CROSS JOIN (
    SELECT
        SUM(cost * quantity) AS capital_values
    FROM Item
) cap;
-- =========================================================
-- 1. Restaurant Configuration
-- =========================================================
INSERT INTO Restaurant (rid, name) 
VALUES (1, '63 South');

-- =========================================================
-- 2. Employees (Base Table)
-- =========================================================
INSERT INTO Employees (eid, name, role, email, phone) VALUES 
(1, 'Gordon Ramsay', 'Head Chef', 'gramsay@goldenfork.com', '555-0101'),
(2, 'Alice Waters', 'General Manager', 'awaters@goldenfork.com', '555-0102'),
(3, 'David Chang', 'Sous Chef', 'dchang@goldenfork.com', '555-0103'),
(4, 'Samin Nosrat', 'Line Cook', 'snosrat@goldenfork.com', '555-0104'),
(5, 'John Doe', 'Server', 'jdoe@goldenfork.com', '555-0201'),
(6, 'Jane Smith', 'Server', 'jsmith@goldenfork.com', '555-0202'),
(7, 'Mike Johnson', 'Bartender', 'mjohnson@goldenfork.com', '555-0203'),
(8, 'Emily Davis', 'Host', 'edavis@goldenfork.com', '555-0204'),
(9, 'Chris Wilson', 'Dishwasher', 'cwilson@goldenfork.com', '555-0205'),
(10, 'Sarah Brown', 'Busser', 'sbrown@goldenfork.com', '555-0206');

-- =========================================================
-- 3. Full-Time & Part-Time Employees
-- =========================================================
-- Full-time employees (Salaried)
INSERT INTO FullTime (eid, salary) VALUES 
(1, 95000), -- Gordon
(2, 80000), -- Alice
(3, 65000), -- David
(4, 55000); -- Samin

-- Part-time employees (Hourly)
INSERT INTO PartTime (eid, hours, pay) VALUES 
(5, 30, 15.50), -- John
(6, 25, 15.50), -- Jane
(7, 35, 18.00), -- Mike
(8, 20, 14.00), -- Emily
(9, 40, 16.00), -- Chris
(10, 20, 13.50); -- Sarah

-- =========================================================
-- 4. Inventory Items (Appliances & Ingredients)
-- =========================================================
INSERT INTO Item (iid, name, cost, quantity) VALUES 
-- Appliances (IDs 1-4)
(1, 'Industrial Oven', 5000.00, 2),
(2, 'Stand Mixer', 800.00, 3),
(3, 'Walk-in Fridge', 8500.00, 1),
(4, 'Espresso Machine', 3200.00, 1),

-- Ingredients (IDs 5-15)
(5, 'Wagyu Beef Patty', 8.50, 150),
(6, 'Brioche Bun', 0.80, 200),
(7, 'Cheddar Cheese', 0.50, 300),
(8, 'Romaine Lettuce', 1.20, 50),
(9, 'Truffle Oil', 25.00, 10),
(10, 'Pasta (Fettuccine)', 1.50, 100),
(11, 'Heavy Cream', 3.00, 40),
(12, 'Parmesan Cheese', 5.00, 30),
(13, 'Chicken Breast', 3.50, 120),
(14, 'Potatoes', 0.40, 500),
(15, 'Craft Beer Keg', 120.00, 5);

-- =========================================================
-- 5. Sub-categorizing Items
-- =========================================================
INSERT INTO Appliances (iid) VALUES (1), (2), (3), (4);

INSERT INTO Ingredients (iid) VALUES 
(5), (6), (7), (8), (9), (10), (11), (12), (13), (14), (15);

-- =========================================================
-- 6. Menu Items
-- =========================================================
INSERT INTO Menu (mid, name, price) VALUES 
(1, 'The Golden Burger', 22.00),
(2, 'Truffle Fries', 12.00),
(3, 'Chicken Alfredo', 24.00),
(4, 'Caesar Salad', 14.00),
(5, 'Craft Beer Pint', 8.00);

-- =========================================================
-- 7. Menu Item Ingredients Mapping
-- =========================================================
INSERT INTO MenuItemUses (mid, iid) VALUES 
(1, 5),  -- Burger uses Wagyu
(1, 6),  -- Burger uses Bun
(1, 7),  -- Burger uses Cheddar
(1, 8),  -- Burger uses Lettuce
(2, 14), -- Fries use Potatoes
(2, 9),  -- Fries use Truffle Oil
(3, 10), -- Alfredo uses Pasta
(3, 11), -- Alfredo uses Cream
(3, 12), -- Alfredo uses Parmesan
(3, 13), -- Alfredo uses Chicken
(4, 8),  -- Salad uses Lettuce
(4, 12), -- Salad uses Parmesan
(5, 15); -- Pint uses Beer Keg

-- =========================================================
-- 8. Orders
-- =========================================================
-- Prices are calculated sums of the menu items for realism
INSERT INTO Orders (oid, price, tip, o_date) VALUES 
(1, 46.00, 9.20, '2023-10-01'), -- Burger, Alfredo
(2, 34.00, 6.00, '2023-10-01'), -- Burger, Fries
(3, 16.00, 3.00, '2023-10-01'), -- Pint x2
(4, 38.00, 8.00, '2023-10-02'), -- Alfredo, Salad
(5, 66.00, 15.00, '2023-10-02'), -- Burger x2, Fries x1, Beer x1
(6, 14.00, 2.50, '2023-10-02'), -- Salad
(7, 88.00, 20.00, '2023-10-03'), -- Alfredo x2, Salad x1, Beer x2
(8, 22.00, 4.00, '2023-10-03'), -- Burger
(9, 44.00, 10.00, '2023-10-04'), -- Burger x2
(10, 20.00, 5.00, '2023-10-04'); -- Fries, Beer

-- =========================================================
-- 9. Order Menu Items (Mapping what was ordered)
-- =========================================================
INSERT INTO OrderMenuItem (oid, mid) VALUES 
-- Order 1: Burger, Alfredo
(1, 1), (1, 3),
-- Order 2: Burger, Fries
(2, 1), (2, 2),
-- Order 3: 2x Beer
(3, 5), (3, 5),
-- Order 4: Alfredo, Salad
(4, 3), (4, 4),
-- Order 5: 2x Burger, Fries, Beer
(5, 1), (5, 1), (5, 2), (5, 5),
-- Order 6: Salad
(6, 4),
-- Order 7: 2x Alfredo, Salad, 2x Beer
(7, 3), (7, 3), (7, 4), (7, 5), (7, 5),
-- Order 8: Burger
(8, 1),
-- Order 9: 2x Burger
(9, 1), (9, 1),
-- Order 10: Fries, Beer
(10, 2), (10, 5);