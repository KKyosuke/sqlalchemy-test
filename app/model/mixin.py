from sqlalchemy import Column, Integer, event, inspect
from sqlalchemy.orm import Session, with_loader_criteria
from sqlalchemy.sql import visitors
from sqlalchemy.sql.elements import BinaryExpression

def get_current_company_id():
    session_company_id = 1  # これは例として固定値を使用しています。実際にはセッションから取得する必要があります。
    return session_company_id

class CompanyMixin:
    company_id = Column(Integer, nullable=False)

    __mapper_args__ = {
        "version_id_col": company_id,
        "version_id_generator": False
    }

@event.listens_for(Session, "do_orm_execute")
def _add_filtering_criteria(execute_state):
    """
    Select時に自動的にcompany_idでフィルタリングを行うためのイベントリスナー。
    CompanyMixinを継承しているモデルに対して、session_company_idによるWHERE句を追加します。
    """
    if (
        execute_state.is_select
        and not execute_state.is_column_load
        and not execute_state.is_relationship_load
    ):
        current_company_id = get_current_company_id()

        execute_state.statement = execute_state.statement.options(
            with_loader_criteria(
                CompanyMixin,
                lambda cls: cls.company_id == current_company_id,
                include_aliases=True,
                propagate_to_loaders=True,
                track_closure_variables=False,
            )
        )


@event.listens_for(CompanyMixin, 'before_insert', propagate=True)
def receive_before_insert(mapper, connection, target):
    if target.company_id is None:
        raise ValueError("company_id is required")

    if target.company_id != get_current_company_id():
        raise ValueError("company_id does not match the session company_id")

    print(f"Before insert: {target}")

@event.listens_for(CompanyMixin, 'before_update', propagate=True)
def receive_before_update(mapper, connection, target):
    state = inspect(target)
    
    history = state.attrs.company_id.history
    if history.has_changes():
        raise ValueError("Updating company_id is not allowed")

    if target.company_id != get_current_company_id():
        raise ValueError("company_id does not match the session company_id")
    
    print(f"Before update: {target}")

@event.listens_for(CompanyMixin, 'before_delete', propagate=True)
def receive_before_delete(mapper, connection, target):
    if target.company_id != get_current_company_id():
        raise ValueError("company_id does not match the session company_id")

    print(f"Before delete: {target}")
