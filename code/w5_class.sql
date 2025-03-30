SELECT name, COALESCE(salary, 0)
FROM instructor;

SELECT *
FROM instructor;

CREATE TABLE test1
(
    a boolean,
    b varchar(10)
);

SELECT a, COALESCE(b, 'no content')
FROM test1;

SELECT a,
       CASE
           WHEN b IS NULL THEN 'no content'
           ELSE b
           END
FROM test1;
-- 找出每个系在 2018 年秋季学期有授课的教师人数
-- instructor(ID, name, dept_name, salary)
-- teaches(ID, course_id, sec_id, semester, year)

SELECT dept_name, COUNT(name) AS number
FROM instructor i
         JOIN teaches t ON i.id = t.id
WHERE semester = 'Fall'
  AND year = '2008'
GROUP BY dept_name

SELECT dept_name, COUNT(DISTINCT instructor.id)
FROM instructor,
     teaches
WHERE instructor.id = teaches.id
  AND semester = 'Fall'
  AND year = '2008'
GROUP BY dept_name;

SELECT a
FROM test1
GROUP BY a;

----
--

SELECT dept_name, AVG(salary) AS avg_salary
FROM instructor
GROUP BY dept_name
HAVING AVG(salary) > 42000;

-- 在 2017 年讲授的课程段，如果该课程段有至少 2 名学生选课， 找出选修该课的所有学生的总学分的平均值。
SELECT course_id, semester, year, sec_id, AVG(tot_cred)
FROM student s
         JOIN takes t ON s.id = t.id
WHERE year = '2007'
GROUP BY course_id, semester, year, sec_id
HAVING COUNT(s.id) >= 2;

SELECT course_id, semester, year, sec_id, AVG(tot_cred)
FROM student,
     takes
WHERE student.id = takes.id
  AND year = 2007
GROUP BY course_id, semester, year, sec_id
HAVING COUNT(student.id) >= 2;

SELECT dept_name, avg_salary
FROM (SELECT dept_name, AVG(salary) AS avg_salary FROM instructor GROUP BY dept_name) AS a
WHERE avg_salary > 42000;


SELECT dept_name, AVG(salary) AS avg_salary
FROM instructor
GROUP BY dept_name
HAVING AVG(salary) > 42000

