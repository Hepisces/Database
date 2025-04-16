CREATE TABLE section1
(
    course_id    varchar(8),
    sec_id       varchar(8),
    semester     varchar(6),
    year         numeric(4, 0),
    building     varchar(15),
    room_number  varchar(7),
    time_slot_id varchar(4),
    PRIMARY KEY (course_id, sec_id, semester, year),
    FOREIGN KEY (course_id) REFERENCES course (course_id),
    CHECK (semester IN ('Spring', 'Fall')),
    CHECK (year BETWEEN 1976 AND 2100)
);
-- 考虑添加约束：semester 只能是 Spring 或 Fall；year 在 1976 到 2100 之间；course_id 为外码，参照关系 course。

SELECT id
FROM (SELECT id, RANK() OVER (ORDER BY salary DESC NULLS LAST) AS s_rank FROM instructor) AS a
WHERE s_rank = 1;

-- 考虑大学数据库，找出 2017 年秋季 (Fall) 开设的每个课程段 (section) 的选课人数。（提示：仅考虑选课人数大于 0 的课程 段，使用关系 takes）
SELECT course_id, sec_id, COUNT(id) AS total_number
FROM takes
WHERE semester = 'Fall'
  AND year = 2017
GROUP BY course_id, sec_id;


SELECT name, course_id
FROM student,
     takes
WHERE student.id = takes.id;
-- 两种写法没有区别
SELECT name, course_id
FROM student
         NATURAL JOIN takes;

