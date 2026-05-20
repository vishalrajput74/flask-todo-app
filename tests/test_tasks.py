# import pytest
# from app import create_app

# @pytest.fixture
# def client():
#     app = create_app()
#     app.config['TESTING'] = True
#     app.config['WTF_CSRF_ENABLED'] = False
#     app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_todo.db'
    
#     with app.test_client() as client:
#         with app.app_context():
#             from app.extensions import db
#             db.create_all()
#             yield client
#             db.drop_all()

# @pytest.fixture
# def logged_in_client(client):
#     # Register + Login
#     client.post('/register', data={
#         'username': 'testuser',
#         'password': 'test123',
#         'confirm_password': 'test123'
#     })
#     client.post('/login', data={
#         'username': 'testuser',
#         'password': 'test123'
#     })
#     return client

# # Test 1 — Tasks page load
# def test_tasks_page(logged_in_client):
#     response = logged_in_client.get('/')
#     assert response.status_code == 200

# # Test 2 — Task add karo
# def test_add_task(logged_in_client):
#     response = logged_in_client.post('/add', data={
#         'title': 'Test task',
#         'due_date': '2026-06-01'
#     })
#     assert response.status_code == 302

# # Test 3 — Task delete karo
# def test_delete_task(logged_in_client):
#     logged_in_client.post('/add', data={
#         'title': 'Delete me',
#         'due_date': ''
#     })
#     response = logged_in_client.post('/delete/1')
#     assert response.status_code == 302

# # Test 4 — Logout
# def test_logout(logged_in_client):
#     response = logged_in_client.get('/logout')
#     assert response.status_code == 302