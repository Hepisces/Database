CREATE TABLE product.product_copy
(
    product_no CHAR(6) PRIMARY KEY,
    name       VARCHAR(15),
    price      NUMERIC(6, 2)
);

COPY product.product_copy (product_no, name, price)
    FROM 'F:\GITHUB\Database\works\6. sql\others\data.txt'
    WITH (FORMAT TEXT, DELIMITER ',', NULL '');

-- 2-1
INSERT INTO product.product(product_no, name, price)
VALUES (000666, 'cake', NULL);

-- 2-2
INSERT INTO product.product (product_no, name, price)
VALUES ('999991', 'iPhone', 999.99),
       ('999992', 'MacBook', 1299.99),
       ('999993', 'AirPods', 199.99);

-- 2-3
UPDATE product.product
SET price=price * 0.8;

-- 2-4
UPDATE product.product
SET price = CASE
                WHEN price > 100 THEN price * 1.02
                ELSE price * 1.04
    END;

-- 2-5
DELETE
FROM product.product
WHERE name LIKE '%cake%';

-- 2-6
SELECT ROUND(AVG(price), 2)
FROM product.product;

DELETE
FROM product.product
WHERE price > (SELECT AVG(price) FROM product.product);