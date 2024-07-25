from csv import DictReader, DictWriter
from models.task import Task
from .base_service_class import BaseService

class TaskService(BaseService):
    _field_names = ["id","name", "done"]
    _id_generator = None

    def create_task(self, task: Task):
        if not self._id_generator:
            raise Exception("id generator is not initialized")
        with open(self._file_name, newline='', mode='a') as csv_db:
            writer = DictWriter(csv_db, self._field_names)
            id = next(self._id_generator())
            writer.writerow({
                "id": id,
                "name": task.name,
                "done": task.done
            })
            return id

    def list_tasks(self):
        with open(self._file_name, newline='') as csv_db:
            reader = DictReader(csv_db)
            return [
                {
                    "id": int(row["id"]),
                    "name": row["name"],
                    "done": True if row["done"] == "True" else False
                } for row in reader
            ]

    def get_task(self, id: int):
        with open(self._file_name, newline='') as csv_db:
            reader = DictReader(csv_db)
            for row in reader:
                if int(row["id"]) == id:
                    return {
                        "id": int(row["id"]),
                        "name": row["name"],
                        "done": True if row["done"] == "True" else False
                    }

    def update_task(self, task_id: int, body: dict):
        tasks = self.list_tasks()
        with open(self._file_name, mode="w") as csv_db:
            writer = DictWriter(csv_db, fieldnames=self._field_names)
            writer.writeheader()
            for task in tasks:
                if task["id"] == task_id:
                    if body.get("name"):
                        task["name"] = body["name"]

                    if body.get("done"):
                        task["done"] = body["done"]
                writer.writerow(task)

    def delete_task(self, task_id: int):
        tasks = self.list_tasks()
        with open(self._file_name, mode="w") as csv_db:
            writer = DictWriter(csv_db, fieldnames=self._field_names)
            writer.writeheader()
            for task in tasks:
                if task["id"] != task_id:
                    writer.writerow(task)
