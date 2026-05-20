from flask import Blueprint, request, jsonify, session
from app.models import Task
from app.extensions import db
from app.utils.decorators import api_login_required
from app.extensions import csrf


api_tasks_bp = Blueprint('api_tasks', __name__, url_prefix='/api/tasks')

@api_tasks_bp.route('/', methods=['POST'])
@csrf.exempt
@api_login_required

def add_task():
    # print("add task hit")
    # print(request.headers)
    # print("HEADERS:", request.headers)
    # # print(" SESSION USER:", session.get('user_id'))
    data = request.get_json(silent=True)
    # print("data",data)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    title = data.get('title')
    # print("title",title)
    if not title:
        return jsonify({"error": "Title required"}), 400
    new_task = Task(
        title=title,
        status="Pending",
        user_id=session['user_id'])

    db.session.add(new_task)
    db.session.commit()

    return jsonify({"message": "Task created", "task_id": new_task.id})


@api_tasks_bp.route('/', methods=['GET'])
@api_login_required
def get_tasks():

    # print(" GET TASKS API HIT")
    # print(" SESSION USER:", session.get('user_id'))

    tasks = Task.query.filter_by(user_id=session['user_id']).all()

    result = []

    for t in tasks:
        result.append({
            "id": t.id,
            "title": t.title,
            "status": t.status
        })

    return jsonify(result)


@api_tasks_bp.route('/<int:task_id>', methods=['GET'])
@api_login_required
def get_single_task(task_id):

    # print(" SINGLE TASK API HIT")
    # print("TASK ID:", task_id)
    # print("USER:", session.get('user_id'))

    task = Task.query.filter_by(id=task_id,user_id=session['user_id']).first()

    if not task:
        return jsonify({"error": "Task not found"}), 404

    return jsonify({
        "id": task.id,
        "title": task.title,
        "status": task.status
    })
    
    
    
@api_tasks_bp.route('/<int:task_id>', methods=['PUT'])
@csrf.exempt
@api_login_required
def update_task(task_id):

    # print(" UPDATE API HIT")
    # print(" TASK ID:", task_id)
    # print(" USER:", session.get('user_id'))

    task = Task.query.filter_by(id=task_id,user_id=session['user_id']).first()

    if not task:
        return jsonify({"error": "Task not found"}), 404

    data = request.get_json(silent=True)
    # print(" DATA:", data)

    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    title = data.get('title')
    status = data.get('status')

    if title is not None:
        if not title.strip():
            return jsonify({"error": "Title cannot be empty"}), 400
        task.title = title

    if status is not None:
        if status not in ["Pending", "Done"]:
            return jsonify({"error": "Invalid status"}), 400
        task.status = status

    db.session.commit()

    return jsonify({
        "message": "Task updated",
        "task": {
            "id": task.id,
            "title": task.title,
            "status": task.status
        }
    })
    
@api_tasks_bp.route('/<int:task_id>', methods=['DELETE'])
@csrf.exempt
@api_login_required
def delete_task(task_id):

    # print(" DELETE API HIT")
    # print("TASK ID:", task_id)
    # print("USER:", session.get('user_id'))

    #  Task fetch (user specific)
    task = Task.query.filter_by(id=task_id,user_id=session['user_id']).first()

    if not task:
        return jsonify({"error": "Task not found"}), 404

    db.session.delete(task)
    db.session.commit()

    return jsonify({"message": "Task deleted"})