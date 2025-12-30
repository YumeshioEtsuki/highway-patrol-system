from pathlib import Path
from utils.utils import execute_sql_file

if __name__ == "__main__":
    sql_path = Path(__file__).resolve().parent.parent / "3-数据�? / "add_indexes.sql"
    print(f"Applying indexes from: {sql_path}")
    ok = execute_sql_file(str(sql_path), skip_read_only_queries=True, print_query_results=False, stop_on_error=False)
    print("�?索引脚本执行完成" if ok else "⚠️ 索引脚本执行部分失败，请检查日�?)

