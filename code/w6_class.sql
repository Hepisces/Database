SELECT dept_name,
       STRING_AGG(id, '|') AS id,
       AVG(salary)
FROM instructor
GROUP BY dept_name;

SELECT *
FROM instructor
LIMIT 10;

SELECT dept_name, MIN(instructor.salary)
FROM instructor
GROUP BY dept_name;

SELECT COUNT(*)
FROM (SELECT dept_name
      FROM instructor
      GROUP BY dept_name
      HAVING AVG(salary) >= ANY (SELECT AVG(salary) FROM instructor GROUP BY dept_name)) a;

SELECT *
FROM student
ORDER BY RANDOM()
LIMIT 5;

SELECT CASE
           WHEN EXISTS(SELECT *
                       FROM instructor
                       WHERE salary > 40000) THEN 'Yes'
           ELSE 'No'
           END re;

SELECT CASE
           WHEN COUNT(*) > 0 THEN 'Yes'
           ELSE 'No'
           END
FROM instructor
WHERE salary > 40000;

SELECT CASE
           WHEN (SELECT MAX(salary) FROM instructor LIMIT 1) > 40000 THEN 'Yes'
           ELSE 'No'
           END;

SELECT COUNT(DISTINCT ta.id)
FROM takes ta
         LEFT JOIN teaches te ON te.course_id = ta.course_id AND te.sec_id = ta.sec_id AND te.semester = ta.semester AND
                                 te.year = ta.year
WHERE te.id = '10101';

SELECT *
FROM department
WHERE budget = (SELECT MAX(budget) FROM department);

WITH max_buedget(value) AS (SELECT MAX(budget) FROM department)
SELECT budget
FROM department,
     max_buedget
WHERE department.budget = max_buedget.value;

SELECT dept_name
FROM instructor
GROUP BY dept_name
HAVING SUM(salary) > (SELECT AVG(salary) FROM select sum(salary) AS salary
FROM instructor
GROUP BY dept_name a )

SELECT dept_name
FROM instructor
GROUP BY dept_name
HAVING
    SUM(salary) > (SELECT AVG(value) FROM (SELECT SUM(salary) FROM instructor GROUP BY dept_name) AS sum_salary(value));


WITH dept_salary(dept_name, total, rank) AS (SELECT dept_name, SUM(salary), RANK() OVER (ORDER BY SUM(salary) DESC )
                                             FROM instructor
                                             GROUP BY dept_name)
SELECT dept_name, total
FROM dept_salary
-- where total=(SELECT max(total) from dept_salary)
WHERE rank = 1;

-- DELETE from instructor
-- where salary>=70000 and salary<=90000

SELECT * from instructor
where name LIKE 'Peter'