from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import sqlglot
from sqlglot import exp

# Database connection URL
# Use 'db' as the host as specified in compose.yaml
DATABASE_URL = "mysql://user:password@db:3306/test_db"

engine = create_engine(DATABASE_URL)

@event.listens_for(engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    import re
    from datetime import datetime, date

    def escape_param(p):
        if isinstance(p, str):
            # Escape single quotes in string
            escaped_str = p.replace("'", "''")
            return f"'{escaped_str}'"
        if isinstance(p, (datetime, date)):
            return f"'{p.isoformat()}'"
        if p is None:
            return "NULL"
        return str(p)

    if parameters:
        if isinstance(parameters, (list, tuple)):
            # Handle positional parameters (%s)
            parts = re.split(r'(%s)', statement)
            new_statement = ""
            param_idx = 0
            for part in parts:
                if part == '%s' and param_idx < len(parameters):
                    new_statement += escape_param(parameters[param_idx])
                    param_idx += 1
                else:
                    new_statement += part
            statement = new_statement
        elif isinstance(parameters, dict):
            # Handle named parameters (%(name)s)
            # Sort keys by length descending to avoid partial replacement issues if names are similar
            for key in sorted(parameters.keys(), key=len, reverse=True):
                value = parameters[key]
                pattern = r'%\(' + re.escape(key) + r'\)s'
                statement = re.sub(pattern, escape_param(value), statement)

    parsed = sqlglot.parse_one(statement)
    tables = [table.name for table in parsed.find_all(exp.Table)]
    print("tables:", tables)

    has_company_id = False

    where = parsed.find(exp.Where)
    if where:
        for column in where.find_all(exp.Column):
            if column.name == "company_id":
                has_company_id = True

    print("has_company_id:", has_company_id)

    print(f"Executing statement: {statement}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
