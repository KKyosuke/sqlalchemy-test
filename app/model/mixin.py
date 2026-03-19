from sqlalchemy import Column, Integer, event, inspect

session_company_id = 1  # これは例として固定値を使用しています。実際にはセッションから取得する必要があります。

class CompanyMixin:
    company_id = Column(Integer, nullable=False)

    __mapper_args__ = {
        "version_id_col": company_id,
        "version_id_generator": False
    }

@event.listens_for(CompanyMixin, 'before_insert', propagate=True)
def receive_before_insert(mapper, connection, target):
    if target.company_id is None:
        raise ValueError("company_id is required")

    if target.company_id != session_company_id:
        raise ValueError("company_id does not match the session company_id")

    print(f"Before insert: {target}")

@event.listens_for(CompanyMixin, 'before_update', propagate=True)
def receive_before_update(mapper, connection, target):
    state = inspect(target)
    
    # 1. company_idが更新されそう
    history = state.attrs.company_id.history
    if history.has_changes():
        raise ValueError("Updating company_id is not allowed")

    if target.company_id != session_company_id:
        raise ValueError("company_id does not match the session company_id")
    
    print(f"Before update: {target}")

@event.listens_for(CompanyMixin, 'before_delete', propagate=True)
def receive_before_delete(mapper, connection, target):
    if target.company_id != session_company_id:
        raise ValueError("company_id does not match the session company_id")

    print(f"Before delete: {target}")
