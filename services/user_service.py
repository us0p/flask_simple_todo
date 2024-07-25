from csv import DictReader, DictWriter
from models.user import User
from .base_service_class import BaseService
from hashlib import sha256

class UserService(BaseService):
    _field_names = ['id', 'username', 'password']
    _id_generator = None

    def __init__(self, file_name = "users.csv"):
        self._file_name = file_name

    def create_user(self, user: User):
        if not self._id_generator:
            raise Exception("id generator is not initialized")
        with open(self._file_name, newline='', mode='a') as csv_db:
            writer = DictWriter(csv_db, fieldnames=self._field_names)
            user_id = next(self._id_generator())
            writer.writerow({
                "id": user_id,
                "username": user.username,
                "password": self.hash_password(user.password)
            })
            return user_id

    def hash_password(self, password: str):
        hasher = sha256()
        hasher.update(bytes(password, encoding='utf-8'))
        return hasher.hexdigest()

    def validate_credentials(self, user: User):
        hashed_pass = self.hash_password(user.password)
        with open(self._file_name, newline='') as csv_db:
            reader = DictReader(csv_db)
            for row in reader:
                if row["username"] == user.username:
                    if row["password"] == hashed_pass:
                        return {
                            "id": int(row["id"]),
                            "username": user.username
                        }
