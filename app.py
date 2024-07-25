from flask import Flask, request
from jwt import encode
from services.task_service import TaskService
from services.user_service import UserService
from models.task import Task
from models.user import User
from helpers.authentication import AuthenticationHelper

def create_app(task_service = TaskService(), user_service = UserService()):
    app = Flask(__name__)
    task_service.start_csv_db()
    user_service.start_csv_db()
    # improve code structure.

    @app.get('/')
    def index():
        return ({"success": True}, 200)

    @app.post("/task")
    @AuthenticationHelper.validate_token
    def create_task():
        body = request.json
    
        if not body:
            return ({"error": "name is required"}, 400)
    
        task = Task(
            body["name"],
            body["done"] if body.get("done") else False
        )
        created_task_id = task_service.create_task(task)
        return ({"success": "Task created", "id": created_task_id}, 201)

    @app.get("/task")
    @AuthenticationHelper.validate_token
    def list_tasks():
        tasks = task_service.list_tasks()
        return (tasks, 200)
    
    @app.delete("/task/<int:task_id>")
    @AuthenticationHelper.validate_token
    def delete_task(task_id):
        task_service.delete_task(task_id)
        return ({}, 204)
    
    @app.put("/task/<int:task_id>")
    @AuthenticationHelper.validate_token
    def update_task(task_id):
        body = request.json
        if not body:
            return ({
                "error": "You must provide at least one atribute to be updated"
            }, 400)
        task_service.update_task(task_id, body)
        return ({"success": "task updated"}, 200)

    @app.post("/user")
    def create_user():
        body = request.json
        if not body or not body["username"] or not body["password"]:
            return ({"error": "username and password are required"}, 400)

        user = User(body["username"], body["password"])
        created_user_id = user_service.create_user(user)
        return ({"id": created_user_id, "success": "user created"}, 201)

    @app.post("/login")
    def login_user():
        body = request.json
        if not body or not body["username"] or not body["password"]:
            return ({"error": "username and password are required"}, 400)

        user = User(body["username"], body["password"])
        user_info = user_service.validate_credentials(user)
        if not user_info:
            return ({"error": "invalid credentials"}, 400)
        token = encode(user_info, "secret")

        return({"token": token}, 200)

    return app
