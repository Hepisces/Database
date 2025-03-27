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
FROM test1