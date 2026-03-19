from sqlalchemy import Column, Integer, event

class CompanyMixin:
    company_id = Column(Integer, nullable=False)

@event.listens_for(CompanyMixin, 'before_insert', propagate=True)
def receive_before_insert(mapper, connection, target):
    # TODO: 必要な処理をここに記述
    print(f"Before insert: {target}")

@event.listens_for(CompanyMixin, 'before_update', propagate=True)
def receive_before_update(mapper, connection, target):
    # TODO: 必要な処理をここに記述
    print(f"Before update: {target}")

@event.listens_for(CompanyMixin, 'before_delete', propagate=True)
def receive_before_delete(mapper, connection, target):
    # TODO: 必要な処理をここに記述
    print(f"Before delete: {target}")
