# import pytest
# from app import create_app

# @pytest.fixture
# def client():
#     app = create_app()
#     app.config['TESTING'] = True
#     app.config['WTF_CSRF_ENABLED'] = False  # test mein CSRF off
#     app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_todo.db'  # test DB
    
#     with app.test_client() as client:
#         with app.app_context():
#             from app.extensions import db
#             db.create_all()
#             yield client
#             db.drop_all()

# # Test 1 — Login page load hoti hai?
# def test_login_page(client):
#     response = client.get('/login')
#     assert response.status_code == 200

# # Test 2 — Register kaam karta hai?
# def test_register(client):
#     response = client.post('/register', data={
#         'username': 'testuser',
#         'password': 'test123',
#         'confirm_password': 'test123'
#     })
#     assert response.status_code == 302  # redirect

# # Test 3 — Login kaam karta hai?
# def test_login(client):
#     # Pehle register karo
#     client.post('/register', data={
#         'username': 'testuser',
#         'password': 'test123',
#         'confirm_password': 'test123'
#     })
#     # Phir login karo
#     response = client.post('/login', data={
#         'username': 'testuser',
#         'password': 'test123'
#     })
#     assert response.status_code == 302  # redirect to tasks

# # Test 4 — Wrong password
# def test_login_wrong_password(client):
#     client.post('/register', data={
#         'username': 'testuser',
#         'password': 'test123',
#         'confirm_password': 'test123'
#     })
#     response = client.post('/login', data={
#         'username': 'testuser',
#         'password': 'wrongpassword'
#     })
#     assert response.status_code == 200  # same page pe rehta hai