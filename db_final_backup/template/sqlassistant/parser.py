"""
SQL解析器模块 - 用于检查SQL语句语法、提供错误提示和建议
"""

import re
import sqlparse
import sqlglot
from sqlglot import parse, errors
from typing import Dict, List, Tuple, Any, Optional


class SQLParser:
    """
    SQL解析器，用于检查SQL语句的语法正确性并提供修改建议
    """
    
    def __init__(self, config: Dict):
        """
        初始化SQL解析器
        
        Args:
            config: 配置字典
        """
        self.config = config
        parser_config = config.get("parser", {})
        self.error_format = parser_config.get("error_format", "friendly")
        self.suggest_fixes = parser_config.get("suggest_fixes", True)
        self.dialect = parser_config.get("dialect", "sqlite")
    
    def set_dialect(self, dialect: str):
        """
        设置SQL方言
        
        Args:
            dialect: SQL方言（如sqlite, mysql, postgresql等）
        """
        self.dialect = dialect
    
    def check_query(self, sql: str) -> Tuple[bool, List[str], List[str]]:
        """
        检查SQL查询语句的语法正确性
        
        Args:
            sql: 要检查的SQL查询语句
            
        Returns:
            Tuple[bool, List[str], List[str]]: (是否有效, 错误列表, 建议列表)
        """
        # 初始化返回值
        is_valid = True
        errors_list = []
        suggestions = []
        
        # 格式化SQL语句以便检查
        formatted_sql = sqlparse.format(sql, reindent=True, keyword_case='upper')
        
        # 基本检查：空语句
        if not sql.strip():
            is_valid = False
            errors_list.append("SQL语句为空")
            suggestions.append("请输入有效的SQL语句")
            return is_valid, errors_list, suggestions
        
        # 使用sqlglot检查SQL语法
        try:
            # 尝试根据方言解析
            parse(sql, read=self.dialect)
        except errors.ParseError as e:
            is_valid = False
            
            # 获取原始错误消息
            error_msg = str(e)
            
            # 根据错误类型生成用户友好的错误消息
            friendly_error = self._get_friendly_error(error_msg, sql)
            errors_list.append(friendly_error)
            
            # 生成修改建议
            if self.suggest_fixes:
                fix_suggestion = self._generate_fix_suggestion(error_msg, sql)
                if fix_suggestion:
                    suggestions.append(fix_suggestion)
        
        # 进一步检查常见错误（即使基本语法正确）
        if is_valid:
            additional_errors, additional_suggestions = self._check_common_mistakes(sql)
            
            if additional_errors:
                is_valid = False
                errors_list.extend(additional_errors)
                suggestions.extend(additional_suggestions)
        
        return is_valid, errors_list, suggestions
    
    def _get_friendly_error(self, error_msg: str, sql: str) -> str:
        """
        将技术错误消息转换为用户友好的消息
        
        Args:
            error_msg: 原始错误消息
            sql: 原始SQL语句
            
        Returns:
            str: 用户友好的错误消息
        """
        # 提取错误位置信息（如果有）
        pos_match = re.search(r'at pos (\d+)', error_msg)
        error_pos = int(pos_match.group(1)) if pos_match else -1
        
        # 常见错误模式匹配
        if "Expected" in error_msg and "Found" in error_msg:
            expected_match = re.search(r'Expected: (.*?) Found:', error_msg)
            found_match = re.search(r'Found: (.*?)($|\(|at)', error_msg)
            
            if expected_match and found_match:
                expected = expected_match.group(1).strip()
                found = found_match.group(1).strip()
                
                return f"语法错误：期望 '{expected}'，但发现 '{found}'"
        
        if "unexpected token" in error_msg.lower():
            token_match = re.search(r"unexpected token: '(.*?)'", error_msg, re.IGNORECASE)
            if token_match:
                unexpected_token = token_match.group(1)
                return f"语法错误：意外的标记 '{unexpected_token}'"
        
        if "missing FROM clause" in error_msg.lower():
            return "语法错误：SELECT语句缺少FROM子句"
        
        if "no such column" in error_msg.lower():
            col_match = re.search(r"no such column: (.*?)($|\s|\()", error_msg, re.IGNORECASE)
            if col_match:
                column = col_match.group(1)
                return f"错误：列 '{column}' 不存在"
        
        # 如果无法识别具体错误，返回通用错误消息
        if error_pos >= 0 and error_pos < len(sql):
            context_start = max(0, error_pos - 10)
            context_end = min(len(sql), error_pos + 10)
            context = sql[context_start:context_end]
            marker_pos = error_pos - context_start
            
            marker = ' ' * marker_pos + '^'
            return f"SQL语法错误，问题位置附近: \n{context}\n{marker}"
        
        # 默认情况，简化原始错误
        return f"SQL语法错误: {error_msg}"
    
    def _generate_fix_suggestion(self, error_msg: str, sql: str) -> Optional[str]:
        """
        根据错误消息生成修复建议
        
        Args:
            error_msg: 原始错误消息
            sql: 原始SQL语句
            
        Returns:
            Optional[str]: 修复建议或None
        """
        # 缺少FROM子句
        if "missing FROM clause" in error_msg.lower():
            return "添加FROM子句指定表名，例如：'FROM table_name'"
        
        # 关键字拼写错误的模糊匹配
        common_keywords = ["SELECT", "FROM", "WHERE", "GROUP BY", "ORDER BY", "HAVING", 
                         "JOIN", "INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "ON", "AND", "OR"]
        
        # 单词拼写错误检查
        words = re.findall(r'\b\w+\b', sql.upper())
        for word in words:
            # 跳过数字和短词
            if word.isdigit() or len(word) <= 2:
                continue
            
            # 检查关键字的相似度
            for keyword in common_keywords:
                # 检查编辑距离或简单拼写错误
                if self._is_similar(word, keyword.replace(" ", "")) and word != keyword.replace(" ", ""):
                    return f"'{word}' 可能是 '{keyword}' 的拼写错误"
        
        # 括号不匹配
        if "parentheses" in error_msg.lower() or "bracket" in error_msg.lower():
            open_count = sql.count('(')
            close_count = sql.count(')')
            
            if open_count > close_count:
                return f"SQL语句缺少 {open_count - close_count} 个右括号 ')'"
            elif close_count > open_count:
                return f"SQL语句有 {close_count - open_count} 个多余的右括号 ')'"
        
        # 缺少关键字
        if "Expected" in error_msg:
            expected_match = re.search(r'Expected: (.*?) Found:', error_msg)
            if expected_match:
                expected = expected_match.group(1).strip()
                return f"在此位置需要关键字 '{expected}'"
        
        # 列不存在
        if "no such column" in error_msg.lower():
            col_match = re.search(r"no such column: (.*?)($|\s|\()", error_msg, re.IGNORECASE)
            if col_match:
                column = col_match.group(1)
                return f"检查列名 '{column}' 是否拼写正确，或者表名是否需要限定"
        
        # 表不存在
        if "no such table" in error_msg.lower():
            table_match = re.search(r"no such table: (.*?)($|\s|\()", error_msg, re.IGNORECASE)
            if table_match:
                table = table_match.group(1)
                return f"检查表名 '{table}' 是否拼写正确，或者该表是否存在于数据库中"
        
        # 默认建议
        return "检查SQL语法，确保所有关键字拼写正确并且结构完整"
    
    def _is_similar(self, word1: str, word2: str) -> bool:
        """
        检查两个单词是否相似（用于拼写检查）
        
        Args:
            word1: 第一个单词
            word2: 第二个单词
            
        Returns:
            bool: 是否相似
        """
        # 如果两个词完全一样，返回False（不需要建议）
        if word1 == word2:
            return False
        
        # 对于短词，只有一个字符不同才算相似
        if len(word1) <= 4 or len(word2) <= 4:
            return self._levenshtein_distance(word1, word2) <= 1
        
        # 对于长词，允许更多的差异
        max_len = max(len(word1), len(word2))
        threshold = max(1, max_len // 3)  # 允许1/3的字符不同
        
        return self._levenshtein_distance(word1, word2) <= threshold
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """
        计算两个字符串的编辑距离
        
        Args:
            s1: 第一个字符串
            s2: 第二个字符串
            
        Returns:
            int: 编辑距离
        """
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if not s2:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def _check_common_mistakes(self, sql: str) -> Tuple[List[str], List[str]]:
        """
        检查常见错误模式
        
        Args:
            sql: SQL查询语句
            
        Returns:
            Tuple[List[str], List[str]]: (错误列表, 建议列表)
        """
        errors = []
        suggestions = []
        
        # 检查是否使用了逗号而不是AND或OR
        if re.search(r'WHERE.*?[^,]\s*,\s*[^,]', sql, re.IGNORECASE):
            errors.append("WHERE子句中逗号的使用可能不正确")
            suggestions.append("在WHERE子句中，条件应使用AND或OR连接，而不是逗号")
        
        # 检查表连接语法
        if re.search(r'FROM\s+(\w+)\s*,\s*(\w+)', sql, re.IGNORECASE) and not re.search(r'JOIN', sql, re.IGNORECASE):
            errors.append("使用了隐式连接语法")
            suggestions.append("建议使用显式JOIN语法代替逗号分隔表名")
        
        # 检查GROUP BY与非聚合函数
        if re.search(r'GROUP BY', sql, re.IGNORECASE):
            select_clause = re.search(r'SELECT\s+(.*?)\s+FROM', sql, re.IGNORECASE)
            if select_clause:
                select_items = select_clause.group(1).split(',')
                for item in select_items:
                    # 如果选择项不是聚合函数且不在GROUP BY中
                    if not re.search(r'(COUNT|SUM|AVG|MIN|MAX)\s*\(', item, re.IGNORECASE) and not re.search(r'\*', item):
                        item_clean = item.strip()
                        if not re.search(rf'GROUP BY\s+.*{re.escape(item_clean)}', sql, re.IGNORECASE):
                            errors.append(f"选择项'{item.strip()}'可能需要包含在GROUP BY子句中")
                            suggestions.append("非聚合列应该包含在GROUP BY子句中")
                            break
        
        # 检查ORDER BY中的列是否存在于SELECT
        order_by_match = re.search(r'ORDER BY\s+(.*?)($|;|\s+LIMIT)', sql, re.IGNORECASE)
        if order_by_match:
            order_items = order_by_match.group(1).split(',')
            for item in order_items:
                # 提取列名（忽略ASC/DESC）
                col_name = re.sub(r'\s+(ASC|DESC)$', '', item.strip(), flags=re.IGNORECASE).strip()
                # 如果是数字，表示按照位置排序，则跳过
                if col_name.isdigit():
                    continue
                
                # 如果不是数字且不在SELECT中
                select_clause = re.search(r'SELECT\s+(.*?)\s+FROM', sql, re.IGNORECASE)
                if select_clause and not re.search(rf'{re.escape(col_name)}', select_clause.group(1)):
                    errors.append(f"ORDER BY中的列 '{col_name}' 可能不在SELECT列表中")
                    suggestions.append("确保ORDER BY中使用的列在SELECT列表中或使用位置索引")
                    break
        
        return errors, suggestions 