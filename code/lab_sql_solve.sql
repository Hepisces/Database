-- q1
SELECT
    DISTINCT t.name
FROM
    instructor AS t,
    instructor AS s
WHERE
    t.salary > s.salary
    AND s.dept_name = 'History';

-- q2 way1:LIKE()
SELECT
    *
FROM
    instructor
WHERE
    name LIKE 'S%';

-- q2 way2:~
SELECT
    *
FROM
    instructor
WHERE
    name ~ '^S';

-- q2 way3: SIMILAR TO
SELECT
    *
FROM
    instructor
WHERE
    name SIMILAR TO 'S%';