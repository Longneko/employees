from flask import render_template, redirect, flash, url_for, request, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, EmployeeForm, EmployeeDeleteForm
from app.models import Employee, User


@app.route('/')
@app.route('/index')
def index():
    return render_template('hierarchy.html', title='Hierarchy')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'warning')
            return redirect(url_for('login'))
        
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        flash('User registered successfully!', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', title='Register', form=form)

@app.route('/manage')
@login_required
def manage():
    form = EmployeeDeleteForm()
    return render_template('manage.html', title='Manage', form=form)

@app.route('/employee/new', defaults={'id': None}, methods=['GET', 'POST'])
@app.route('/employee/<int:id>', methods=['GET', 'POST'])
@login_required
def employee(id):
    form = EmployeeForm()
    if form.validate_on_submit():
        if not form.id.data:
            employee = Employee()
            message = ('New employee added successfully!', 'success')
        else:
            employee = Employee.query.filter_by(id=int(form.id.data)).first()
            message = ('Employee changes saved successfully!', 'success')

        for attr_name in ['full_name', 'position', 'hire_date', 'salary']:
            setattr(employee, attr_name, getattr(form, attr_name).data)
        employee.supervisor = Employee.query.filter_by(id=form.supervisor_id.data).first()

        db.session.add(employee)
        db.session.commit()
        flash(*message)
        return redirect(url_for('employee', id=employee.id))
    
    if id:
        employee = Employee.query.filter_by(id=id).first_or_404()
        for attr_name in ['id', 'full_name', 'position', 'hire_date', 'salary', 'supervisor_id']:
            getattr(form, attr_name).data = getattr(employee, attr_name)
        title = '[{id}] {name}'.format(id=id, name=employee.full_name)
    else:
        title = 'New Employee'

    return render_template('employee.html', title=title, form=form)

@app.route('/employee/delete', methods=['POST'])
@login_required
def employee_delete():
    next_page = request.args.get('next')
    form = EmployeeDeleteForm()
    if form.validate_on_submit():
        employee = Employee.query.filter_by(id=int(form.id.data)).first_or_404()
        if form.replacement_id.data:
            replacement = Employee.query.filter_by(id=int(form.replacement_id.data)).first()
            employee.transfer_subs(replacement)

        db.session.delete(employee)
        db.session.commit()

        if next_page:
            flash('Employee deleted successfully!', 'success')
            if url_parse(next_page).netloc != '':
                next_page = url_for('manage')
            return redirect(next_page)

        return jsonify(success=True), 200

    errors = {field.name: [err for err in field.errors] for field in form if field.errors}

    return jsonify(errors), 400
