# -*- coding: utf-8 -*-
"""
数据库备份与恢复脚本

该脚本用于备份和恢复PostgreSQL数据库，基于项目的配置文件获取数据库连接信息。
"""

import os
import sys
import psycopg2
import argparse
from datetime import datetime
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import Config

def get_db_connection():
    """
    获取数据库连接
    """
    try:
        # 解析数据库连接字符串
        db_uri = Config.SQLALCHEMY_DATABASE_URI
        
        # 提取协议部分后的内容
        db_uri = db_uri.split('://')[1]
        
        # 分离用户密码与主机数据库部分
        user_pass_part, host_db_part = db_uri.split('@')
        
        # 解析用户名和密码
        user = user_pass_part.split(':')[0]
        password = user_pass_part.split(':')[1]
        
        # 解析主机、端口和数据库名
        host_port_part, dbname = host_db_part.split('/')
        host = host_port_part.split(':')[0]
        port = host_port_part.split(':')[1]
        
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        return conn
    except Exception as e:
        print(f"连接数据库失败: {e}")
        sys.exit(1)

def backup_database(backup_file):
    """
    备份数据库
    """
    print(f"开始备份数据库到 {backup_file}...")
    
    # 使用psycopg2执行pg_dump命令
    result = os.system(f"pg_dump -h localhost -p 5432 -U postgres -d gradpush -f {backup_file} --password")
    
    if result != 0:
        raise Exception(f"pg_dump命令执行失败，退出码: {result}")
    
    print(f"数据库备份完成: {backup_file}")

def backup_database_python(backup_file):
    """
    使用Python代码备份数据库（备选方案，当pg_dump不可用时）
    """
    print(f"开始使用Python备份数据库到 {backup_file}...")
    
    conn = get_db_connection()
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    try:
        # 创建备份文件
        with open(backup_file, 'w', encoding='utf-8') as f:
            # 第一步：备份所有序列
            print("备份序列...")
            # 使用pg_get_serial_sequence获取所有表的序列
            cursor.execute("""
                SELECT
                    t.table_name,
                    c.column_name,
                    pg_get_serial_sequence(t.table_name::text, c.column_name::text) AS sequence_name
                FROM
                    information_schema.tables t
                JOIN
                    information_schema.columns c ON t.table_name = c.table_name AND t.table_schema = c.table_schema
                WHERE
                    t.table_schema = 'public' AND
                    t.table_type = 'BASE TABLE' AND
                    c.column_default LIKE '%nextval%'
            """)
            serial_sequences = cursor.fetchall()
            
            sequences = set()
            for row in serial_sequences:
                sequence_name = row[2]
                if sequence_name:
                    sequences.add(sequence_name)
            
            # 也直接获取所有序列
            cursor.execute("SELECT sequence_name FROM information_schema.sequences WHERE sequence_schema = 'public'")
            direct_sequences = cursor.fetchall()
            for seq in direct_sequences:
                sequences.add(f"public.{seq[0]}")
            
            if sequences:
                for seq_name in sequences:
                    f.write(f"-- 序列: {seq_name}")
                    
                    try:
                        # 简化序列备份：只备份当前值，不尝试重建完整序列定义
                        f.write(f"\n-- 序列当前值: {seq_name}\n")
                        
                        # 设置序列当前值
                        cursor.execute(f"SELECT last_value FROM {seq_name}")
                        last_val = cursor.fetchone()[0]
                        f.write(f"SELECT setval('{seq_name}', {last_val}, true);\n\n")
                    except Exception as e:
                        print(f"  备份序列 {seq_name} 失败: {e}")
                        f.write(f"-- 备份序列 {seq_name} 失败\n\n")
            
            # 第二步：备份所有表结构和数据
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE'")
            tables = cursor.fetchall()
            
            for table in tables:
                table_name = table[0]
                print(f"备份表: {table_name}")
                
                # 备份表结构
                f.write(f"-- 表结构: {table_name}\n")
                
                # 处理保留关键字表名
                quoted_table_name = f'"{table_name}"' if table_name.lower() in ['user', 'order', 'group', 'select', 'insert', 'update', 'delete'] else table_name
                
                f.write(f"CREATE TABLE {quoted_table_name} (\n")
                
                # 获取表列信息
                cursor.execute("""
                    SELECT column_name, data_type, character_maximum_length, column_default, is_nullable 
                    FROM information_schema.columns 
                    WHERE table_schema = 'public' AND table_name = %s ORDER BY ordinal_position
                """, (table_name,))
                columns = cursor.fetchall()
                
                column_definitions = []
                for col in columns:
                    col_name, data_type, max_length, default, is_nullable = col
                    col_def = f"    {col_name} {data_type}"
                    
                    if max_length is not None:
                        col_def += f"({max_length})"
                    
                    if default is not None:
                        col_def += f" DEFAULT {default}"
                    
                    if is_nullable == 'NO':
                        col_def += " NOT NULL"
                    
                    column_definitions.append(col_def)
                
                # 添加主键约束
                cursor.execute("""
                    SELECT constraint_name, column_name 
                    FROM information_schema.key_column_usage 
                    WHERE table_schema = 'public' AND table_name = %s AND constraint_name LIKE '%%_pkey'
                """, (table_name,))
                primary_keys = cursor.fetchall()
                if primary_keys:
                    pkey_cols = [pk[1] for pk in primary_keys]
                    column_definitions.append(f"    PRIMARY KEY ({', '.join(pkey_cols)})")
                
                f.write(",\n".join(column_definitions))
                f.write("\n);\n\n")
                
                # 备份表数据
                cursor.execute(f"SELECT * FROM {quoted_table_name}")
                rows = cursor.fetchall()
                
                if rows:
                    f.write(f"-- 表数据: {table_name}\n")
                    column_names = [desc[0] for desc in cursor.description]
                    
                    for row in rows:
                        # 处理特殊字符
                        values = []
                        for value in row:
                            if value is None:
                                values.append('NULL')
                            elif isinstance(value, str):
                                # 转义单引号
                                values.append(f"'{value.replace("'", "''")}'")
                            elif isinstance(value, datetime):
                                values.append(f"'{value}'")
                            elif isinstance(value, list):
                                # 处理列表/数组类型，转换为JSON格式
                                import json
                                json_str = json.dumps(value)
                                values.append(f"'{json_str.replace("'", "''")}'")
                            else:
                                values.append(str(value))
                        
                        insert_sql = f"INSERT INTO {quoted_table_name} ({', '.join(column_names)}) VALUES ({', '.join(values)});\n"
                        f.write(insert_sql)
                    f.write("\n")
        
        print(f"数据库备份完成: {backup_file}")
        
    except Exception as e:
        print(f"备份数据库失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()

def restore_database(backup_file):
    """
    恢复数据库
    """
    print(f"开始从 {backup_file} 恢复数据库...")
    
    # 使用psycopg2执行psql命令
    result = os.system(f"psql -h localhost -p 5432 -U postgres -d gradpush -f {backup_file} --password")
    
    if result != 0:
        raise Exception(f"psql命令执行失败，退出码: {result}")
    
    print(f"数据库恢复完成")

def restore_database_python(backup_file):
    """
    使用Python代码恢复数据库（备选方案，当psql不可用时）
    """
    print(f"开始使用Python从 {backup_file} 恢复数据库...")
    
    conn = get_db_connection()
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    try:
        # 第一步：从备份文件中提取所有引用的序列
        print("提取备份文件中的序列信息...")
        
        # 以二进制模式读取文件，然后使用errors='replace'忽略无法解码的字符
        with open(backup_file, 'rb') as f:
            binary_content = f.read()
        
        # 使用utf-8解码，忽略无法解码的字符
        content = binary_content.decode('utf-8', errors='replace')
        print("成功使用utf-8编码（忽略错误）读取备份文件")
        
        # 查找所有引用的序列：nextval('sequence_name'::regclass)
        import re
        sequence_pattern = r"nextval\('([^']+)\'::regclass"
        sequences = set(re.findall(sequence_pattern, content))
        
        print(f"备份文件中引用的序列: {', '.join(sequences)}")
        
        # 第二步：创建所有序列
        if sequences:
            print("创建必要的序列...")
            for seq in sequences:
                try:
                    # 尝试创建序列
                    cursor.execute(f"CREATE SEQUENCE {seq} START 1;")
                    print(f"  创建序列 {seq} 成功")
                except Exception as e:
                    # 如果序列已存在，忽略错误
                    if "already exists" in str(e):
                        print(f"  序列 {seq} 已存在")
                    else:
                        print(f"  创建序列 {seq} 失败: {e}")
        
        # 第三步：提取表名（已经有content变量，无需再次读取文件）
        print("提取备份文件中的表信息...")
        table_names = []
        current_table = None
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('CREATE TABLE'):
                # 提取表名
                parts = line.split()
                if len(parts) >= 3:
                    table_name = parts[2]
                    # 处理可能的引号
                    if table_name.startswith('"') and table_name.endswith('"'):
                        table_name = table_name[1:-1]
                    table_names.append(table_name)
        
        print(f"备份文件中包含的表: {', '.join(table_names)}")
        
        # 第四步：获取当前数据库中的所有表
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        # 第五步：删除需要恢复的表（注意：这里没有处理外键约束，实际使用时需要更复杂的处理）
        tables_to_drop = [table for table in existing_tables if table in table_names]
        if tables_to_drop:
            print(f"删除现有表以准备恢复: {', '.join(tables_to_drop)}")
            
            # 首先禁用外键约束
            cursor.execute("SET session_replication_role = 'replica'")
            
            # 删除表（逆序删除，避免外键约束问题）
            for table in reversed(tables_to_drop):
                try:
                    # 处理保留关键字，如表名是user等
                    quoted_table = f'"{table}"' if table.lower() in ['user', 'order', 'group', 'select', 'insert', 'update', 'delete'] else table
                    cursor.execute(f"DROP TABLE IF EXISTS {quoted_table} CASCADE")
                    print(f"已删除表: {table}")
                except Exception as e:
                    print(f"删除表 {table} 失败: {e}")
            
            # 重置序列（处理自动递增的ID）
            cursor.execute("SELECT sequence_name FROM information_schema.sequences WHERE sequence_schema = 'public'")
            sequences = [row[0] for row in cursor.fetchall()]
            for seq in sequences:
                try:
                    cursor.execute(f"DROP SEQUENCE IF EXISTS {seq} CASCADE")
                    print(f"已删除序列: {seq}")
                except Exception as e:
                    print(f"删除序列 {seq} 失败: {e}")
            
            # 重新启用外键约束
            cursor.execute("SET session_replication_role = 'origin'")
        
        # 第六步：创建所有需要的序列
        print("创建序列...")
        sequences_to_create = [
            "system_settings_id_seq",
            "user_id_seq",
            "faculty_id_seq",
            "department_id_seq",
            "major_id_seq",
            "class_id_seq",
            "student_id_seq",
            "teacher_id_seq",
            "graduate_file_id_seq",
            "rule_id_seq"
        ]
        
        for seq in sequences_to_create:
            try:
                cursor.execute(f"CREATE SEQUENCE IF NOT EXISTS {seq} START WITH 1 INCREMENT BY 1")
                print(f"已创建序列: {seq}")
            except Exception as e:
                print(f"创建序列 {seq} 失败: {e}")
        
        # 第七步：执行备份文件中的SQL命令（已经有content变量，无需再次读取文件）
        print("执行备份文件中的SQL命令...")
        sql_content = content
        
        # 处理保留关键字：将CREATE TABLE user替换为CREATE TABLE "user"
        sql_content = sql_content.replace('CREATE TABLE user', 'CREATE TABLE "user"')
        sql_content = sql_content.replace('INSERT INTO user', 'INSERT INTO "user"')
        
        # 执行整个SQL内容
        try:
            cursor.execute(sql_content)
            print("备份文件中的SQL命令执行完成")
        except Exception as e:
            print(f"执行SQL命令失败: {e}")
            print(f"尝试分段执行...")
            
            # 如果整个执行失败，尝试按分号分割并逐个执行
            import re
            # 正则表达式分割SQL命令，忽略字符串和注释中的分号
            sql_commands = re.split(r';(?=(?:[^"\']*["\'][^"\']*["\'])*[^"\']*$)', sql_content)
            
            # 执行所有SQL命令
            command_count = 0
            for command in sql_commands:
                command = command.strip()
                if not command or command.startswith('--'):
                    continue
                
                command_count += 1
                try:
                    cursor.execute(command)
                    if command_count % 10 == 0:  # 每执行10条命令显示进度
                        print(f"已执行 {command_count} 条命令")
                except Exception as e:
                    print(f"执行SQL命令失败 (第{command_count}条): {e}")
                    print(f"失败的命令: {command[:200]}...")
                    raise
        
        print(f"数据库恢复完成")
        
    except Exception as e:
        print(f"恢复数据库失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        cursor.close()
        conn.close()
    
    return True

def main():
    parser = argparse.ArgumentParser(description='数据库备份与恢复工具')
    parser.add_argument('action', choices=['backup', 'restore'], help='操作类型: backup(备份) 或 restore(恢复)')
    parser.add_argument('file', help='备份文件路径')
    parser.add_argument('--python-only', action='store_true', help='仅使用Python代码执行备份/恢复，不依赖pg_dump/psql命令')
    
    args = parser.parse_args()
    
    if args.action == 'backup':
        if args.python_only:
            backup_database_python(args.file)
        else:
            try:
                backup_database(args.file)
            except Exception as e:
                print(f"使用pg_dump备份失败，尝试使用Python代码备份: {e}")
                backup_database_python(args.file)
    elif args.action == 'restore':
        if args.python_only:
            restore_database_python(args.file)
        else:
            try:
                restore_database(args.file)
            except Exception as e:
                print(f"使用psql恢复失败，尝试使用Python代码恢复: {e}")
                restore_database_python(args.file)

if __name__ == '__main__':
    main()

