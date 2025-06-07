"""
查询可视化模块 - 可视化SQL查询结果和查询流程
"""

import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from typing import Dict, List, Any, Optional, Union
import sqlite3
import io
from sqlalchemy import create_engine
import plotly.express as px
import plotly.graph_objects as go
import sqlparse


class QueryVisualizer:
    """
    查询结果和流程可视化工具
    """
    
    def __init__(self, config: Dict):
        """
        初始化查询可视化器
        
        Args:
            config: 配置字典
        """
        self.config = config
        vis_config = config.get("visualization", {})
        self.engine = vis_config.get("engine", "matplotlib")
        self.theme = vis_config.get("theme", "default")
        self.show_query_plan = vis_config.get("query_plan", True)
        self.max_results = vis_config.get("max_results", 1000)
        
        # 设置matplotlib样式
        if self.engine == "matplotlib":
            plt.style.use('ggplot' if self.theme == "default" else self.theme)
    
    def visualize_query_result(
        self, 
        query: str, 
        result: Dict[str, Any], 
        output_path: Optional[str] = None,
        title: Optional[str] = None
    ):
        """
        可视化查询结果
        
        Args:
            query: 原始SQL查询
            result: 查询结果字典，包含列名和数据
            output_path: 输出文件路径（可选）
            title: 可视化标题（可选）
        """
        if not result or not result.get("data"):
            print("无数据可视化")
            return
        
        # 将结果转换为DataFrame
        df = pd.DataFrame(result.get("data", []), columns=result.get("columns", []))
        
        # 限制结果数量
        if len(df) > self.max_results:
            print(f"结果太大，只可视化前 {self.max_results} 行")
            df = df.head(self.max_results)
        
        # 尝试推断查询类型并选择合适的可视化方法
        query_type = self._infer_query_type(query)
        
        # 如果提供了标题，使用它
        vis_title = title if title else f"查询结果 - {query_type}"
        
        # 根据查询类型选择可视化方法
        if query_type == "聚合分析":
            self._visualize_aggregation(df, output_path, vis_title)
        elif query_type == "时间序列":
            self._visualize_time_series(df, output_path, vis_title)
        elif query_type == "多表关联":
            self._visualize_joined_data(df, output_path, vis_title)
        else:
            # 默认表格展示
            self._visualize_general_result(df, output_path, vis_title)
        
        # 如果开启了查询计划可视化，则也显示查询计划
        if self.show_query_plan:
            self._visualize_query_plan(query, output_path)
    
    def _infer_query_type(self, query: str) -> str:
        """
        推断查询类型以选择合适的可视化方法
        
        Args:
            query: SQL查询语句
            
        Returns:
            str: 查询类型描述
        """
        # 格式化查询用于分析
        formatted_query = sqlparse.format(query.strip(), reindent=True, keyword_case='upper')
        
        # 检查是否是聚合查询
        if re.search(r'(COUNT|SUM|AVG|MIN|MAX)\s*\(', formatted_query, re.IGNORECASE):
            if re.search(r'GROUP BY', formatted_query, re.IGNORECASE):
                return "聚合分析"
        
        # 检查是否是时间序列查询
        date_patterns = [
            r'DATE', r'TIMESTAMP', r'TIME', r'INTERVAL', 
            r'\d{4}-\d{2}-\d{2}', r'EXTRACT\s*\(\s*YEAR|MONTH|DAY\s*FROM'
        ]
        for pattern in date_patterns:
            if re.search(pattern, formatted_query, re.IGNORECASE):
                return "时间序列"
        
        # 检查是否是连接查询
        if re.search(r'JOIN', formatted_query, re.IGNORECASE) or re.search(r'FROM\s+\w+\s*,\s*\w+', formatted_query, re.IGNORECASE):
            return "多表关联"
        
        # 默认类型
        return "一般查询"
    
    def _visualize_aggregation(self, df: pd.DataFrame, output_path: Optional[str], title: str):
        """
        可视化聚合查询结果
        
        Args:
            df: 结果数据框
            output_path: 输出路径
            title: 可视化标题
        """
        # 检查是否有数值列
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if not numeric_cols:
            print("聚合查询结果中没有数值列，使用表格展示")
            self._visualize_general_result(df, output_path, title)
            return
        
        # 找出合适的类别列和数值列
        category_cols = [col for col in df.columns if col not in numeric_cols]
        
        if not category_cols:
            # 如果没有类别列，显示数值分布直方图
            if self.engine == "matplotlib":
                fig, axes = plt.subplots(len(numeric_cols), 1, figsize=(10, 4*len(numeric_cols)))
                if len(numeric_cols) == 1:
                    axes = [axes]
                
                for i, col in enumerate(numeric_cols):
                    df[col].plot(kind='bar', ax=axes[i], title=f"{col}分布")
                    axes[i].set_ylabel(col)
                
                plt.tight_layout()
                plt.suptitle(title, fontsize=16, y=1.02)
                
                if output_path:
                    plt.savefig(output_path, bbox_inches='tight')
                plt.show()
            else:  # plotly
                fig = go.Figure()
                for col in numeric_cols:
                    fig.add_trace(go.Bar(y=df[col], name=col))
                
                fig.update_layout(title=title, barmode='group')
                
                if output_path:
                    fig.write_image(output_path)
                fig.show()
        
        else:
            # 有类别列，使用柱状图或饼图
            main_category = category_cols[0]
            main_metric = numeric_cols[0]
            
            if len(df) <= 10:  # 对于较小的结果集，使用饼图
                if self.engine == "matplotlib":
                    plt.figure(figsize=(10, 8))
                    plt.pie(df[main_metric], labels=df[main_category], autopct='%1.1f%%')
                    plt.title(title)
                    
                    if output_path:
                        plt.savefig(output_path, bbox_inches='tight')
                    plt.show()
                else:  # plotly
                    fig = px.pie(df, values=main_metric, names=main_category, title=title)
                    
                    if output_path:
                        fig.write_image(output_path)
                    fig.show()
            
            else:  # 对于较大的结果集，使用柱状图
                if self.engine == "matplotlib":
                    plt.figure(figsize=(12, 8))
                    df.set_index(main_category)[main_metric].plot(kind='bar')
                    plt.title(title)
                    plt.xticks(rotation=45, ha='right')
                    plt.tight_layout()
                    
                    if output_path:
                        plt.savefig(output_path, bbox_inches='tight')
                    plt.show()
                else:  # plotly
                    fig = px.bar(df, x=main_category, y=main_metric, title=title)
                    
                    if output_path:
                        fig.write_image(output_path)
                    fig.show()
    
    def _visualize_time_series(self, df: pd.DataFrame, output_path: Optional[str], title: str):
        """
        可视化时间序列数据
        
        Args:
            df: 结果数据框
            output_path: 输出路径
            title: 可视化标题
        """
        # 尝试找出日期/时间列
        date_cols = []
        for col in df.columns:
            # 检查列名是否包含日期相关字符
            if any(term in col.lower() for term in ['date', 'time', 'year', 'month', 'day']):
                date_cols.append(col)
        
        # 如果找不到日期列，尝试根据数据类型推断
        if not date_cols:
            for col in df.columns:
                # 尝试转换为日期类型
                try:
                    pd.to_datetime(df[col])
                    date_cols.append(col)
                except:
                    continue
        
        # 如果还是找不到日期列，返回一般可视化
        if not date_cols:
            print("无法识别时间序列数据，使用表格展示")
            self._visualize_general_result(df, output_path, title)
            return
        
        date_col = date_cols[0]  # 使用第一个识别出的日期列
        
        # 尝试转换为日期类型
        try:
            df[date_col] = pd.to_datetime(df[date_col])
        except:
            # 如果无法转换，仍然用原始值
            pass
        
        # 找出数值列
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        numeric_cols = [col for col in numeric_cols if col != date_col]  # 排除日期列（如果是数值的）
        
        if not numeric_cols:
            print("时间序列数据中没有数值列，使用表格展示")
            self._visualize_general_result(df, output_path, title)
            return
        
        # 绘制时间序列图
        if self.engine == "matplotlib":
            plt.figure(figsize=(12, 8))
            for col in numeric_cols[:3]:  # 限制到3个系列以避免过于拥挤
                plt.plot(df[date_col], df[col], label=col, marker='o')
            
            plt.xlabel(date_col)
            plt.ylabel("值")
            plt.title(title)
            plt.legend()
            plt.grid(True)
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            if output_path:
                plt.savefig(output_path, bbox_inches='tight')
            plt.show()
        else:  # plotly
            fig = go.Figure()
            for col in numeric_cols[:5]:  # plotly可以处理更多系列
                fig.add_trace(go.Scatter(x=df[date_col], y=df[col], mode='lines+markers', name=col))
            
            fig.update_layout(
                title=title,
                xaxis_title=date_col,
                yaxis_title="值",
                legend_title="指标"
            )
            
            if output_path:
                fig.write_image(output_path)
            fig.show()
    
    def _visualize_joined_data(self, df: pd.DataFrame, output_path: Optional[str], title: str):
        """
        可视化多表关联数据
        
        Args:
            df: 结果数据框
            output_path: 输出路径
            title: 可视化标题
        """
        # 对于关联查询，尝试创建散点图或多维分析
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        if len(numeric_cols) >= 2:
            # 有两个以上数值列，可以创建散点图
            if self.engine == "matplotlib":
                plt.figure(figsize=(10, 8))
                plt.scatter(df[numeric_cols[0]], df[numeric_cols[1]])
                plt.xlabel(numeric_cols[0])
                plt.ylabel(numeric_cols[1])
                plt.title(title)
                plt.grid(True)
                
                if output_path:
                    plt.savefig(output_path, bbox_inches='tight')
                plt.show()
            else:  # plotly
                # 如果有第三个数值列，用颜色表示
                if len(numeric_cols) >= 3:
                    fig = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1], 
                                    color=numeric_cols[2], title=title)
                else:
                    fig = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1], title=title)
                
                if output_path:
                    fig.write_image(output_path)
                fig.show()
        else:
            # 否则使用普通表格展示
            self._visualize_general_result(df, output_path, title)
    
    def _visualize_general_result(self, df: pd.DataFrame, output_path: Optional[str], title: str):
        """
        通用的结果可视化，适用于无法分类或数据较少的情况
        
        Args:
            df: 结果数据框
            output_path: 输出路径
            title: 可视化标题
        """
        if len(df) == 0:
            print("查询结果为空")
            return
        
        # 对于小型结果集，直接显示表格
        if len(df) <= 50:
            if self.engine == "matplotlib":
                fig, ax = plt.subplots(figsize=(12, len(df) * 0.5 + 2))
                ax.axis('off')
                table = ax.table(
                    cellText=df.values,
                    colLabels=df.columns,
                    loc='center',
                    cellLoc='center'
                )
                table.auto_set_font_size(False)
                table.set_fontsize(10)
                table.scale(1.2, 1.2)
                plt.title(title)
                
                if output_path:
                    plt.savefig(output_path, bbox_inches='tight')
                plt.show()
            else:  # plotly
                fig = go.Figure(data=[go.Table(
                    header=dict(values=list(df.columns)),
                    cells=dict(values=[df[col] for col in df.columns]))
                ])
                fig.update_layout(title=title)
                
                if output_path:
                    fig.write_image(output_path)
                fig.show()
        
        # 对于大型结果集，尝试创建热图或其他摘要可视化
        else:
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            
            if len(numeric_cols) >= 2:
                # 创建相关性热图
                if self.engine == "matplotlib":
                    plt.figure(figsize=(10, 8))
                    corr = df[numeric_cols].corr()
                    cmap = plt.cm.Blues
                    plt.imshow(corr, cmap=cmap)
                    plt.colorbar()
                    plt.xticks(range(len(corr)), corr.columns, rotation=45)
                    plt.yticks(range(len(corr)), corr.columns)
                    plt.title(f"{title} - 数值字段相关性")
                    
                    # 添加相关系数文本
                    for i in range(len(corr)):
                        for j in range(len(corr)):
                            plt.text(j, i, f"{corr.iloc[i, j]:.2f}",
                                   ha="center", va="center", color="black")
                    
                    plt.tight_layout()
                    
                    if output_path:
                        plt.savefig(output_path, bbox_inches='tight')
                    plt.show()
                else:  # plotly
                    corr = df[numeric_cols].corr()
                    fig = px.imshow(corr, title=f"{title} - 数值字段相关性")
                    
                    if output_path:
                        fig.write_image(output_path)
                    fig.show()
            else:
                # 如果没有足够的数值列，显示数据分布
                if self.engine == "matplotlib":
                    # 选择最多5个列进行可视化
                    cols_to_plot = df.columns[:5]
                    fig, axes = plt.subplots(len(cols_to_plot), 1, figsize=(10, 3*len(cols_to_plot)))
                    
                    if len(cols_to_plot) == 1:
                        axes = [axes]
                    
                    for i, col in enumerate(cols_to_plot):
                        if df[col].dtype.kind in 'ifc':  # 数值列
                            df[col].hist(ax=axes[i], bins=20)
                        else:  # 分类列
                            df[col].value_counts().plot(kind='bar', ax=axes[i])
                        
                        axes[i].set_title(f"{col}分布")
                    
                    plt.tight_layout()
                    plt.suptitle(title, fontsize=16, y=1.02)
                    
                    if output_path:
                        plt.savefig(output_path, bbox_inches='tight')
                    plt.show()
                else:  # plotly
                    # 创建子图
                    from plotly.subplots import make_subplots
                    cols_to_plot = df.columns[:5]
                    
                    fig = make_subplots(rows=len(cols_to_plot), cols=1, 
                                       subplot_titles=[f"{col}分布" for col in cols_to_plot])
                    
                    for i, col in enumerate(cols_to_plot):
                        if df[col].dtype.kind in 'ifc':  # 数值列
                            fig.add_trace(
                                go.Histogram(x=df[col], name=col),
                                row=i+1, col=1
                            )
                        else:  # 分类列
                            counts = df[col].value_counts()
                            fig.add_trace(
                                go.Bar(x=counts.index, y=counts.values, name=col),
                                row=i+1, col=1
                            )
                    
                    fig.update_layout(height=300*len(cols_to_plot), title_text=title)
                    
                    if output_path:
                        fig.write_image(output_path)
                    fig.show()
    
    def _visualize_query_plan(self, query: str, output_path: Optional[str] = None):
        """
        可视化查询执行计划
        
        Args:
            query: SQL查询语句
            output_path: 输出文件路径（可选）
        """
        # 这个功能需要SQLite或其他支持EXPLAIN的数据库
        # 为简单起见，这里使用SQLite实现
        try:
            # 创建临时内存数据库来分析查询计划
            conn = sqlite3.connect(":memory:")
            
            # 提取查询中的表名
            tables = self._extract_tables_from_query(query)
            
            # 为查询中的表创建临时表结构
            for table in tables:
                conn.execute(f"CREATE TABLE {table} (id INTEGER);")
            
            # 获取执行计划
            explain_query = f"EXPLAIN QUERY PLAN {query}"
            plan_result = conn.execute(explain_query).fetchall()
            
            # 关闭连接
            conn.close()
            
            # 解析执行计划
            plan_data = []
            for row in plan_result:
                plan_data.append({
                    "id": row[0],
                    "parent": row[1],
                    "detail": row[3]
                })
            
            # 可视化计划为树形结构
            if not plan_data:
                print("无法获取查询计划")
                return
            
            if self.engine == "matplotlib":
                # 使用matplotlib创建简单的树状图
                fig, ax = plt.subplots(figsize=(12, len(plan_data) * 0.8 + 2))
                y_positions = {}
                max_depth = 0
                
                # 递归构建树
                def build_tree(node_id, depth, y):
                    nonlocal max_depth
                    max_depth = max(max_depth, depth)
                    
                    # 当前节点
                    node = next((n for n in plan_data if n["id"] == node_id), None)
                    if not node:
                        return y
                    
                    # 保存位置
                    y_positions[node_id] = y
                    
                    # 查找子节点
                    children = [n for n in plan_data if n["parent"] == node_id]
                    next_y = y
                    
                    # 递归处理子节点
                    for child in children:
                        next_y = build_tree(child["id"], depth + 1, next_y) + 1
                    
                    return next_y if children else y + 1
                
                # 找出根节点
                root_nodes = [n for n in plan_data if n["parent"] == -1]
                y = 0
                for root in root_nodes:
                    y = build_tree(root["id"], 0, y)
                
                # 绘制节点和连接线
                for node in plan_data:
                    node_id = node["id"]
                    parent_id = node["parent"]
                    detail = node["detail"]
                    
                    # 找出节点深度
                    depth = 0
                    temp_parent = parent_id
                    while temp_parent != -1:
                        parent_node = next((n for n in plan_data if n["id"] == temp_parent), None)
                        if not parent_node:
                            break
                        depth += 1
                        temp_parent = parent_node["parent"]
                    
                    # 绘制节点
                    x = depth
                    y = y_positions[node_id]
                    ax.text(x, -y, detail, ha='left', va='center', 
                          bbox=dict(facecolor='lightblue', alpha=0.5))
                    
                    # 绘制连接线
                    if parent_id != -1 and parent_id in y_positions:
                        parent_x = depth - 1
                        parent_y = y_positions[parent_id]
                        ax.plot([parent_x + 0.3, x - 0.1], [-parent_y, -y], 'k-')
                
                ax.set_xlim(-0.5, max_depth + 2)
                ax.set_ylim(-y - 0.5, 0.5)
                ax.axis('off')
                plt.title("查询执行计划")
                
                if output_path and isinstance(output_path, str):
                    plan_output = os.path.splitext(output_path)[0] + "_plan" + os.path.splitext(output_path)[1]
                    plt.savefig(plan_output, bbox_inches='tight')
                plt.show()
            
            else:  # plotly
                # 使用plotly创建交互式树状图
                import networkx as nx
                
                # 构建图
                G = nx.DiGraph()
                
                # 添加节点和边
                for node in plan_data:
                    node_id = node["id"]
                    parent_id = node["parent"]
                    G.add_node(node_id, label=node["detail"])
                    
                    if parent_id != -1:
                        G.add_edge(parent_id, node_id)
                
                # 计算布局
                pos = nx.nx_pydot.graphviz_layout(G, prog="dot")
                
                # 创建边的跟踪
                edge_x = []
                edge_y = []
                for edge in G.edges():
                    x0, y0 = pos[edge[0]]
                    x1, y1 = pos[edge[1]]
                    edge_x.extend([x0, x1, None])
                    edge_y.extend([y0, y1, None])
                
                edge_trace = go.Scatter(
                    x=edge_x, y=edge_y,
                    line=dict(width=1, color='#888'),
                    hoverinfo='none',
                    mode='lines')
                
                # 创建节点的跟踪
                node_x = []
                node_y = []
                node_text = []
                for node in G.nodes():
                    x, y = pos[node]
                    node_x.append(x)
                    node_y.append(y)
                    node_text.append(G.nodes[node]['label'])
                
                node_trace = go.Scatter(
                    x=node_x, y=node_y,
                    mode='markers+text',
                    text=node_text,
                    textposition="top center",
                    hoverinfo='text',
                    marker=dict(
                        color='lightblue',
                        size=15,
                        line=dict(width=2)))
                
                # 创建图形
                fig = go.Figure(data=[edge_trace, node_trace],
                             layout=go.Layout(
                                title="查询执行计划",
                                showlegend=False,
                                hovermode='closest',
                                margin=dict(b=20, l=5, r=5, t=40),
                                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))
                
                if output_path and isinstance(output_path, str):
                    plan_output = os.path.splitext(output_path)[0] + "_plan" + os.path.splitext(output_path)[1]
                    fig.write_image(plan_output)
                fig.show()
        
        except Exception as e:
            print(f"无法生成查询计划可视化: {str(e)}")
    
    def _extract_tables_from_query(self, query: str) -> List[str]:
        """
        从查询中提取表名
        
        Args:
            query: SQL查询语句
            
        Returns:
            List[str]: 表名列表
        """
        # 格式化查询
        formatted_query = sqlparse.format(query.strip(), reindent=True, keyword_case='upper')
        
        # 从FROM子句中提取表名
        from_match = re.search(r'FROM\s+(.*?)(?:WHERE|GROUP BY|ORDER BY|LIMIT|$)', formatted_query, re.IGNORECASE | re.DOTALL)
        if not from_match:
            return []
        
        from_clause = from_match.group(1).strip()
        
        # 处理简单的多表查询（逗号分隔）
        if ',' in from_clause and 'JOIN' not in from_clause.upper():
            tables = [t.strip() for t in from_clause.split(',')]
            return [self._clean_table_name(t) for t in tables]
        
        # 处理JOIN
        if 'JOIN' in from_clause.upper():
            join_parts = re.split(r'\s+(?:LEFT|RIGHT|INNER|OUTER|CROSS|FULL)?\s+JOIN\s+', from_clause, flags=re.IGNORECASE)
            tables = [join_parts[0].strip()]  # 第一个表
            
            # 提取JOIN表
            for part in join_parts[1:]:
                on_match = re.search(r'(.*?)(?:ON|USING)', part, re.IGNORECASE | re.DOTALL)
                if on_match:
                    tables.append(on_match.group(1).strip())
                else:
                    tables.append(part.strip())
            
            return [self._clean_table_name(t) for t in tables]
        
        # 单表查询
        return [self._clean_table_name(from_clause)]
    
    def _clean_table_name(self, table_name: str) -> str:
        """
        清理表名（去除别名等）
        
        Args:
            table_name: 原始表名字符串
            
        Returns:
            str: 清理后的表名
        """
        # 去除可能的别名
        if ' AS ' in table_name.upper():
            table_name = table_name.split(' AS ')[0].strip()
        elif ' ' in table_name:
            table_name = table_name.split(' ')[0].strip()
        
        # 去除任何括号
        table_name = table_name.strip('()')
        
        # 去除模式名前缀
        if '.' in table_name:
            table_name = table_name.split('.')[-1]
        
        return table_name 