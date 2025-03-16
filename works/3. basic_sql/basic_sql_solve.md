# Basic SQL 作业解答

## 问题一

> 题目一（3 分）
> 假设拟在数据库添加一个关系，其关系模式是 users(name, pswd, gender)，并让 name 作为主码。请使用 CREATE TABLE 命令添加该关系

```sql
CREATE TABLE users(
    name VARCHAR(20) PRIMARY KEY,
    pswd VARCHAR(20),
    gender BOOLEAN -- 0 表示女, 1 表示男
);
```

## 问题二

> 考虑课堂中使用的`大学`数据库，包括如下关系：
>
> - course(course_id, title, dept_name, credits)
> - instructor(ID, name, dept_name, salary)
> - teaches(ID, course_id, sec_id, semester, year)
> - student(ID, name, dept_name, tot_cred)
> - takes(ID, course_id, sec_id, semester, year, grade)
>
> 使用 SQL 语句完成下面的查询：
>
> 1. 找到在`计算机`学院开设的不少于`3`个`学分`的课程，并按`学分`进行升序排序。
> 2. 找到所有被名叫`图灵`的老师教过的学生的学号（`ID`），并确保结果没有重复。

- 1

```sql
SELECT course_id
FROM course
WHERE
    credits>=3
    AND
    dept_name='计算机'
ORDER BY credits ASC;
```

- 2

```sql
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
    ins.name = '图灵';
```

## 问题三

> 考虑题目二提到的关系模式，请问下面的 SQL 语句的含义是什么？
>
> ```sql
> SELECT DISTINCT T.name
> FROM instructor AS T, instructor AS S
> WHERE T.salary > S.salary AND S.dept_name = '会计';
> ```

所有至少比一个会计学院老师薪水高的老师的名字, 确保结果没有重复.
