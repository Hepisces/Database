# 挑战题解答

## 问题一

> 思考并解释关系数据库中"关系"一词的含义。（不超过 100 字）

关系数据库中的"关系"指的是由元组形式的行和作为属性的列组成的二维表格, 用来存储数据,体现数据的表内的逻辑结构. 但也可以通过具有唯一性的一个或多个属性(主键, 用于唯一性确定一个元组)进行表格间的关系运算. _(93 words)_

### 问题一参考文献

[1] Oracle. (n.d.). 什么是关系数据库. https://www.oracle.com/cn/database/what-is-a-relational-database/

[2] 知乎. (2025.2.27). 数据库原理与应用第三章关系数据模型. https://zhuanlan.zhihu.com/p/26568591349

### 问题一 LLMs 使用说明

因为调用了多个 LLM, 如果全部在正文展示篇幅过长, 因此这部分内容将在[reference/llm_respond.md](reference/llm_respond.md)中展示, 并注明模型名称.

## 问题二

> 调研 2023 年之后最先进的 Text2SQL 技术（类似小的文献综述，不超过 500 字），并总结其异同之处。

Text-to-SQL 技术旨在将自然语言查询转化为 SQL 语句，以高效访问关系型数据库。传统方法依赖深度学习和预训练模型，但在语义理解、复杂查询及跨域泛化上存在局限性[5]。2023 年后，大语言模型（LLM）驱动的方法占据主流，分为四类：Prompt、Fine-tuning、Agent 和混合方法[4,17,22]。

**Prompt**通过设计提示词和辅助组件引导 LLM 生成 SQL，如 DAIL-SQL 在 BIRD[8] 基准上达 55.9%准确率[15]。其优点是支持零/少样本学习，无需大量训练数据，但提示词设计脆弱，跨域泛化能力有限[6,13,23]。

**Fine-tuning**通过全参数或参数高效技术优化 LLM，增强特定领域表现。目前，Xi-Yan SQL 的混合框架在 BIRD[8] 基准上以 75.63%准确率保持 SOTA[24]。该方法在特定领域表现优异，但需大量高质量标注数据，尤其在多表查询中挑战较大[8,11]。

**Agent**利用多 LLM 协作动态生成和修正 SQL，如 MAC-SQL 在 BIRD[8] 测试上获 59%准确率[19]。其灵活性适于多步推理任务，但系统复杂度和资源需求较高[18,20]。

**混合方法**结合微调与其他技术提升性能。如 CHESS 通过智能体与微调在 BIRD[8] 上达 64.62%准确率[18]，CHASE-SQL 则融合微调与提示词，设计了更精巧的流程在 BIRD[8] 上获得 73%的准确率[14]。然而，组件整合增加了复杂度[3,11]。

综上，2023 年后 Text-to-SQL 技术在 LLM 推动下进步显著。Prompt 方法部署快但泛化不足；Fine-tuning 方法领域强但数据依赖高；Agent 灵活但资源密集；混合方法平衡优势却设计复杂。未来需聚焦降低数据与计算需求，提升跨域能力。

### 问题二参考文献

[1] Caferoğlu, H.A. and Ulusoy, Ö. 2025. E-SQL: Direct Schema Linking via Question Enrichment in Text-to-SQL. arXiv.

[2] Cheng, Z. et al. 2023. Binding Language Models in Symbolic Languages. arXiv.

[3] Gao, D. et al. 2023. Text-to-SQL Empowered by Large Language Models: A Benchmark Evaluation. arXiv.

[4] Hong, Z. et al. 2025. Next-Generation Database Interfaces: A Survey of LLM-based Text-to-SQL. arXiv.

[5] Katsogiannis-Meimarakis, G. and Koutrika, G. 2023. A survey on deep learning approaches for text-to-SQL. The VLDB Journal. 32, 4 (Jul. 2023), 905–936. DOI:https://doi.org/10.1007/s00778-022-00776-8.

[6] Li, B. et al. 2024. The Dawn of Natural Language to SQL: Are We Fully Ready? Proceedings of the VLDB Endowment. 17, 11 (Jul. 2024), 3318–3331. DOI:https://doi.org/10.14778/3681954.3682003.

[7] Li, H. et al. 2023. RESDSQL: Decoupling Schema Linking and Skeleton Parsing for Text-to-SQL. arXiv.

[8] Li, J. et al. 2023. Can LLM Already Serve as A Database Interface? A BIg Bench for Large-Scale Database Grounded Text-to-SQLs. arXiv.

[9] Li, Y. et al. 2023. T5-SR: A Unified Seq-to-Seq Decoding Strategy for Semantic Parsing. arXiv.

[10] Liu, A. et al. 2023. A comprehensive evaluation of ChatGPT's zero-shot Text-to-SQL capability. arXiv.

[11] Liu, X. et al. 2024. A Survey of NL2SQL with Large Language Models: Where are we, and where are we going? arXiv.

[12] Maamari, K. et al. 2024. The Death of Schema Linking? Text-to-SQL in the Age of Well-Reasoned Language Models. arXiv.

[13] Mohammadjafari, A. et al. 2025. From Natural Language to SQL: Review of LLM-based Text-to-SQL Systems. arXiv.

[14] Pourreza, M. et al. 2024. CHASE-SQL: Multi-Path Reasoning and Preference Optimized Candidate Selection in Text-to-SQL. arXiv.

[15] Pourreza, M. and Rafiei, D. 2023. DIN-SQL: Decomposed In-Context Learning of Text-to-SQL with Self-Correction. arXiv.

[16] Qin, B. et al. 2022. A Survey on Text-to-SQL Parsing: Concepts, Methods, and Future Directions. arXiv.

[17] Shi, L. et al. 2024. A Survey on Employing Large Language Models for Text-to-SQL Tasks. arXiv.

[18] Talaei, S. et al. 2024. CHESS: Contextual Harnessing for Efficient SQL Synthesis. arXiv.

[19] Wang, B. et al. 2024. MAC-SQL: A Multi-Agent Collaborative Framework for Text-to-SQL. arXiv.

[20] Wang, T. et al. 2025. DBCopilot: Natural Language Querying over Massive Databases via Schema Routing. arXiv.

[21] Zhou, F. et al. 2024. DB-GPT-Hub: Towards Open Benchmarking Text-to-SQL Empowered by Large Language Models. arXiv.

[22] Zhu, X. et al. 2024. Large Language Model Enhanced Text-to-SQL Generation: A Survey. arXiv.

[23] Gu, Z. et al. 2023. Few-shot Text-to-SQL Translation using Structure and Content Prompt Learning. Proceedings of the ACM on Management of Data. 1, 2 (Jun. 2023), 1–28. DOI:https://doi.org/10.1145/3589292.

[24] Gao, Y. et al. 2025. A Preview of XiYan-SQL: A Multi-Generator Ensemble Framework for Text-to-SQL. arXiv.

### 问题二 LLMs 使用说明

部分的文献阅读使用了 LLM 进行辅助, 包括文章的翻译, 摘要等任务.

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

**小结:** 可以看到, 在经过 co-star 的控制后, 模型能够正确输出期望的输出答案, 同时没有多余的解释说明.

## 问题四

> 为什么在 Python 中 **{[1,2]}** 不合法?

首先, 如果在 python 中定义`{[1,2]}`会导致如下错误:

```bash
>>> a={[1,2]}
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: unhashable type: 'list'
```

报错提示列表是不可哈希的. 这说明列表不能作为字典的键存在. (一个重点是如果在 python 中使用花括号定义, 那么这个定义的是字典, 而不是集合)

根据 python 的官方文档,(https://docs.python.org/zh-cn/3.13/tutorial/datastructures.html#dictionaries)

> 字典是以 键 来索引的，键可以是任何不可变类型；字符串和数字总是可以作为键。 元组在其仅包含字符串、数字或元组时也可以作为键；如果一个元组直接或间接地包含了任何可变对象，则不可以用作键。 你不能使用列表作为键，因为列表可使用索引赋值、切片赋值或 append() 和 extend() 等方法进行原地修改

因此很明显, 列表是可变对象, 并且是可以原地修改的, 这不符合 python 对列表键的定义, 即不可变, 或者不可哈希.

从定义上来说, 哈希的关键要求时`对象在生命周期内保持不变`, 列表显然不符合定义

从一个字典的定义和检索过程来看,

当字典的键值对`{key: value}`被定义后, 字典会通过内置的`hash()`函数对 key 进行一次计算, 根据返回值(记为`A`)决定`value`的存储位置并不再更新;

当`key`为列表时, 由于是可变对象, 当列表被修改后, `hash()`函数的返回值会发生变化,记为`B` 当字典检索时, 就会去找到`B`位置的`value`值. 但实际上我们需要的`value`值是`A`位置的, 因此就会导致检索错误.

为了避免这个错误, 字典就禁止了列表作为键.
