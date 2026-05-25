from app.models import Task
from flask_migrate import upgrade
from app import create_app,db
import os

app=create_app()  #function call for app creation
print(app.config["SQLALCHEMY_DATABASE_URI"])
# print("DB Path:", os.path.abspath('instance/todo.db'))
# print("Current Working Directory:", os.getcwd())

with app.app_context():
    print(Task.query.count())
    db.create_all()
    upgrade()
if __name__=="__main__":
    app.run(debug=False,port=5001)
    