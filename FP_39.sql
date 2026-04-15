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

-- 1. Insert Restaurants
INSERT INTO Restaurant VALUES (1, 'The Rusty Spoon'), (2, 'Pizza Paradiso');

-- 2. Insert Employees
INSERT INTO Employees VALUES (101, 'Alice Smith', 'Chef', 'alice@test.com', 1, 5551234);
INSERT INTO Employees VALUES (102, 'Bob Jones', 'Waiter', 'bob@test.com', 1, 5555678);
INSERT INTO Employees VALUES (103, 'Charlie Brown', 'Manager', 'char@test.com', 2, 5559012);

-- 3. Populate Subtypes
INSERT INTO FullTime VALUES (101, 65000);
INSERT INTO FullTime VALUES (103, 72000);
INSERT INTO PartTime VALUES (102, 25, 18.50);

-- 4. Menu & Items
INSERT INTO Menu VALUES (201, 'Burger', 12.50, 1), (202, 'Pizza', 15.00, 2);
INSERT INTO Item VALUES (301, 'Beef', 5.00, 100), (302, 'Oven', 2000.00, 1);
INSERT INTO Ingredients VALUES (301);
INSERT INTO Appliances VALUES (302);

-- 5. Orders & Relations
INSERT INTO Orders VALUES (401, 25.00, 5.00, '2026-04-08', 1);
INSERT INTO OrderMenuItem VALUES (401, 201);
INSERT INTO MenuItemUses VALUES (201, 301);
INSERT INTO RestaurantStock VALUES (1, 301), (2, 302);

