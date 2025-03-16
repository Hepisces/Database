SELECT
    count(DISTINCT tk.id) AS ID
FROM
    takes tk
    JOIN teaches te ON tk.course_id = te.course_id
    JOIN instructor ins ON te.ID = ins.ID
WHERE
    ins.name = 'Tung';

SELECT
    course_id,
    credits
FROM
    course
WHERE
    credits >= 3
    AND dept_name = 'Comp. Sci.'
ORDER BY
    credits;

SELECT
    DISTINCT tk.ID AS ID
FROM
    takes tk
    JOIN teaches te ON tk.course_id = te.course_id
    AND tk.sec_id = te.sec_id
    AND tk.semester = te.semester
    AND tk.year = te.year
    JOIN instructor ins ON te.ID = ins.ID
WHERE
    ins.name = 'Tung';