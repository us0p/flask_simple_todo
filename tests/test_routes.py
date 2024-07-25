from unittest import TestCase
from unittest.mock import Mock
from jwt import encode

from app import create_app
from models.task import Task
from models.user import User

class TestRoutes(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._task_service_mock = Mock()
        cls._task_service_mock.create_task.return_value = 1
        cls._task_service_mock.list_tasks.return_value = []

        cls._user_service_mock = Mock()
        cls._user_service_mock.create_user.return_value = 1

        cls._app = create_app(
            cls._task_service_mock,
            cls._user_service_mock
        )
        cls._client = cls._app.test_client()
        cls._app_request_context = cls._app.test_request_context()
        cls._default_token = encode({"id": 1, "username": "us0p"}, 'secret')
        cls._default_authorization_header = {
                "Authorization": cls._default_token
        }

    def test_status_route(self):
        with self._app_request_context:
            response = self._client.get(self._app.url_for("index"))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json,
                {"success": True}
            )
            
    def test_create_task_route(self):
        with self._app_request_context:
            request_bodies = [
                ({}, {}, {"error": "missing authorization token"}, 401),
                (
                    self._default_authorization_header,
                    {},
                    {"error": "name is required"},
                    400
                ),
                (
                    self._default_authorization_header,
                    {"name": "marry mari"},
                    {"success": "Task created", "id": 1},
                    201
                ),
                (
                    self._default_authorization_header,
                    {"name": "date mari", "done": True},
                    {"success": "Task created", "id": 1},
                    201
                )
            ]

            for headers, request_body, response_body, status_code in request_bodies:
                response = self._client.post(
                    self._app.url_for("create_task"),
                    json = request_body,
                    headers=headers
                )
                self.assertEqual(
                    response.status_code,
                    status_code
                )
                self.assertEqual(response.json, response_body)
                if status_code == 201:
                    self.assertEqual(
                        self
                        ._task_service_mock
                        .create_task
                        .call_args
                        .args[0]
                        .__dict__,
                        Task(
                            request_body["name"],
                            request_body["done"] if request_body.get("done")
                            else False
                        ).__dict__
                    )

    def test_list_tasks_route(self):
        with self._app_request_context:
            header_list = [
                ({}, {"error": "missing authorization token"}, 401),
                (
                    self._default_authorization_header,
                    [],
                    200
                )
            ]
            for header, res_body, status in header_list:
                response = self._client.get(
                    self._app.url_for("list_tasks"),
                    headers=header
                )
                self.assertEqual(
                    response.status_code,
                    status
                )
                self.assertEqual(
                    response.json,
                    res_body
                )
                if status == 200:
                    self._task_service_mock.list_tasks.assert_called_once()


    def test_delete_task_route(self):
        request_list = [
            ({}, {"error": "missing authorization token"}, 401),
            (
                self._default_authorization_header,
                b'',
                204
            )
        ]
        with self._app_request_context:
            for header, res_body, status in request_list:
                response = self._client.delete(
                    self._app.url_for("delete_task", task_id=1),
                    headers=header
                )
                self.assertEqual(
                    response.status_code,
                    status
                )
                if status == 401:
                    self.assertEqual(
                        response.json,
                        res_body
                    )
                else:
                    self.assertEqual(
                        response.data,
                        res_body
                    )
                    self._task_service_mock.delete_task.assert_called_with(1)

    def test_update_task_route(self):
        with self._app_request_context:
            request_bodies = [
                (
                    {},
                    {},
                    {"error": "missing authorization token"},
                    401
                ),
                (
                    self._default_authorization_header,
                    {},
                    {"error": "You must provide at least one atribute to be updated"},
                    400
                ),
                (
                    self._default_authorization_header,
                    {"name": "play something for mari"},
                    {"success": "task updated"},
                    200
                )
            ]
            for header, req_body, res_body, res_status in request_bodies:
                response = self._client.put(
                    self._app.url_for("update_task", task_id=1),
                    json=req_body,
                    headers=header
                )
                self.assertEqual(response.status_code, res_status)
                self.assertEqual(response.json, res_body)
                if res_status == 200:
                    self._task_service_mock.update_task.assert_called_with(
                            1,
                            req_body
                    )

    def test_create_user_route(self):
        with self._app_request_context:
            username = "us0p"
            password = "1234abcd"
            response = self._client.post(
                self._app.url_for("create_user"),
                json={"username": username, "password": password}
            )
            self.assertEqual(response.status_code, 201)
            self.assertEqual(
                    response.json,
                    {"id": 1, "success": "user created"}
            )
            user = User(username, password)
            self.assertEqual(
                self
                ._user_service_mock
                .create_user
                .call_args
                .args[0]
                .__dict__,
                user.__dict__
            )

    def test_login_user_route(self):
        with self._app_request_context:
            request_bodies = [
                (
                    {"username": "us0p","password": "1234abcd"},
                    {"token": self._default_token},
                    200
                ),
                (
                    {"username": "us0p","password": "1234abcd"},
                    {"error": "invalid credentials"},
                    400
                )
            ]
            for req_body, res_body, status in request_bodies:
                if status == 400:
                    self._user_service_mock.validate_credentials.return_value = None
                else:
                    self._user_service_mock.validate_credentials.return_value = {
                        "id": 1,
                        "username": "us0p"
                    }

                response = self._client.post(
                    self._app.url_for("login_user"),
                    json=req_body
                )
                self.assertEqual(response.status_code, status)
                self.assertEqual(
                    response.json,
                    res_body
                )
                user = User(req_body["username"], req_body["password"])
                self.assertEqual(
                        self
                        ._user_service_mock
                        .validate_credentials
                        .call_args
                        .args[0]
                        .__dict__,
                        user.__dict__
                )
