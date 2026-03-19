import datetime
from app.database import SessionLocal, Base
from app.model import User, Task

def main():
    db = SessionLocal()
    try:
        # --- 既存のユーザー情報を表示 ---
        print("--- Existing Users ---")
        users = db.query(User).all()
        for user in users:
            print(f"ID: {user.id}, Name: {user.name}, Email: {user.email}")

        # --- Create (Insert) ---
        # 新しいタスクを作成してデータベースに保存します
        print("\n--- Creating a new task ---")
        new_task = Task(todo="Sample Task", company_id=1)
        db.add(new_task)
        db.commit()
        db.refresh(new_task) # 生成されたIDなどを取得するためにリフレッシュ
        print(f"Created Task ID: {new_task.id}, Todo: {new_task.todo}")

        # --- Read (Select) ---
        # すべてのタスクを取得して表示します
        tasks = db.query(Task).all()
        print(f"\nTotal tasks: {len(tasks)}")
        for task in tasks:
            print(f"ID: {task.id}, Todo: {task.todo}, Company ID: {task.company_id}")

        # --- Update ---
        # 先ほど作成したタスクの内容を更新します
        print(f"\n--- Updating task ID: {new_task.id} ---")
        task_to_update = db.query(Task).filter(Task.id == new_task.id).first()
        if task_to_update:
            task_to_update.todo = "Updated Sample Task"
            # task_to_update.company_id = 100 # 会社IDを更新してみる（これがエラーになるはず）
            db.commit()
            db.refresh(task_to_update)
            print(f"Updated Task ID: {task_to_update.id}, Todo: {task_to_update.todo}")

        # --- Delete ---
        # 更新したタスクを削除します
        print(f"\n--- Deleting task ID: {new_task.id} ---")
        task_to_delete = db.query(Task).filter(Task.id == new_task.id).first()
        if task_to_delete:
            db.delete(task_to_delete)
            db.commit()
            print(f"Deleted Task ID: {new_task.id}")

        # --- Final Read ---
        # 削除後のタスク一覧を確認します
        final_tasks = db.query(Task).all()
        print(f"\nTotal tasks after deletion: {len(final_tasks)}")

    except Exception as e:
        print(f"Error occurred: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
