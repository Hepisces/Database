"""
命令行接口模块 - 提供命令行工具的主要交互功能
"""

import os
import typer
from typing import Optional
from rich.console import Console
from rich.table import Table

from .db import DatabaseManager
from .parser import SQLParser
from .visualizer import QueryVisualizer
from .nlp import NLProcessor
from .utils import load_config

# 创建命令行应用
app = typer.Typer(
    name="sqlassistant",
    help="SQL助手：SQL语句检查、可视化和自然语言查询工具",
    add_completion=False,
)

console = Console()
config = load_config()

# 初始化各模块
db_manager = DatabaseManager(config)
sql_parser = SQLParser(config)
visualizer = QueryVisualizer(config)
nlp_processor = NLProcessor(config)


@app.command()
def init(
    db_path: Optional[str] = typer.Option(
        None, "--path", "-p", help="数据库路径，默认使用配置文件中的设置"
    )
):
    """
    初始化并创建数据库
    """
    if db_path:
        db_manager.set_db_path(db_path)
    
    success = db_manager.initialize_database()
    
    if success:
        console.print("[green]数据库初始化成功！[/green]")
    else:
        console.print("[red]数据库初始化失败！[/red]")


@app.command()
def schema(
    action: str = typer.Argument(..., help="操作类型: import, list"),
    file: Optional[str] = typer.Option(None, "--file", "-f", help="存有关系模式的SQL文件")
):
    """
    管理数据库关系模式
    """
    if action == "import" and file:
        if not os.path.exists(file):
            console.print(f"[red]文件 {file} 不存在[/red]")
            raise typer.Exit(1)
        
        with open(file, "r", encoding="utf-8") as f:
            schema_sql = f.read()
        
        success, message = db_manager.import_schema(schema_sql)
        
        if success:
            console.print("[green]成功导入关系模式！[/green]")
        else:
            console.print(f"[red]导入关系模式失败: {message}[/red]")
    
    elif action == "list":
        tables = db_manager.list_tables()
        
        if not tables:
            console.print("[yellow]数据库中没有表[/yellow]")
            return
        
        table = Table(title="数据库中的表")
        table.add_column("表名")
        table.add_column("列数")
        
        for table_name, column_count in tables:
            table.add_row(table_name, str(column_count))
        
        console.print(table)
    
    else:
        console.print("[red]无效的操作类型。请使用 'import' 或 'list'[/red]")


@app.command()
def check(
    sql: str = typer.Argument(..., help="要检查的SQL查询语句"),
    dialect: Optional[str] = typer.Option(None, "--dialect", "-d", help="SQL方言")
):
    """
    检查SQL查询语句的正确性并给出建议
    """
    if dialect:
        sql_parser.set_dialect(dialect)
    
    is_valid, errors, suggestions = sql_parser.check_query(sql)
    
    if is_valid:
        console.print("[green]SQL语句语法正确！[/green]")
    else:
        console.print("[red]SQL语句存在错误:[/red]")
        for error in errors:
            console.print(f"  - {error}")
        
        if suggestions:
            console.print("\n[yellow]修改建议:[/yellow]")
            for suggestion in suggestions:
                console.print(f"  - {suggestion}")


@app.command()
def query(
    sql: str = typer.Argument(..., help="要执行的SQL查询语句"),
    visualize: bool = typer.Option(False, "--visualize", "-v", help="是否可视化查询结果"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="输出文件路径")
):
    """
    执行SQL查询并可选择可视化结果
    """
    # 首先检查SQL语法
    is_valid, errors, _ = sql_parser.check_query(sql)
    
    if not is_valid:
        console.print("[red]SQL语句存在错误，请先修正:[/red]")
        for error in errors:
            console.print(f"  - {error}")
        raise typer.Exit(1)
    
    # 执行查询
    success, result = db_manager.execute_query(sql)
    
    if not success:
        console.print(f"[red]查询执行失败: {result}[/red]")
        raise typer.Exit(1)
    
    # 显示结果
    if visualize:
        visualizer.visualize_query_result(sql, result, output_path=output)
    else:
        # 仅显示表格结果
        if not result or not result.get("data"):
            console.print("[yellow]查询未返回数据[/yellow]")
            return
        
        table = Table(title="查询结果")
        
        # 添加列
        columns = result.get("columns", [])
        for column in columns:
            table.add_column(column)
        
        # 添加数据行
        for row in result.get("data", []):
            table.add_row(*[str(cell) for cell in row])
        
        console.print(table)
        console.print(f"返回 {len(result.get('data', []))} 行数据")


@app.command()
def nlquery(
    query: str = typer.Argument(..., help="自然语言查询"),
    visualize: bool = typer.Option(False, "--visualize", "-v", help="是否可视化查询结果"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="输出文件路径")
):
    """
    使用自然语言查询数据库
    """
    console.print(f"[blue]处理自然语言查询: '{query}'[/blue]")
    
    # 将自然语言转换为SQL
    success, sql = nlp_processor.translate_to_sql(query)
    
    if not success:
        console.print(f"[red]无法将自然语言转换为SQL: {sql}[/red]")
        raise typer.Exit(1)
    
    console.print(f"[green]生成的SQL查询:[/green] {sql}")
    
    # 执行SQL查询
    success, result = db_manager.execute_query(sql)
    
    if not success:
        console.print(f"[red]查询执行失败: {result}[/red]")
        raise typer.Exit(1)
    
    # 显示结果
    if visualize:
        visualizer.visualize_query_result(sql, result, output_path=output, title=query)
    else:
        # 仅显示表格结果
        if not result or not result.get("data"):
            console.print("[yellow]查询未返回数据[/yellow]")
            return
        
        table = Table(title="查询结果")
        
        # 添加列
        columns = result.get("columns", [])
        for column in columns:
            table.add_column(column)
        
        # 添加数据行
        for row in result.get("data", []):
            table.add_row(*[str(cell) for cell in row])
        
        console.print(table)
        console.print(f"返回 {len(result.get('data', []))} 行数据")


@app.command()
def reset(
    force: bool = typer.Option(False, "--force", "-f", help="强制重置，不提示确认")
):
    """
    重置系统，清除数据库和相关资源
    """
    if not force:
        confirm = typer.confirm("此操作将删除所有数据库内容和相关资源。确认继续?")
        if not confirm:
            console.print("[yellow]操作已取消[/yellow]")
            raise typer.Exit(0)
    
    success = db_manager.reset_database()
    
    if success:
        console.print("[green]系统已成功重置！[/green]")
    else:
        console.print("[red]系统重置失败！[/red]")


def main():
    """
    主函数，用于直接运行模块
    """
    app()


if __name__ == "__main__":
    main() 