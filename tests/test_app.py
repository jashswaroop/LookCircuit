import unittest
import json
from backend.app import app, db, User, WardrobeItem

class TestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_register(self):
        response = self.app.post(
            '/register',
            data=json.dumps({'username': 'test', 'email': 'test@test.com', 'password': 'test'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)

    def test_login(self):
        self.app.post(
            '/register',
            data=json.dumps({'username': 'test', 'email': 'test@test.com', 'password': 'test'}),
            content_type='application/json'
        )
        response = self.app.post(
            '/login',
            data=json.dumps({'email': 'test@test.com', 'password': 'test'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def test_add_wardrobe_item(self):
        self.app.post(
            '/register',
            data=json.dumps({'username': 'test', 'email': 'test@test.com', 'password': 'test'}),
            content_type='application/json'
        )
        response = self.app.post(
            '/wardrobe/add',
            data=json.dumps({'name': 'test item', 'image_url': 'test.jpg'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)

    def test_get_wardrobe_items(self):
        self.app.post(
            '/register',
            data=json.dumps({'username': 'test', 'email': 'test@test.com', 'password': 'test'}),
            content_type='application/json'
        )
        self.app.post(
            '/wardrobe/add',
            data=json.dumps({'name': 'test item', 'image_url': 'test.jpg'}),
            content_type='application/json'
        )
        response = self.app.get('/wardrobe')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(len(data), 1)

if __name__ == '__main__':
    unittest.main()
