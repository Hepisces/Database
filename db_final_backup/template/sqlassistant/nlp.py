"""
自然语言处理模块 - 用于将自然语言转换为SQL查询

本模块负责将用户的自然语言查询转换为SQL语句。支持两种模式：
1. 使用Hugging Face模型在本地处理
2. 通过API调用在线模型（Qwen或DeepSeek）
"""

import os
import json
from typing import Dict, List, Tuple, Any, Optional, Union
import logging
import traceback
import re

# Hugging Face相关库
try:
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    from accelerate import infer_auto_device_map
except ImportError:
    torch = None
    AutoTokenizer = None
    AutoModelForCausalLM = None
    pipeline = None
    infer_auto_device_map = None

# Qwen API（阿里云灵积模型服务）
try:
    import dashscope
    from dashscope import Generation
except ImportError:
    dashscope = None
    Generation = None

# DeepSeek API
try:
    import deepseek
    from deepseek import DeepSeekAPI
except ImportError:
    deepseek = None
    DeepSeekAPI = None


class NLProcessor:
    """
    自然语言处理器，用于将自然语言翻译为SQL
    
    设计思路：
    1. 提供一个统一的接口来处理自然语言到SQL的转换
    2. 支持本地模型(Hugging Face)和在线模型(Qwen,DeepSeek)
    3. 自动处理数据库模式的注入，使模型能生成正确的SQL
    4. 健壮的错误处理和日志记录机制
    """
    
    def __init__(self, config: Dict):
        """
        初始化自然语言处理器
        
        Args:
            config: 配置字典，包含模型类型、路径或API密钥等配置
        """
        self.config = config
        self.nlp_config = config.get("nlp", {})
        self.model_type = self.nlp_config.get("model_type", "local")
        self.model = None
        self.tokenizer = None
        self.db_schema = {}
        
        # 设置日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # 初始化模型
        self._initialize_model()
    
    def _initialize_model(self):
        """
        根据配置初始化合适的模型
        
        本地模型：加载Hugging Face模型
        在线模型：配置API客户端
        """
        try:
            if self.model_type == "local":
                self._initialize_local_model()
            else:  # online
                self._initialize_online_model()
        except Exception as e:
            self.logger.error(f"初始化NLP模型失败: {str(e)}")
            self.logger.error(traceback.format_exc())
    
    def _initialize_local_model(self):
        """
        初始化本地Hugging Face模型
        
        加载预训练或微调过的模型，配置设备映射以优化资源使用
        """
        local_config = self.nlp_config.get("local", {})
        model_path = local_config.get("model_path")
        provider = local_config.get("provider", "huggingface")
        
        if provider != "huggingface":
            self.logger.error(f"不支持的本地模型类型: {provider}，仅支持huggingface")
            return
        
        if not model_path:
            self.logger.error("本地模型路径未指定")
            return
        
        # 检查模型文件是否存在
        if os.path.exists(model_path):
            self.logger.info(f"正在加载本地模型: {model_path}")
        else:
            self.logger.info(f"本地模型路径不存在，将尝试从Hugging Face Hub下载: {model_path}")
        
        # 确保必要的库已安装
        if not AutoModelForCausalLM or not AutoTokenizer or not torch:
            self.logger.error("缺少必要的库: transformers 或 torch。请安装: pip install transformers torch")
            return
        
        try:
            # 加载tokenizer
            self.logger.info(f"正在加载tokenizer: {model_path}")
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_path, 
                trust_remote_code=True,
                use_fast=True
            )
            
            # 检测可用资源并加载模型
            device_map = "auto"
            if torch.cuda.is_available():
                self.logger.info(f"检测到CUDA设备: {torch.cuda.get_device_name(0)}")
                # 获取GPU内存
                gpu_mem = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                self.logger.info(f"GPU内存: {gpu_mem:.2f}GB")
                
                # 如果GPU内存不足，使用更高效的配置
                if gpu_mem < 10:  # 小于10GB的GPU
                    self.logger.info("GPU内存有限，使用8-bit量化")
                    self.model = AutoModelForCausalLM.from_pretrained(
                        model_path,
                        device_map=device_map,
                        torch_dtype=torch.float16,
                        load_in_8bit=True,
                        trust_remote_code=True
                    )
                else:
                    self.model = AutoModelForCausalLM.from_pretrained(
                        model_path,
                        device_map=device_map,
                        torch_dtype=torch.float16,
                        trust_remote_code=True
                    )
            else:
                self.logger.info("未检测到GPU，使用CPU推理")
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_path,
                    device_map=device_map,
                    trust_remote_code=True
                )
            
            self.logger.info(f"Hugging Face模型加载成功: {model_path}")
            
        except Exception as e:
            self.logger.error(f"加载Hugging Face模型失败: {str(e)}")
            self.logger.error(traceback.format_exc())
    
    def _initialize_online_model(self):
        """
        初始化在线API模型客户端
        
        支持Qwen（阿里云灵积模型）和DeepSeek API
        """
        online_config = self.nlp_config.get("online", {})
        provider = online_config.get("provider", "qwen")
        
        if provider == "qwen":
            if not dashscope or not Generation:
                self.logger.error("缺少DashScope库，请安装: pip install dashscope")
                return
            
            api_key = online_config.get("api_key")
            if not api_key:
                # 尝试从环境变量获取
                api_key = os.environ.get("QWEN_API_KEY")
            
            if not api_key:
                self.logger.error("Qwen API密钥未提供，请在配置中设置或设置环境变量QWEN_API_KEY")
                return
            
            try:
                # 设置API密钥
                dashscope.api_key = api_key
                self.logger.info("Qwen API配置成功")
            except Exception as e:
                self.logger.error(f"Qwen API配置失败: {str(e)}")
            
        elif provider == "deepseek":
            if not deepseek or not DeepSeekAPI:
                self.logger.error("缺少DeepSeek库，请安装: pip install deepseek")
                return
            
            api_key = online_config.get("api_key")
            if not api_key:
                # 尝试从环境变量获取
                api_key = os.environ.get("DEEPSEEK_API_KEY")
            
            if not api_key:
                self.logger.error("DeepSeek API密钥未提供，请在配置中设置或设置环境变量DEEPSEEK_API_KEY")
                return
            
            try:
                # 初始化API客户端
                self.model = DeepSeekAPI(api_key=api_key)
                self.logger.info("DeepSeek API配置成功")
            except Exception as e:
                self.logger.error(f"DeepSeek API配置失败: {str(e)}")
        
        else:
            self.logger.error(f"不支持的API提供商: {provider}，仅支持qwen和deepseek")
    
    def set_db_schema(self, schema: Dict[str, Any]):
        """
        设置数据库模式信息，用于更好的查询翻译
        
        Args:
            schema: 数据库模式信息，包含表和列的详细信息
        """
        self.db_schema = schema
        self.logger.info(f"已更新数据库模式信息，共 {len(schema)} 个表")
    
    def translate_to_sql(self, nl_query: str) -> Tuple[bool, str]:
        """
        将自然语言查询翻译为SQL查询
        
        Args:
            nl_query: 自然语言查询
            
        Returns:
            Tuple[bool, str]: (是否成功, SQL查询或错误消息)
        """
        try:
            if self.model_type == "local":
                return self._translate_with_local_model(nl_query)
            else:  # online
                return self._translate_with_online_model(nl_query)
        except Exception as e:
            self.logger.error(f"翻译查询时出错: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False, f"翻译查询时出错: {str(e)}"
    
    def _translate_with_local_model(self, nl_query: str) -> Tuple[bool, str]:
        """
        使用本地Hugging Face模型将自然语言翻译为SQL
        
        Args:
            nl_query: 自然语言查询
            
        Returns:
            Tuple[bool, str]: (是否成功, SQL查询或错误消息)
        """
        if not self.model or not self.tokenizer:
            return False, "本地模型未初始化"
        
        local_config = self.nlp_config.get("local", {})
        max_tokens = local_config.get("max_tokens", 1024)
        temperature = local_config.get("temperature", 0.3)
        
        # 准备提示
        prompt = self._prepare_prompt(nl_query)
        
        # 调用Hugging Face模型
        try:
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
            
            generation_config = {
                "max_new_tokens": max_tokens,
                "temperature": temperature,
                "do_sample": temperature > 0,
                "top_p": 0.95,
                "top_k": 50,
                "repetition_penalty": 1.1,
                "pad_token_id": self.tokenizer.eos_token_id,
            }
            
            with torch.no_grad():
                outputs = self.model.generate(**inputs, **generation_config)
            
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # 删除原始提示部分
            response = generated_text[len(prompt):].strip()
            
            # 提取SQL查询
            sql_query = self._extract_sql_from_text(response)
            
            return True, sql_query
        
        except Exception as e:
            self.logger.error(f"使用Hugging Face模型生成SQL时出错: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False, f"使用本地模型生成SQL时出错: {str(e)}"
    
    def _translate_with_online_model(self, nl_query: str) -> Tuple[bool, str]:
        """
        使用在线API模型将自然语言翻译为SQL
        
        支持Qwen（阿里云）和DeepSeek模型API
        
        Args:
            nl_query: 自然语言查询
            
        Returns:
            Tuple[bool, str]: (是否成功, SQL查询或错误消息)
        """
        online_config = self.nlp_config.get("online", {})
        provider = online_config.get("provider", "qwen")
        
        # 准备提示
        prompt = self._prepare_prompt(nl_query)
        
        if provider == "qwen":
            if not dashscope or not Generation:
                return False, "Qwen API库未安装"
            
            model = online_config.get("model", "qwen-max")
            max_tokens = online_config.get("max_tokens", 1024)
            temperature = online_config.get("temperature", 0.3)
            
            try:
                response = Generation.call(
                    model=model,
                    prompt=prompt,
                    result_format='message',  # 使用message格式
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=0.95,
                    repetition_penalty=1.1,
                )
                
                if response.status_code == 200:
                    generated_text = response.output.choices[0]['message']['content']
                    sql_query = self._extract_sql_from_text(generated_text)
                    return True, sql_query
                else:
                    error_msg = f"Qwen API调用失败: 状态码 {response.status_code}, 错误: {response.message}"
                    self.logger.error(error_msg)
                    return False, error_msg
            
            except Exception as e:
                return False, f"使用Qwen API生成SQL时出错: {str(e)}"
        
        elif provider == "deepseek":
            if not deepseek or not DeepSeekAPI or not self.model:
                return False, "DeepSeek API未初始化"
            
            model = online_config.get("model", "deepseek-chat")
            max_tokens = online_config.get("max_tokens", 1024)
            temperature = online_config.get("temperature", 0.3)
            
            try:
                response = self.model.chat(
                    model=model,
                    messages=[
                        {"role": "system", "content": "你是一个SQL专家，擅长将自然语言查询转换为准确的SQL查询语句。"},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                
                generated_text = response['choices'][0]['message']['content']
                sql_query = self._extract_sql_from_text(generated_text)
                
                return True, sql_query
            
            except Exception as e:
                return False, f"使用DeepSeek API生成SQL时出错: {str(e)}"
        
        else:
            return False, f"不支持的API提供商: {provider}，仅支持qwen和deepseek"
    
    def _prepare_prompt(self, nl_query: str) -> str:
        """
        准备模型提示
        
        构建详细的提示，包括自然语言查询和数据库模式信息，帮助模型生成准确的SQL
        
        Args:
            nl_query: 自然语言查询
            
        Returns:
            str: 完整的提示文本
        """
        # 基本提示
        prompt = "你是一个SQL专家，请将以下自然语言查询转换为PostgreSQL格式的SQL语句。\n\n"
        prompt += f"自然语言查询: {nl_query}\n\n"
        
        # 如果有数据库模式信息，添加到提示中
        if self.db_schema:
            prompt += "数据库模式信息如下:\n"
            for table_name, table_info in self.db_schema.items():
                prompt += f"表名: {table_name}\n"
                
                if table_info and "columns" in table_info:
                    prompt += "列:\n"
                    for col in table_info["columns"]:
                        col_name = col.get("name", "")
                        col_type = col.get("type", "")
                        prompt += f"  - {col_name} ({col_type})\n"
                
                # 添加主键信息
                if table_info and "primary_keys" in table_info and table_info["primary_keys"]:
                    primary_keys = ", ".join(table_info["primary_keys"])
                    prompt += f"  主键: {primary_keys}\n"
                
                # 添加外键信息
                if table_info and "foreign_keys" in table_info and table_info["foreign_keys"]:
                    prompt += "  外键:\n"
                    for fk in table_info["foreign_keys"]:
                        refer_table = fk.get("referred_table", "")
                        constrained_columns = ", ".join(fk.get("constrained_columns", []))
                        referred_columns = ", ".join(fk.get("referred_columns", []))
                        prompt += f"    - {constrained_columns} 引用 {refer_table}({referred_columns})\n"
                
                prompt += "\n"
        
        prompt += "请仅返回SQL查询语句，不需要解释。确保SQL语法正确，并使用PostgreSQL的语法特性。\n"
        prompt += "SQL查询:\n"
        
        return prompt
    
    def _extract_sql_from_text(self, text: str) -> str:
        """
        从生成的文本中提取SQL查询
        
        处理多种常见的模型输出格式，提取出实际的SQL语句
        
        Args:
            text: 生成的文本
            
        Returns:
            str: 提取的SQL查询
        """
        # 尝试从Markdown代码块中提取
        sql_match = re.search(r'```sql\s*(.*?)\s*```', text, re.DOTALL)
        if sql_match:
            return sql_match.group(1).strip()
        
        # 尝试从一般代码块中提取
        sql_match = re.search(r'```\s*(.*?)\s*```', text, re.DOTALL)
        if sql_match:
            return sql_match.group(1).strip()
        
        # 尝试查找常见的SQL关键字开始的行
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if re.match(r'^\s*(SELECT|WITH|CREATE|INSERT|UPDATE|DELETE)\s+', line, re.IGNORECASE):
                # 找到可能的SQL语句开始
                # 尝试提取完整SQL（多行，直到语句结束或文本结束）
                sql_lines = []
                for j in range(i, len(lines)):
                    sql_lines.append(lines[j])
                    if lines[j].strip().endswith(';'):
                        break
                
                return '\n'.join(sql_lines)
        
        # 如果没有明确的SQL标记，返回整个文本
        # 但尝试清理一些常见的文本模式
        text = text.strip()
        
        # 去除可能的前缀解释
        text = re.sub(r'^(好的|这是|以下是|下面是|Here is|Here\'s).*?:\s*', '', text, flags=re.IGNORECASE|re.DOTALL)
        
        # 去除结尾的解释
        text = re.sub(r'\n\s*(这个查询|这条SQL|这个SQL|This query|This SQL).*$', '', text, flags=re.IGNORECASE|re.DOTALL)
        
        return text.strip()
    
    def get_model_info(self) -> Dict[str, str]:
        """
        获取当前使用的模型信息
        
        Returns:
            Dict[str, str]: 模型信息
        """
        if self.model_type == "local":
            local_config = self.nlp_config.get("local", {})
            model_path = local_config.get("model_path", "未指定")
            
            device_info = "CPU"
            if torch and torch.cuda.is_available():
                device_info = f"CUDA ({torch.cuda.get_device_name(0)})"
            
            return {
                "model_type": "Hugging Face本地模型",
                "model_path": model_path,
                "device": device_info,
                "status": "已加载" if self.model else "未加载"
            }
        else:
            online_config = self.nlp_config.get("online", {})
            provider = online_config.get("provider", "未指定")
            model = online_config.get("model", "未指定")
            
            status = "未配置"
            if provider == "qwen" and dashscope and dashscope.api_key:
                status = "已配置"
            elif provider == "deepseek" and self.model:
                status = "已配置"
                
            return {
                "model_type": "在线API模型",
                "provider": provider,
                "model": model,
                "status": status
            } 