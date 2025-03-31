-- 1-1
SELECT dept_name, MIN(salary)
FROM instructor;
-- 1-1-corrected
SELECT dept_name, MIN(salary)
FROM instructor
GROUP BY dept_name;

-- 1-2
SELECT dept_name, MIN(salary)
FROM instructor
GROUP BY dept_name
HAVING name LIKE '%at%';
-- 1-2-corrected
SELECT dept_name, MIN(salary)
FROM instructor
WHERE name LIKE '%at%'
GROUP BY dept_name

-- 1-3
SELECT dept_name
FROM instructor
WHERE AVG(salary) > 20000;
-- 1-3-corrected
SELECT dept_name
FROM instructor
GROUP BY dept_name
HAVING AVG(salary) > 20000;

-- 2-1
-- 解法一：ORDER BY 和 LIMIT子句
SELECT *
FROM instructor
ORDER BY salary DESC
LIMIT 1;

-- 解法二：WHERE子句
SELECT *
FROM instructor
WHERE salary = (SELECT MAX(salary) FROM instructor);

-- 解法三：窗口函数ROW_NUMBER()
SELECT id, name, dept_name, salary
FROM (SELECT *,
             ROW_NUMBER() OVER (ORDER BY salary DESC ) AS rk
      FROM instructor) a
WHERE rk = 1;

-- 解法四：窗口函数RANK()
SELECT id, name, dept_name, salary
FROM (SELECT *,
             RANK() OVER (ORDER BY salary DESC) AS rk
      FROM instructor) a
WHERE rk = 1;

-- 解法五：窗口函数DENSE_RANK()
SELECT id, name, dept_name, salary
FROM (SELECT *,
             DENSE_RANK() OVER (ORDER BY salary DESC) AS rk
      FROM instructor) a
WHERE rk = 1;

-- 解法六：HAVING子句
SELECT id, name, dept_name, salary
FROM instructor
GROUP BY id, name, dept_name, salary
HAVING salary = (SELECT MAX(salary) FROM instructor);

-- 解法七：ALL关键字
SELECT *
FROM instructor
WHERE salary >= ALL (SELECT salary FROM instructor);

-- 解法八： JOIN子句
SELECT i.*
FROM instructor i
         JOIN (SELECT MAX(salary) AS max_salary FROM instructor) m
              ON i.salary = m.max_salary;


-- 2-2
INSERT INTO instructor (id, name, dept_name, salary)
VALUES (11451, 'Test', NULL, 124651.41);

-- 解法一：WHERE子句
SELECT *
FROM instructor
WHERE salary = (SELECT MAX(salary) FROM instructor);

-- 解法二：窗口函数RANK()
SELECT id, name, dept_name, salary
FROM (SELECT *,
             RANK() OVER (ORDER BY salary DESC) AS rk
      FROM instructor) a
WHERE rk = 1;


-- 解法三：HAVING子句
SELECT id, name, dept_name, salary
FROM instructor
GROUP BY id, name, dept_name, salary
HAVING salary = (SELECT MAX(salary) FROM instructor);

-- 解法四：ALL关键字
SELECT *
FROM instructor
WHERE salary >= ALL (SELECT salary FROM instructor);

-- 解法五： JOIN子句
SELECT i.*
FROM instructor i
         JOIN (SELECT MAX(salary) AS max_salary FROM instructor) m
              ON i.salary = m.max_salary;

-- 2-3
SELECT 1 IN (1);

SELECT 1 = (1);

SELECT (1, 2) = (1, 2), (1, 2) = (2, 1);

SELECT (1) IN (1, 2);



