# 挑战题解答

## 问题一

> 思考并解释关系数据库中“关系”一词的含义。（不超过 100 字）

关系数据库中的"关系"指的是由元组形式的行和作为属性的列组成的二维表格, 用来存储数据,体现数据的表内的逻辑结构. 但也可以通过具有唯一性的一个或多个属性(主键, 用于唯一性确定一个元组)进行表格间的关系运算. *(93 words)*

### 参考文献

[1] Oracle. (n.d.). 什么是关系数据库. https://www.oracle.com/cn/database/what-is-a-relational-database/

[2] 知乎. (2025.2.27). 数据库原理与应用第三章关系数据模型. https://zhuanlan.zhihu.com/p/26568591349

### LLMs使用说明

因为调用了多个LLM, 如果全部在正文展示篇幅过长, 因此这部分内容将在[reference/llm_respond.md](reference/llm_respond.md)中展示, 并注明模型名称. 

## 问题二

> 调研 2023 年之后最先进的 Text2SQL 技术（类似小的文献综述，不超过 500 字），并总结其异同之处。

## 问题三

> 考虑下面的题目，
> 考虑
>
> ```sql
> create table classroom
> (building  varchar(15),
>  room_number  varchar(7),
>  capacity  numeric(4,0),
>  primary key (building, room_number)
> );
> ```
>
> 找出容量最大的教室房间号
>
> 其答案是
>
> ```sql
> SELECT room_number\
> FROM classroom\
> WHERE capacity = (SELECT MAX>(capacity) FROM classroom);
> ```
>
> 请使用任意编程语言通过 API 分别调用>DeepSeek V3 和 R1 让大模型回答上面的题目。

本次分别使用两种提示词(无提示和 costar 提示), 并分别调用 v3 和 r1 模型,得到回答如下, 代码已上传到仓库中:[code/q3.ipynb](code/q3.ipynb)

### 无提示

这里的无提示词指的是不为此任务设置专一化的提示词, 而是使用通用任务中使用的广泛提示词, 即

```txt
你是一位助手
```

用户的输入即为问题本身, 最终得到答案如下:

- DeepSeek v3

````markdown
    要找出容量最大的教室房间号，你可以使用 SQL 查询语句。以下是一个示例查询：

    ```sql
    SELECT building, room_number
    FROM classroom
    WHERE capacity = (SELECT MAX(capacity) FROM classroom);
    ```

    ### 解释：
    1. **`SELECT building, room_number`**: 选择要返回的列，即 `building` 和 `room_number`。
    2. **`FROM classroom`**: 从 `classroom` 表中查询数据。
    3. **`WHERE capacity = (SELECT MAX(capacity) FROM classroom)`**: 过滤条件，选择容量等于最大容量的记录。子查询 `(SELECT MAX(capacity) FROM classroom)` 返回 `classroom` 表中最大的 `capacity` 值。

    ### 结果：
    该查询将返回容量最大的教室的 `building` 和 `room_number`。如果有多个教室的容量相同且都是最大的，查询将返回所有这些教室的信息。
````

- DeepSeek R1

````markdown
    要找出容量最大的教室房间号，可以使用以下SQL查询：

    ```sql
    SELECT building, room_number
    FROM classroom
    WHERE capacity = (SELECT MAX(capacity) FROM classroom);
    ```

    **步骤解释：**
    1. **子查询获取最大容量**：`(SELECT MAX(capacity) FROM classroom)` 计算所有教室的最大容量。
    2. **主查询匹配容量**：外层查询选择容量等于最大值的记录，返回对应的`building`和`room_number`组合，确保唯一标识每个教室。

    **注意：**
    - 使用`building`和`room_number`共同确保结果唯一，因为不同建筑可能有相同房间号。
    - 若存在多个教室容量同为最大值，将全部返回。
````

**小结:** 可以看到的是, 在零提示词下, 模型不仅没有输出正确的答案, 同时出现了不希望看到的解释和说明, 因此需要通过 prompt 来控制模型的输出

### costar 提示

costar 是 2023 年 GPT-4 Prompt Engineering 竞赛中冠军得主提出的一套提示词模板, 可以有效引导模型思考问题, 并控制模型的输出结构(https://towardsdatascience.com/how-i-won-singapores-gpt-4-prompt-engineering-competition-34c195a93d41/).

鉴于当前问题较为简单, 所以这里不使用完整的 costar 架构, 而是简单描述任务, 定义角色以及限制输出格式:

```txt
#角色#
你是一个SQL专家。我会给你一个SQL相关的问题。

#规则#
请你：
1. 只输出解决问题所需的SQL代码
2. 不要有任何解释性文字
3. 确保代码语法正确且可以直接执行
4. 代码要简洁高效
5. 只输出一个SQL语句
```

_也可以额外增加一段如`#输出格式# <<<你的sql代码>>>`来保证格式, 但是经过实验模型已经可以不需要这个部分, 虽然他仍然带有一定的 markdown 格式._

- DeepSeek v3

````markdown
    ```sql
    SELECT room_number FROM classroom WHERE capacity = (SELECT MAX(capacity) FROM classroom);
    ```
````

- DeepSeek R1

````markdown
    ```sql
    SELECT room_number FROM classroom WHERE capacity = (SELECT MAX(capacity) FROM classroom);
    ```
````

**小结:** 可以看到, 在经过co-star的控制后, 模型能够正确输出期望的输出答案, 同时没有多余的解释说明. 
