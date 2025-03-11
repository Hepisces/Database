# Relational Model 作业解答

# 题目一

> 考虑一个`银行`数据库，其关系模式如下所示：
>
> - branch (branch_name, branch_city, assets)
> - customer (ID, customer_name, customer_street, customer_city)
> - loan (loan_number, branch_name, amount)
> - borrower (ID, loan_number)
> - account (account_number, branch_name, balance)
> - depositor (ID, account_number)
>
> 使用`关系代数`完成下面的查询：
>
> 1. 找到位于`成都`市的支行的名字。
> 2. 找到在`杨柳`支行有贷款（`loan`）的借款人（`borrower`）的 ID。

1. $$
   \Pi_{{\text{branch\_name}}}(\sigma_{\text{branch\_city = '成都'}}(\text{branch}))
   $$

2. $$
   \Pi_{{\text{ID}}}(\sigma_{\text{branch\_name = '杨柳'} \land \text{loan\_number}>0}(\text{loan} \bowtie \text{borrower}))
   $$

# 题目二

> 假设数据库中存储用户名和密码的关系模式是 users(name, pswd, gender)，请结合关系代数简述实现`用户登录`逻辑的思路。

当用户在客户端输入用户名和密码后, 服务器(后台)会负责验证先后用户名和密码是否正确。

验证的逻辑是:

1. 从客户端获取用户名和密码。
2. 首先在数据库中查找对应的用户名, 如果找到用户名则继续查找密码。
3. 如果找到对应的用户名和密码, 则认为用户登录成功。
4. 如果在第二步中没有找到用户名或者密码与用户名不匹配, 认为用户登录失败, 一般显示的是"用户名或密码错误"

因此, 假设用户在客户端输入的用户名和密码分别为`input_name`和`input_pswd`, 则第二步查找的过程可能是先查找用户名, 再查找密码, 用关系代数表示为:

$$
\sigma_{\text{pswd = input\_pswd}}(\sigma_{\text{name = input\_name}}(\text{users}))
$$

因此验证失败的情况应该是:(1) 用户名不存在, (2) 用户名存在, 但是密码错误. 当然还有都错误的情况, 不过如果用户名已经判定为不存在, 不应当继续判定密码增加开销, 当然数据库系统可能已经有对应优化措施, 所以像

$$
\sigma_{\text{pswd = input\_pswd} \land \text{name = input\_name}}(\text{users})
$$

这样同时判断用户名和密码是否匹配的判断方法与前面的计算方法可能几乎无性能差异.

进一步地, 可以判断用户的性别, 优化登录界面, 在验证成功后, 根据

$$
\Pi_{\text{gender,name}}(\sigma_{\text{pswd = input\_pswd} \land \text{name = input\_name}}(\text{users}))
$$

的返回结果来判定用户的性别, 显示`{name}{gender},欢迎您`的登录界面.
