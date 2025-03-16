SELECT count(DISTINCT tk.id) AS ID
FROM takes tk
         JOIN teaches te ON tk.course_id = te.course_id
         JOIN instructor ins ON te.ID = ins.ID
WHERE ins.name = 'Tung';

SELECT course_id,credits
FROM course 
WHERE
    credits>=3
    AND
    dept_name='Comp. Sci.'
ORDER BY credits ;


SELECT count(DISTINCT takes.ID) AS ID
FROM takes
JOIN teaches ON takes.course_id = teaches.course_id 
JOIN instructor ON teaches.ID = instructor.ID
WHERE instructor.name = 'Tung';

