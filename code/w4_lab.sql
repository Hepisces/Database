SELECT DISTINCT dept_name
FROM instructor;

SELECT name, salary / 12
FROM instructor;

SELECT name
FROM instructor
WHERE dept_name = 'Physics';

SELECT name
FROM instructor
WHERE salary BETWEEN 90000 AND 100000;


SELECT *
FROM try
WHERE col3 LIKE 'abc\\%';

SELECT *
FROM section
WHERE (year = 2007 AND semester = 'Fall')
   OR (year = 2008 AND semester = 'Spring');


SELECT *
FROM section
WHERE (year = 2007 AND semester = 'Fall')
UNION
SELECT *
FROM section
WHERE (year = 2008 AND semester = 'Spring');
