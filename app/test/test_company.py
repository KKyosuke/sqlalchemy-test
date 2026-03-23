import sqlglot
from sqlglot import exp
from typing import List, Set

def validate_company_id(sql: str, table_names: List[str], company_id: str) -> None:
    """
    SQLの種類（INSERT/SELECT/UPDATE/DELETE）に応じて、適切なcompany_idバリデーションを実行するエントリポイント。
    不正な場合は ValueError を投げる。対象外のSQLやテーブルの場合は何もしない。
    """
    try:
        parsed = sqlglot.parse_one(sql)
    except Exception as e:
        raise ValueError(f"SQLの解析に失敗しました: {e}") from e

    normalized_tables = {t.lower() for t in table_names}

    if isinstance(parsed, exp.Insert):
        _validate_insert(parsed, normalized_tables, company_id)
    elif isinstance(parsed, (exp.Select, exp.Update, exp.Delete)):
        _validate_where_clause(parsed, normalized_tables, company_id)

def _validate_insert(parsed: exp.Insert, table_names: Set[str], company_id: str) -> None:
    """INSERT文のバリデーションロジック"""
    table = parsed.find(exp.Table)
    if not table or table.name.lower() not in table_names:
        return

    table_name = table.name.lower()
    
    # カラム名の取得
    schema = parsed.find(exp.Schema)
    if not schema:
        # test_where_company.py の実装に合わせ、スキーマなし（カラム指定なし）はエラーとする
        raise ValueError(f"Table '{table_name}' への INSERT にカラム指定がありません。")

    columns = [c.name.lower() for c in schema.find_all(exp.Identifier)]
    
    if 'company_id' not in columns:
        raise ValueError(f"Table '{table_name}' への INSERT に 'company_id' が含まれていません。")

    company_id_index = columns.index('company_id')

    # VALUES 句のチェック
    values_list = list(parsed.find_all(exp.Values))
    if values_list:
        for values in values_list:
            for tuple_exp in values.find_all(exp.Tuple):
                expressions = tuple_exp.expressions
                if len(expressions) > company_id_index:
                    val = expressions[company_id_index]
                    _compare_value(val, company_id, "company_id")
                else:
                    raise ValueError("VALUES の値の数がカラム数と一致しません。")
        return

    # INSERT INTO ... SELECT ... のチェック
    select_exp = parsed.find(exp.Select)
    if select_exp:
        projections = select_exp.expressions
        if len(projections) > company_id_index:
            target_projection = projections[company_id_index]
            # Alias の場合は中身をチェック
            if isinstance(target_projection, exp.Alias):
                target_projection = target_projection.this
            
            _compare_value(target_projection, company_id, "SELECT句の company_id")
        else:
            raise ValueError("SELECT 句のカラム数が INSERT のカラム数と一致しません。")

def _validate_where_clause(parsed: exp.Expression, table_names: Set[str], company_id: str) -> None:
    """SELECT/UPDATE/DELETE文のWHERE句バリデーションロジック"""
    # 使用されている対象テーブルとそのエイリアスを特定
    table_aliases = {}
    for table in parsed.find_all(exp.Table):
        t_name = table.name.lower()
        if t_name in table_names:
            alias = table.alias
            table_aliases[alias.lower() if alias else t_name] = t_name

    if not table_aliases:
        return

    where_clause = parsed.find(exp.Where)
    if not where_clause:
        raise ValueError(f"WHERE 句が見つかりません。対象テーブル: {', '.join(table_aliases.values())}")

    found_tables = {}
    
    for eq in where_clause.find_all(exp.EQ):
        left, right = eq.left, eq.right
        column = None
        value_node = None
        
        if isinstance(left, exp.Column) and left.name.lower() == 'company_id':
            column, value_node = left, right
        elif isinstance(right, exp.Column) and right.name.lower() == 'company_id':
            column, value_node = right, left
            
        if column and value_node:
            _compare_value(value_node, company_id, "company_id")
            actual_value = str(value_node.this) if isinstance(value_node, exp.Literal) else str(value_node)

            col_table = column.table.lower() if column.table else None
            if col_table:
                if col_table in table_aliases:
                    found_tables[table_aliases[col_table]] = actual_value
            else:
                # テーブル指定がない場合は全対象テーブルに適用
                for t_name in table_aliases.values():
                    found_tables[t_name] = actual_value

    used_target_tables = set(table_aliases.values())
    missing_tables = used_target_tables - set(found_tables.keys())
    
    if missing_tables:
        raise ValueError(f"以下のテーブルに対して company_id の条件が WHERE 句にありません: {', '.join(missing_tables)}")

def _compare_value(node: exp.Expression, expected: str, label: str) -> None:
    """値の比較。不一致なら ValueError"""
    actual = str(node.this) if isinstance(node, exp.Literal) else str(node)
    if actual != str(expected):
        raise ValueError(f"{label} が一致しません。期待値: {expected}, 実際の値: {actual}")

def test_validate_company_id():
    table_names = ["users", "tasks"]
    company_id = "1"

    print("Testing validate_company_id...")

    # --- INSERT Tests ---
    # 正常系
    validate_company_id("INSERT INTO users (name, company_id) VALUES ('Alice', 1)", table_names, company_id)
    validate_company_id("INSERT INTO users (name, company_id) SELECT name, 1 FROM old_users", table_names, company_id)
    
    # 異常系 (company_id 不一致)
    try:
        validate_company_id("INSERT INTO users (name, company_id) VALUES ('Bob', 2)", table_names, company_id)
        assert False, "Should fail for wrong company_id"
    except ValueError as e:
        print(f"OK: {e}")

    # 異常系 (company_id 欠落)
    try:
        validate_company_id("INSERT INTO users (name) VALUES ('Charlie')", table_names, company_id)
        assert False, "Should fail for missing company_id"
    except ValueError as e:
        print(f"OK: {e}")

    # --- WHERE Clause Tests (SELECT/UPDATE/DELETE) ---
    # 正常系
    validate_company_id("SELECT * FROM users WHERE company_id = 1", table_names, company_id)
    validate_company_id("UPDATE tasks SET status = 'done' WHERE company_id = 1", table_names, company_id)
    validate_company_id("DELETE FROM users WHERE company_id = 1", table_names, company_id)

    # 複数テーブル正常系
    validate_company_id("SELECT * FROM users u JOIN tasks t ON u.id = t.user_id WHERE u.company_id = 1 AND t.company_id = 1", table_names, company_id)

    # 異常系 (WHEREなし)
    try:
        validate_company_id("SELECT * FROM users", table_names, company_id)
        assert False, "Should fail for missing WHERE"
    except ValueError as e:
        print(f"OK: {e}")

    # 異常系 (値不一致)
    try:
        validate_company_id("SELECT * FROM users WHERE company_id = 999", table_names, company_id)
        assert False, "Should fail for value mismatch"
    except ValueError as e:
        print(f"OK: {e}")

    # 異常系 (一部テーブルのみWHEREあり)
    try:
        validate_company_id("SELECT * FROM users u JOIN tasks t ON u.id = t.user_id WHERE u.company_id = 1", table_names, company_id)
        assert False, "Should fail for missing condition on 'tasks'"
    except ValueError as e:
        print(f"OK: {e}")

    # 対象外テーブル
    validate_company_id("SELECT * FROM logs", table_names, company_id)

    print("All tests passed!")

if __name__ == "__main__":
    test_validate_company_id()
