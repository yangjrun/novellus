#!/usr/bin/env python3
"""
数据库初始化脚本
用于创建和初始化 Novellus 项目的 PostgreSQL 数据库
"""

import asyncio
import asyncpg
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
import sys
from pathlib import Path
from typing import Optional

from config import config


class DatabaseInitializer:
    """数据库初始化器"""

    def __init__(self):
        self.config = config

    def create_database_if_not_exists(self) -> bool:
        """创建数据库（如果不存在）"""
        try:
            # 连接到 postgres 默认数据库
            conn = psycopg2.connect(
                host=self.config.postgres_host,
                port=self.config.postgres_port,
                user=self.config.postgres_user,
                password=self.config.postgres_password,
                database='postgres'
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()

            # 检查数据库是否存在
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (self.config.postgres_db,)
            )
            exists = cursor.fetchone()

            if not exists:
                print(f"创建数据库: {self.config.postgres_db}")
                cursor.execute(f'CREATE DATABASE "{self.config.postgres_db}"')
                print("数据库创建成功")
                return True
            else:
                print(f"数据库 {self.config.postgres_db} 已存在")
                return False

        except Exception as e:
            print(f"创建数据库时出错: {e}")
            return False
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def get_sql_files(self, include_default_data: bool = True) -> list[Path]:
        """获取需要执行的 SQL 文件列表，按依赖关系排序

        Args:
            include_default_data: 是否包含默认数据文件
        """
        schemas_dir = Path(__file__).parent / "database" / "schemas"

        # 按依赖关系和逻辑顺序执行 SQL 文件
        # 注意：严格按照依赖关系排序，基础表结构必须先创建
        sql_files = [
            "init_postgresql.sql",              # 1. 核心表结构和函数/触发器
            "cultural_framework_tables.sql",   # 2. 文化框架扩展表
            "geographic_entity_types.sql",     # 3. 地理实体类型定义
            "character_management_tables.sql", # 4. 角色管理相关表
            "plot_function_mapping_tables.sql", # 5. 剧情功能映射表
            "cross_domain_conflicts_init.sql", # 6. 跨域冲突处理表
        ]

        # 可选的默认数据文件
        if include_default_data:
            sql_files.append("default_data.sql")  # 7. 默认数据和系统配置（最后执行）

        existing_files = []
        for filename in sql_files:
            file_path = schemas_dir / filename
            if file_path.exists():
                existing_files.append(file_path)
            else:
                print(f"警告: SQL 文件不存在: {file_path}")

        return existing_files

    async def execute_sql_file(self, file_path: Path) -> bool:
        """执行单个 SQL 文件

        Args:
            file_path: SQL 文件路径

        Returns:
            bool: 执行成功返回 True，失败返回 False
        """
        try:
            print(f"执行 SQL 文件: {file_path.name}")

            # 读取 SQL 文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()

            # 过滤掉注释和空行，但保留完整的 SQL 语句
            if not sql_content.strip():
                print(f"警告: {file_path.name} 文件为空")
                return True

            # 连接数据库
            conn = await asyncpg.connect(
                host=self.config.postgres_host,
                port=self.config.postgres_port,
                user=self.config.postgres_user,
                password=self.config.postgres_password,
                database=self.config.postgres_db
            )

            try:
                # 执行 SQL 内容
                # 使用事务确保原子性
                async with conn.transaction():
                    await conn.execute(sql_content)
                print(f"✓ {file_path.name} 执行成功")
                return True

            except Exception as e:
                print(f"✗ {file_path.name} 执行失败: {e}")

                # 尝试分析错误位置
                if 'syntax error' in str(e).lower():
                    print(f"详细错误信息: {e}")
                    print("正在分析 SQL 语句...")

                    # 将 SQL 内容按语句分割进行逐一测试
                    sql_statements = []
                    current_statement = ""

                    for line_num, line in enumerate(sql_content.split('\n'), 1):
                        line = line.strip()
                        if not line or line.startswith('--'):
                            continue

                        current_statement += line + '\n'

                        # 检查是否是语句结束（简单判断）
                        if line.endswith(';') or 'END;' in line or 'END $$' in line:
                            if current_statement.strip():
                                sql_statements.append((line_num, current_statement.strip()))
                            current_statement = ""

                    # 如果还有未完成的语句
                    if current_statement.strip():
                        sql_statements.append((len(sql_content.split('\n')), current_statement.strip()))

                    print(f"共找到 {len(sql_statements)} 个 SQL 语句，正在逐一测试...")

                    # 逐个测试语句
                    async with conn.transaction():
                        for stmt_num, (line_num, stmt) in enumerate(sql_statements, 1):
                            try:
                                await conn.execute(stmt)
                            except Exception as stmt_error:
                                print(f"第 {stmt_num} 个语句（第 {line_num} 行附近）执行失败:")
                                print(f"错误: {stmt_error}")
                                print(f"语句内容（前200字符）: {stmt[:200]}...")
                                break

                return False

            finally:
                await conn.close()

        except Exception as e:
            print(f"处理文件 {file_path.name} 时出错: {e}")
            return False

    async def check_database_status(self) -> dict:
        """检查数据库连接状态和基本信息

        Returns:
            dict: 包含数据库状态信息的字典
        """
        try:
            conn = await asyncpg.connect(
                host=self.config.postgres_host,
                port=self.config.postgres_port,
                user=self.config.postgres_user,
                password=self.config.postgres_password,
                database=self.config.postgres_db
            )

            try:
                # 检查数据库中的表数量
                tables_count = await conn.fetchval("""
                    SELECT COUNT(*)
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                """)

                # 检查核心表是否存在及其数据量
                novels_count = 0
                try:
                    novels_count = await conn.fetchval("SELECT COUNT(*) FROM novels")
                except:
                    pass  # 表可能还不存在

                # 检查必要的 PostgreSQL 扩展是否已安装
                extensions = await conn.fetch("""
                    SELECT extname FROM pg_extension
                    WHERE extname IN ('uuid-ossp')
                """)

                return {
                    'tables_count': tables_count,
                    'novels_count': novels_count,
                    'extensions': [ext['extname'] for ext in extensions],
                    'status': 'connected'
                }

            finally:
                await conn.close()

        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    async def drop_all_tables(self) -> bool:
        """删除数据库中的所有表和对象

        Returns:
            bool: 删除成功返回 True
        """
        try:
            conn = await asyncpg.connect(
                host=self.config.postgres_host,
                port=self.config.postgres_port,
                user=self.config.postgres_user,
                password=self.config.postgres_password,
                database=self.config.postgres_db
            )

            try:
                print("  正在删除所有表和对象...")

                # 第一步：删除所有视图（依赖于表）
                print("    删除视图...")
                views = await conn.fetch("""
                    SELECT viewname
                    FROM pg_views
                    WHERE schemaname = 'public'
                """)

                for view in views:
                    view_name = view['viewname']
                    try:
                        await conn.execute(f'DROP VIEW IF EXISTS "{view_name}" CASCADE')
                        print(f"    ✓ 删除视图: {view_name}")
                    except Exception as e:
                        print(f"    ⚠ 删除视图 {view_name} 时出现警告: {e}")

                if not views:
                    print("    没有找到需要删除的视图")

                # 第二步：删除所有触发器（依赖于函数和表）
                print("    删除触发器...")
                try:
                    await conn.execute("""
                        DO $$
                        DECLARE
                            r RECORD;
                            trigger_count INTEGER := 0;
                        BEGIN
                            FOR r IN (
                                SELECT n.nspname as schemaname, c.relname as tablename, t.tgname as triggername
                                FROM pg_trigger t
                                JOIN pg_class c ON t.tgrelid = c.oid
                                JOIN pg_namespace n ON c.relnamespace = n.oid
                                WHERE n.nspname = 'public' AND NOT t.tgisinternal
                            )
                            LOOP
                                BEGIN
                                    EXECUTE 'DROP TRIGGER IF EXISTS ' || quote_ident(r.triggername) ||
                                           ' ON ' || quote_ident(r.schemaname) || '.' || quote_ident(r.tablename) || ' CASCADE';
                                    trigger_count := trigger_count + 1;
                                EXCEPTION WHEN OTHERS THEN
                                    RAISE NOTICE '删除触发器 % 时出现警告: %', r.triggername, SQLERRM;
                                END;
                            END LOOP;
                            RAISE NOTICE '删除了 % 个触发器', trigger_count;
                        END $$;
                    """)
                    print("    ✓ 触发器删除完成")
                except Exception as e:
                    print(f"    ⚠ 删除触发器时出现警告: {e}")

                # 第三步：删除所有函数
                print("    删除函数...")
                try:
                    await conn.execute("""
                        DO $$
                        DECLARE
                            r RECORD;
                            function_count INTEGER := 0;
                        BEGIN
                            FOR r IN (
                                SELECT p.proname, n.nspname
                                FROM pg_proc p
                                JOIN pg_namespace n ON p.pronamespace = n.oid
                                WHERE n.nspname = 'public'
                            )
                            LOOP
                                BEGIN
                                    EXECUTE 'DROP FUNCTION IF EXISTS ' || quote_ident(r.nspname) || '.' || quote_ident(r.proname) || ' CASCADE';
                                    function_count := function_count + 1;
                                EXCEPTION WHEN OTHERS THEN
                                    RAISE NOTICE '删除函数 % 时出现警告: %', r.proname, SQLERRM;
                                END;
                            END LOOP;
                            RAISE NOTICE '删除了 % 个函数', function_count;
                        END $$;
                    """)
                    print("    ✓ 函数删除完成")
                except Exception as e:
                    print(f"    ⚠ 删除函数时出现警告: {e}")

                # 第四步：删除所有表（使用 CASCADE 处理外键依赖）
                print("    删除表...")
                tables = await conn.fetch("""
                    SELECT tablename
                    FROM pg_tables
                    WHERE schemaname = 'public'
                    AND tablename NOT LIKE 'pg_%'
                    AND tablename NOT LIKE 'sql_%'
                """)

                for table in tables:
                    table_name = table['tablename']
                    try:
                        await conn.execute(f'DROP TABLE IF EXISTS "{table_name}" CASCADE')
                        print(f"    ✓ 删除表: {table_name}")
                    except Exception as e:
                        print(f"    ⚠ 删除表 {table_name} 时出现警告: {e}")

                if not tables:
                    print("    没有找到需要删除的表")

                # 第五步：删除所有序列
                print("    删除序列...")
                sequences = await conn.fetch("""
                    SELECT sequencename
                    FROM pg_sequences
                    WHERE schemaname = 'public'
                """)

                for sequence in sequences:
                    sequence_name = sequence['sequencename']
                    try:
                        await conn.execute(f'DROP SEQUENCE IF EXISTS "{sequence_name}" CASCADE')
                        print(f"    ✓ 删除序列: {sequence_name}")
                    except Exception as e:
                        print(f"    ⚠ 删除序列 {sequence_name} 时出现警告: {e}")

                if not sequences:
                    print("    没有找到需要删除的序列")

                # 第六步：删除所有自定义类型
                print("    删除自定义类型...")
                try:
                    await conn.execute("""
                        DO $$
                        DECLARE
                            r RECORD;
                            type_count INTEGER := 0;
                        BEGIN
                            FOR r IN (
                                SELECT typname
                                FROM pg_type
                                WHERE typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
                                AND typtype = 'e'
                            )
                            LOOP
                                BEGIN
                                    EXECUTE 'DROP TYPE IF EXISTS ' || quote_ident(r.typname) || ' CASCADE';
                                    type_count := type_count + 1;
                                EXCEPTION WHEN OTHERS THEN
                                    RAISE NOTICE '删除类型 % 时出现警告: %', r.typname, SQLERRM;
                                END;
                            END LOOP;
                            RAISE NOTICE '删除了 % 个自定义类型', type_count;
                        END $$;
                    """)
                    print("    ✓ 自定义类型删除完成")
                except Exception as e:
                    print(f"    ⚠ 删除自定义类型时出现警告: {e}")

                print("  ✓ 所有表和对象删除完成")
                return True

            finally:
                await conn.close()

        except Exception as e:
            print(f"  ✗ 删除表和对象时出错: {e}")
            return False

    async def initialize_database(self, force_recreate: bool = False, include_default_data: bool = True) -> bool:
        """执行数据库完整初始化流程

        Args:
            force_recreate: 是否强制重新创建（会删除现有数据）
            include_default_data: 是否包含默认数据和模板

        Returns:
            bool: 初始化成功返回 True
        """
        print("=" * 60)
        print("开始数据库初始化")
        print("=" * 60)

        # 第一步：检查数据库连接和当前状态
        print("1. 检查数据库连接...")
        status = await self.check_database_status()

        if status.get('status') == 'error':
            print(f"数据库连接失败: {status.get('error')}")

            # 第二步：如果连接失败，尝试创建数据库
            print("2. 尝试创建数据库...")
            if not self.create_database_if_not_exists():
                print("创建数据库失败")
                return False

            # 重新检查数据库连接
            status = await self.check_database_status()
            if status.get('status') == 'error':
                print(f"创建数据库后仍无法连接: {status.get('error')}")
                return False

        print(f"✓ 数据库连接成功")
        print(f"  - 当前表数量: {status.get('tables_count', 0)}")
        print(f"  - 小说记录数: {status.get('novels_count', 0)}")
        print(f"  - 已安装扩展: {', '.join(status.get('extensions', []))}")

        # 第三步：处理强制重建逻辑
        if force_recreate and status.get('tables_count', 0) > 0:
            print("\n" + "!" * 60)
            print("⚠️  强制重建模式警告")
            print("!" * 60)
            print(f"即将删除数据库 '{self.config.postgres_db}' 中的所有内容：")
            print(f"  - {status.get('tables_count', 0)} 个表")
            print(f"  - {status.get('novels_count', 0)} 条小说记录")
            print("  - 所有视图、函数、序列和触发器")
            print("\n此操作不可逆转！所有数据将永久丢失！")
            print("!" * 60)

            # 在非交互环境中跳过确认（用于自动化脚本）
            import sys
            if sys.stdin.isatty():
                confirm = input("\n确认要继续吗？请输入 'YES' 确认删除所有数据: ")
                if confirm != 'YES':
                    print("操作已取消")
                    return False
            else:
                print("检测到非交互环境，跳过确认步骤")

            print("\n2. 清理现有数据库结构...")

            # 删除所有表和对象
            if not await self.drop_all_tables():
                print("✗ 清理数据库失败")
                return False

            print("✓ 数据库清理完成")

        # 第四步：判断是否需要执行初始化
        elif status.get('tables_count', 0) > 0 and not force_recreate:
            print("\n数据库已存在表结构，跳过初始化")
            print("如需重新初始化，请使用 --force 参数")
            return True

        # 第五步：准备要执行的 SQL 文件
        print("\n3. 准备 SQL 文件...")
        sql_files = self.get_sql_files(include_default_data=include_default_data)

        if not sql_files:
            print("未找到 SQL 文件")
            return False

        print(f"找到 {len(sql_files)} 个 SQL 文件")

        # 第六步：按顺序执行所有 SQL 文件
        print("\n4. 执行 SQL 文件...")
        success_count = 0

        for sql_file in sql_files:
            if await self.execute_sql_file(sql_file):
                success_count += 1
            else:
                print(f"停止执行，因为 {sql_file.name} 失败")
                print("建议检查 SQL 语法或数据库权限")
                return False

        print(f"\n✓ 成功执行 {success_count}/{len(sql_files)} 个 SQL 文件")

        # 第七步：验证初始化结果
        print("\n5. 验证初始化结果...")
        final_status = await self.check_database_status()
        print(f"  - 最终表数量: {final_status.get('tables_count', 0)}")
        print(f"  - 小说模板数: {final_status.get('novels_count', 0)}")

        print("\n" + "=" * 60)
        print("数据库初始化完成！")
        print("=" * 60)

        return True


async def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='Novellus 数据库初始化工具')
    parser.add_argument(
        '--force',
        action='store_true',
        help='强制重新创建数据库结构（⚠️ 警告：会删除所有现有数据和表结构）'
    )
    parser.add_argument(
        '--check-only',
        action='store_true',
        help='仅检查数据库状态，不执行初始化'
    )
    parser.add_argument(
        '--no-default-data',
        action='store_true',
        help='不加载默认数据和模板（仅创建表结构）'
    )

    args = parser.parse_args()

    initializer = DatabaseInitializer()

    if args.check_only:
        print("检查数据库状态...")
        status = await initializer.check_database_status()

        if status.get('status') == 'error':
            print(f"数据库连接失败: {status.get('error')}")
            sys.exit(1)
        else:
            print("数据库状态:")
            print(f"  - 表数量: {status.get('tables_count', 0)}")
            print(f"  - 记录数: {status.get('novels_count', 0)}")
            print(f"  - 扩展: {', '.join(status.get('extensions', []))}")
            sys.exit(0)

    # 执行初始化
    success = await initializer.initialize_database(
        force_recreate=args.force,
        include_default_data=not args.no_default_data
    )

    if success:
        print("\n🎉 数据库初始化成功！")
        print("\n接下来您可以:")
        print("1. 运行 MCP 服务器: python mcp_server.py")
        print("2. 开始创建小说项目")
        print("3. 导入测试数据")

        if args.force:
            print("\n📝 注意：由于使用了 --force 参数，所有原有数据已被清除")

        sys.exit(0)
    else:
        print("\n❌ 数据库初始化失败！")
        print("\n请检查:")
        print("1. 数据库服务是否运行")
        print("2. 连接配置是否正确（.env文件）")
        print("3. 数据库权限是否充足")
        print("4. SQL 文件是否存在且语法正确")

        if args.force:
            print("5. 强制删除过程中是否出现错误")

        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())