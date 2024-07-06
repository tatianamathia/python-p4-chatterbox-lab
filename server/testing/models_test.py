from datetime import datetime

from app import app
from models import db, Message

class TestMessage:
    '''Message model in models.py'''

    @classmethod
    def setup_class(cls):
        with app.app_context():
            # Clean up existing messages for test consistency
            db.session.query(Message).filter(Message.body == "Hello 👋", Message.username == "Liza").delete()
            db.session.commit()

    def setup_method(self, method):
        # Each test method starts with a clean session
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def teardown_method(self, method):
        # Clean up session after each test method
        db.session.rollback()
        db.session.close()
        db.drop_all()
        self.app_context.pop()

    def test_has_correct_columns(self):
        with self.app_context:
            hello_from_liza = Message(
                body="Hello 👋",
                username="Liza"
            )
            db.session.add(hello_from_liza)
            db.session.commit()

            assert hello_from_liza.body == "Hello 👋"
            assert hello_from_liza.username == "Liza"
            assert isinstance(hello_from_liza.created_at, datetime)
