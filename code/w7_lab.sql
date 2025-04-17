-- 1.1
SELECT id, COUNT(sec_id)
FROM teaches
GROUP BY id;

-- 1.2
SELECT instructor.id, COUNT(sec_id) tot
FROM instructor
         LEFT JOIN teaches ON instructor.id = teaches.id
GROUP BY instructor.id;

-- 1.3
SELECT id,
       (SELECT COUNT(sec_id)
        FROM teaches
        WHERE teaches.id = instructor.id) tot
FROM instructor
GROUP BY id;


-- 1.4
SELECT course_id, semester, year, sec_id, AVG(tot_cred)
FROM takes
         NATURAL JOIN student
NATURAL join section
WHERE year = 2017
GROUP BY course_id, semester, year, sec_id
HAVING COUNT(id) >= 2;

-- 1.5
SELECT *
FROM section
         NATURAL JOIN classroom;

SELECT *
FROM section
         JOIN classroom
              USING (building, room_number);


-- 2.1
CREATE TABLE emp_bonus
(
    emp_no   CHAR(4),
    received CHAR(11),
    type     INTEGER CHECK (type IN (1, 2, 3))
);

INSERT INTO emp_bonus(emp_no, received, type)
VALUES ('7934', '17-MAR-2005', 1),
       ('7934', '15-FEB-2005', 2),
       ('7839', '15-FEB-2005', 3),
       ('7782', '15-FEB-2005', 1);

CREATE TABLE emp
(
    emp_no  CHAR(4) PRIMARY KEY,
    ename   VARCHAR(6),
    sal     NUMERIC(10, 2),
    dept_no INTEGER
);

INSERT INTO emp(emp_no, ename, sal, dept_no)
VALUES (7934, '张三', 10000, 42),
       (7839, '李四', 8000, 42),
       (7782, '王五', 45000, 43);

-- 2.2
SELECT SUM(sal) tot_salary, SUM(bonus) tot_bonus
FROM (SELECT *,
             (CASE
                  WHEN type = 1 THEN sal * 0.1
                  WHEN type = 2 THEN sal * 0.2
                  ELSE sal * 0.3
                 END) AS bonus
      FROM emp e
               LEFT JOIN emp_bonus eb ON e.emp_no = eb.emp_no) a
WHERE dept_no = 42;
