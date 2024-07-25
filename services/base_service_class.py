from os.path import isfile
from csv import DictWriter, DictReader

class BaseService:
    _file_name: str
    _field_names: list[str]

    def __init__(self, file_name = "tasks.csv"):
        self._file_name = file_name

    def start_csv_db(self):
        if not isfile(self._file_name):
            with open(self._file_name, mode="w+") as csv_db:
                writer = DictWriter(csv_db, fieldnames=self._field_names)
                writer.writeheader()

        with open(self._file_name) as csv_db:
            reader = DictReader(csv_db, fieldnames=self._field_names)
            last_id = 0
            for row in reader:
                id = row["id"]
                if id.isdecimal():
                    last_id = int(row["id"])

            self._id_generator = self._id_generator_closure(last_id)

    def _id_generator_closure(self, starting_id: int):
        id = starting_id + 1
        def id_generator():
            nonlocal id
            id += 1
            yield id - 1

        return id_generator
