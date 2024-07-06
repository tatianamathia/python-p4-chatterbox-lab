from datetime import datetime

from app import app
from models import db, Message
import pytest

class TestApp:
    '''Flask application in app.py'''

    @classmethod
    def setup_class(cls):
        with app.app_context():
            db.create_all()
            # Clean up existing messages for test consistency
            db.session.query(Message).filter(Message.body == "Hello 👋", Message.username == "Liza").delete()
            db.session.commit()

    def setup_method(self, method):
        # Each test method starts with a clean session
        self.app_context = app.app_context()
        self.app_context.push()
        self.client = app.test_client()

    def teardown_method(self, method):
        # Clean up session after each test method
        db.session.rollback()
        db.session.close()
        self.app_context.pop()

    @classmethod
    def teardown_class(cls):
        with app.app_context():
            db.drop_all()

    def test_has_correct_columns(self):
        with app.app_context():
            hello_from_liza = Message(body="Hello 👋", username="Liza")
            db.session.add(hello_from_liza)
            db.session.commit()

            assert hello_from_liza.body == "Hello 👋"
            assert hello_from_liza.username == "Liza"
            assert isinstance(hello_from_liza.created_at, datetime)

    def test_returns_list_of_json_objects_for_all_messages_in_database(self):

        with app.app_context():
            response = self.client.get('/messages')
            assert response.status_code == 200
            messages = Message.query.all()
            json_data = response.get_json()

            assert len(json_data) == len(messages)
            for message in json_data:
                assert any(message['body'] == m.body for m in messages)

    def test_creates_new_message_in_the_database(self):

        with app.app_context():
            response = self.client.post('/messages', json={
                "body": "Hello 👋",
                "username": "Liza"
            })
            assert response.status_code == 200

            new_message = Message.query.filter_by(body="Hello 👋").first()
            assert new_message is not None

    def test_returns_data_for_newly_created_message_as_json(self):

        with app.app_context():
            response = self.client.post('/messages', json={
                "body": "Hello 👋",
                "username": "Liza"
            })
            assert response.content_type == 'application/json'
            assert response.json['body'] == "Hello 👋"
            assert response.json['username'] == "Liza"

    def test_updates_body_of_message_in_database(self):
        with app.app_context():
            new_message = Message(body="Hello 👋", username="Liza")
            db.session.add(new_message)
            db.session.commit()

            response = self.client.patch(f'/messages/{new_message.id}', json={
                "body": "Goodbye 👋"
            })
            assert response.status_code == 200

            updated_message = Message.query.get(new_message.id)
            assert updated_message.body == "Goodbye 👋"

    def test_returns_data_for_updated_message_as_json(self):

        with app.app_context():
            new_message = Message(body="Hello 👋", username="Liza")
            db.session.add(new_message)
            db.session.commit()

            response = self.client.patch(f'/messages/{new_message.id}', json={
                "body": "Goodbye 👋"
            })
            assert response.content_type == 'application/json'
            assert response.json['body'] == "Goodbye 👋"

    def test_deletes_message_from_database(self):

        with app.app_context():
            new_message = Message(body="Hello 👋", username="Liza")
            db.session.add(new_message)
            db.session.commit()

            response = self.client.delete(f'/messages/{new_message.id}')
            assert response.status_code == 200

            deleted_message = Message.query.get(new_message.id)
            assert deleted_message is None