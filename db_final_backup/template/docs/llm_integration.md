# LLM模型集成指南

本文档介绍如何配置和使用SQL助手的自然语言查询功能，该功能允许用户使用自然语言而非SQL语法来查询数据库。

## 模型选择

SQL助手支持两种类型的LLM（大型语言模型）集成：
1. **本地模型**：在用户自己的计算机上运行
2. **在线API**：通过云服务API调用远程模型

### 本地模型 vs 在线API

|            | 本地模型                       | 在线API                    |
|------------|-------------------------------|----------------------------|
| **优点**    | - 隐私保护，数据不离开本地<br>- 无需互联网连接<br>- 无API调用费用<br>- 低延迟 | - 更强大的模型<br>- 无需高配置硬件<br>- 无需安装大型模型<br>- 始终保持最新 |
| **缺点**    | - 需要足够的计算资源<br>- 需要下载大型模型文件<br>- 通常性能弱于大型在线模型 | - 需要API密钥<br>- 可能产生API费用<br>- 隐私风险<br>- 依赖互联网连接 |
| **推荐使用场景** | - 高隐私需求场景<br>- 内网环境<br>- 频繁查询 | - 复杂查询需求<br>- 追求高精度<br>- 资源受限环境 |

## 配置方法

### 本地模型配置

1. **获取模型文件**
   - 下载与SQL任务相关的模型，例如经过微调的LLAMA或其他开源LLM
   - 推荐模型格式：GGUF (GPT-Generated Unified Format)，这种格式对资源需求较低

2. **存放模型文件**
   - 创建`models`目录并将模型文件放入其中
   - 确保模型文件路径正确配置

3. **修改配置文件**
   ```yaml
   nlp:
     model_type: local
     local:
       model_path: models/your-model-name.gguf  # 修改为您的模型文件路径
       max_tokens: 1024
       temperature: 0.3
   ```

4. **硬件要求**
   - 最低: 8GB RAM, 现代多核CPU
   - 推荐: 16GB+ RAM, 高性能CPU或GPU

### 在线API配置

1. **获取API密钥**
   - OpenAI: 访问 https://platform.openai.com/ 注册并获取API密钥
   - 其他提供商: 请参考各自的官方文档

2. **设置API密钥**
   - 方法1: 在配置文件中直接设置 (不推荐用于共享环境)
     ```yaml
     nlp:
       model_type: online
       online:
         provider: openai
         api_key: your_api_key_here
         model: gpt-3.5-turbo
     ```
   
   - 方法2: 使用环境变量 (推荐)
     ```yaml
     nlp:
       model_type: online
       online:
         provider: openai
         api_key: ${OPENAI_API_KEY}
         model: gpt-3.5-turbo
     ```
     然后在环境中设置变量:
     ```bash
     # Linux/macOS
     export OPENAI_API_KEY=your_api_key_here
     
     # Windows
     set OPENAI_API_KEY=your_api_key_here
     ```

## 自定义微调模型

如果您计划为SQL任务微调自己的模型，我们推荐:

1. **选择基础模型**
   - 小型模型 (微调成本低): LLAMA-2-7B, Phi-2, Mistral-7B
   - 中型模型 (平衡性能与成本): LLAMA-2-13B, Mixtral 8x7B
   - 大型模型 (最佳性能): LLAMA-3, Mixtral, GPT-3.5

2. **准备训练数据**
   - 收集自然语言到SQL的转换示例
   - 确保覆盖多种SQL操作和表结构
   - 数据结构应为 {"instruction": "用中文找出...", "output": "SELECT..."}

3. **微调步骤**
   - 使用QLoRA等参数高效微调方法
   - 使用transformers或类似库执行微调
   - 导出为GGUF格式以提高推理效率

4. **集成到系统**
   - 将微调后的模型放入`models`目录
   - 更新配置文件指向新模型

## 故障排除

1. **LLM无法加载**
   - 检查模型文件路径是否正确
   - 确认系统内存是否足够
   - 查看日志文件获取详细错误信息

2. **翻译结果不准确**
   - 尝试调整提示模板 (查看`nlp.py`中的`_prepare_prompt`方法)
   - 考虑使用更强大的模型
   - 确保数据库结构信息被正确提供给模型

3. **API连接失败**
   - 验证API密钥是否正确
   - 检查网络连接
   - 确认API账户余额是否充足

## 进一步自定义

要修改模型提示或翻译逻辑，可以编辑以下文件:

- `sqlassistant/nlp.py`: 核心NLP处理逻辑
- 特别是`_prepare_prompt`方法可以自定义提示模板

---

如需更多帮助，请查看[项目GitHub仓库](https://github.com/yourusername/sqlassistant)或提交Issue。 