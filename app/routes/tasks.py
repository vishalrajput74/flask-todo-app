import csv
import io
from flask import Response


from flask import Blueprint,render_template,request,redirect,url_for,flash,session
# from app import db
from app.extensions import db
from app.models import Task
from app.forms import TaskForm, EditTaskForm, UpdateStatusForm, DeleteTaskForm, ClearTasksForm, BulkActionForm 
from datetime import date
from sqlalchemy import nulls_last

#create blueprint
tasks_bp = Blueprint('tasks',__name__)

#helper function for state preservation
def get_redirect_params():
    page = request.form.get('page') or request.args.get('page', 1)
    try:
        page = int(page)
    except (TypeError, ValueError):
        page = 1
    status = request.form.get('status_filter', request.args.get('status', 'All'))
    search = request.form.get('search', request.args.get('search', ''))
    priority = request.form.get('priority', request.args.get('priority', 'All'))  # ADD
    
    per_page = request.form.get('per_page') or request.args.get('per_page', 5)
    sort_by = request.args.get('sort_by', 'id')     
    sort_order = request.args.get('sort_order', 'desc') 
    return dict(page=page, status=status, search=search, per_page=per_page,priority=priority,sort_by=sort_by,sort_order=sort_order)


#helper function for calculate_priority
def calculate_priority(due_date):
    if not due_date:
        return None
    days = (due_date - date.today()).days
    if days <= 2:   return 'High'
    elif days <= 5: return 'Medium'
    else:           return 'Low'
    
    
@tasks_bp.route('/')
def view_tasks():
    # print("view task route hit")
    # print("session ", dict(session), flush=True)
    if 'user_id' not in session:
        # print("user not loged in")
        return redirect(url_for('auth.login'))
    page = request.args.get('page', 1, type=int)
    # per_page dropdown feature: read selected items-per-page from query string
    per_page = request.args.get('per_page', 5, type=int)
    if per_page not in [5, 10, 25]:
        per_page = 5
     #filter status read 
    status = request.args.get('status')
    # print("Filter status:", status)
    search = request.args.get('search')
    priority = request.args.get('priority', 'All') 
     # Priority auto-calculate + save
    all_tasks = Task.query.filter_by(user_id=session['user_id']).all()
    changed = False
    for task in all_tasks:
        new_priority = calculate_priority(task.due_date)
        if task.priority != new_priority:
            task.priority = new_priority
            changed = True
    if changed:
        db.session.commit()
    
     #base query
    query = Task.query.filter_by(user_id=session['user_id'])
    # tasks = Task.query.filter_by(user_id=session['user_id']).all()
    # print("task fetch",tasks)
    
    #  filter apply karo
    if status and status != "All":
        # print("Applying filter",status)
        query = query.filter_by(status=status)
        
    if search and search.strip():
        s = search.strip()
        query = query.filter(Task.title.ilike(f"%{s}%"))
        
    if priority and priority != 'All':
        if priority == 'None':
            query = query.filter(Task.priority == None)
        else:
            query = query.filter_by(priority=priority)
    sort_by = request.args.get('sort_by', 'id')
    sort_order = request.args.get('sort_order', 'desc')     
    
    if sort_by == 'due_date':
        if sort_order == 'asc':
            order = Task.due_date.asc().nulls_last()
        else:
            order = Task.due_date.desc().nulls_last()
    else:
        order = Task.id.desc()
    pagination = query.order_by(order).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    # clamp high page to last page (if any)
    if pagination.pages and page > pagination.pages:
        # keep per_page while clamping invalid high page numbers
        return redirect(url_for('tasks.view_tasks', page=pagination.pages, status=status, search=search, per_page=per_page,priority=priority))
    tasks = pagination.items
    # final tasks
    # tasks = query.all()
    # tasks = query.order_by(Task.id.desc()).all()
    # print("Total tasks ",len(tasks))
    
    # for t in tasks:
    #     print(t.id, t.title)
    stats = {
    'total': Task.query.filter_by(user_id=session['user_id']).count(),
    'pending': Task.query.filter_by(user_id=session['user_id'], status='Pending').count(),
    'working': Task.query.filter_by(user_id=session['user_id'], status='Working').count(),
    'done': Task.query.filter_by(user_id=session['user_id'], status='Done').count(),
    'overdue': Task.query.filter(
        Task.user_id == session['user_id'],
        Task.due_date < date.today(),
        Task.status != 'Done'
    ).count(),
}
    
    form = TaskForm()  # Pass form to template
    update_status_form = UpdateStatusForm()
    delete_form = DeleteTaskForm() 
    clear_form = ClearTasksForm() 
    bulk_action_form = BulkActionForm()
    
    #Pass all forms to template
    return render_template('tasks.html', tasks=tasks,pagination=pagination,form=form, 
                        update_status_form=update_status_form, delete_form=delete_form, clear_form=clear_form,bulk_action_form=bulk_action_form,
today=date.today(),priority=priority,stats=stats)

@tasks_bp.route('/add', methods=["POST"])
def add_task():
    # print("add task route hit")
    # print("session",dict(session))
    if 'user_id' not in session:
        # print("not logged in ")
        return redirect(url_for('auth.login'))
    
    form = TaskForm()
    
    if form.validate_on_submit():
        # print("form valid")
        # print("title",form.title.data)
        new_task = Task(title=form.title.data,due_date=form.due_date.data,status='Pending',user_id=session['user_id'])
        db.session.add(new_task)
        db.session.commit()
        
        # print("task saved with id",new_task.id)
        flash('Task added successfully!', 'success')
    else:
        # print("form.errors")
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'error')
    
    return redirect(url_for('tasks.view_tasks', **get_redirect_params()))



@tasks_bp.route('/update-status/<int:task_id>', methods=["POST"])
def update_status(task_id):
    if 'user_id' not in session:
        flash("Please login first", "error")
        return redirect(url_for('auth.login'))
    
    form = UpdateStatusForm()
    
    if not form.validate_on_submit():
        flash("CSRF validation failed", "error")
        return redirect(url_for('tasks.view_tasks', **get_redirect_params()))

    
    task = Task.query.filter_by(id=task_id, user_id=session['user_id']).first()
    
    if not task:
        flash("Task not found!", "error")
        return redirect(url_for('tasks.view_tasks', **get_redirect_params()))

    new_status = request.form.get('status')
    if new_status in ['Pending', 'Working', 'Done']:
        task.status = new_status
        db.session.commit()
        flash('Status updated!', 'success')
    
    # return redirect(url_for('tasks.view_tasks', **get_redirect_params()))
    params = get_redirect_params()
    return redirect(url_for('tasks.view_tasks', **params))

@tasks_bp.route('/clear', methods=["POST"])
def clear_tasks():
    if 'user_id' not in session:
        flash("Please login first", "error")
        return redirect(url_for('auth.login'))
    
    form = ClearTasksForm() # validation
    
    if not form.validate_on_submit():  
        flash("CSRF validation failed", "error")
        # preserve pagination/filter/search to return user to same view
        return redirect(url_for('tasks.view_tasks', **get_redirect_params()))

    
    # deleted_count = Task.query.filter_by(user_id=session['user_id']).delete(synchronize_session=False)
    status = request.form.get('status', 'All')
    query = Task.query.filter_by(user_id=session['user_id'])
    if status and status != 'All':
        query = query.filter_by(status=status)
    deleted_count = query.delete(synchronize_session=False)
    db.session.commit()
    flash(f'{deleted_count} task(s) cleared!', 'info')
    return redirect(url_for('tasks.view_tasks', **get_redirect_params()))


@tasks_bp.route('/edit/<int:task_id>', methods=["GET", "POST"])
def edit_task(task_id):
    # task = Task.query.get(task_id)
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    task = Task.query.filter_by(id=task_id,user_id=session['user_id']).first()
    if not task:
        flash("Task not found", "error")
        return redirect(url_for('tasks.view_tasks', **get_redirect_params()))
    
    form = EditTaskForm()
    
    if form.validate_on_submit():
        # ← sirf yahan change hai
        if form.due_date.data and form.due_date.data < date.today():
            if form.due_date.data != task.due_date:
                flash('Due date cannot be in the past.', 'error')
                return render_template('edit.html', task=task, form=form)
        
        task.title = form.title.data
        task.due_date = form.due_date.data
        db.session.commit()
        flash("Task updated successfully!", "success")
        return redirect(url_for('tasks.view_tasks', **get_redirect_params()))

    elif request.method == "GET":
        form.title.data = task.title
        form.due_date.data = task.due_date
    return render_template('edit.html', task=task, form=form)

@tasks_bp.route('/delete/<int:task_id>', methods=["POST"])
def delete_task(task_id):
    if 'user_id' not in session:
       flash("Please login first", "error")
       return redirect(url_for('auth.login'))
    
    form = DeleteTaskForm()  # validation
    
    if not form.validate_on_submit():  
        flash("CSRF validation failed", "error")
        return redirect(url_for('tasks.view_tasks', **get_redirect_params()))

    task = Task.query.filter_by(id=task_id, user_id=session['user_id']).first()
    
    if not task:
        flash("Task not found!", "error")
        return redirect(url_for('tasks.view_tasks', **get_redirect_params()))
    
    db.session.delete(task)
    db.session.commit()
    flash("Task deleted successfully!", "success")
    return redirect(url_for('tasks.view_tasks', **get_redirect_params()))

@tasks_bp.route('/bulk-action', methods=["POST"])
def bulk_action():
    if 'user_id' not in session:
        flash("Please login first", "error")
        return redirect(url_for('auth.login'))

    form = BulkActionForm()

    if not form.validate_on_submit():
        flash("CSRF validation failed", "error")
        return redirect(url_for('tasks.view_tasks', **get_redirect_params()))

    task_ids = request.form.getlist('task_ids')
    action = request.form.get('action')

    if not task_ids:
        flash("No tasks selected!", "info")
        return redirect(url_for('tasks.view_tasks', **get_redirect_params()))

    try:
        task_ids = [int(task_id) for task_id in task_ids]
    except ValueError:
        flash("Invalid task selection", "error")
        return redirect(url_for('tasks.view_tasks', **get_redirect_params()))

    tasks = Task.query.filter(
        Task.id.in_(task_ids),
        Task.user_id == session['user_id']
    ).all()

    if not tasks:
        flash("No matching tasks found!", "info")
        return redirect(url_for('tasks.view_tasks', **get_redirect_params()))

    if action == 'delete':
        for task in tasks:
            db.session.delete(task)
        db.session.commit()
        flash(f"{len(tasks)} task(s) deleted!", "success")

    elif action == 'done':
        for task in tasks:
            task.status = 'Done'
        db.session.commit()
        flash(f"{len(tasks)} task(s) marked as Done!", "success")

    elif action == 'working':
        for task in tasks:
            task.status = 'Working'
        db.session.commit()
        flash(f"{len(tasks)} task(s) marked as Working!", "success")

    else:
        flash("Invalid action!", "error")

    return redirect(url_for('tasks.view_tasks', **get_redirect_params()))

@tasks_bp.route('/export-csv')
def export_csv():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    query = Task.query.filter_by(user_id=session['user_id'])
    
    status = request.args.get('status', 'All')
    search = request.args.get('search', '')
    priority = request.args.get('priority', 'All')

    if status and status != 'All':
        query = query.filter_by(status=status)

    if search and search.strip():
        query = query.filter(Task.title.ilike(f"%{search.strip()}%"))

    if priority and priority != 'All':
        if priority == 'None':
            query = query.filter(Task.priority == None)
        else:
            query = query.filter_by(priority=priority)

    tasks = query.all()

    filename = 'tasks'
    if status != 'All':
        filename += f'_{status.lower()}'
    if priority != 'All':
        filename += f'_{priority.lower()}'
    filename += '.csv'

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Title', 'Due Date', 'Priority', 'Status'])

    for task in tasks:
        writer.writerow([
            task.title,
            task.due_date or '',
            task.priority or '',
            task.status
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )