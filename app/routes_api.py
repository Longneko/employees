import operator
from flask import render_template, redirect, flash, url_for, request, jsonify
from flask_login import login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import EmployeeForm, EmployeeDeleteForm
from app.models import Employee
from app.exceptions import HierarchyLoopError

API_PREFIX = '/api'
API_PUBLIC_PREFIX = '/api_public'
CSRF_TOKEN_NAME = 'csrf_token'
exclude_fields = [CSRF_TOKEN_NAME, 'submit']

@app.route(API_PREFIX + '/employee/delete', methods=['POST'])
@login_required
def api_employee_delete():
    form = EmployeeDeleteForm()
    if form.validate_on_submit():
        employee = Employee.query.get(int(form.id.data))
        if form.replacement_id.data:
            replacement = Employee.query.get(int(form.replacement_id.data))
            try:
                employee.transfer_subs(replacement)
            except HierarchyLoopError as err:
                errors = {form.replacement_id.id: [str(err)]}
                return jsonify(errors=errors), 400

        db.session.delete(employee)
        db.session.commit()


        return jsonify(success=True), 200

    errors = {field.id: [err for err in field.errors] for field in form if field.errors}

    return jsonify(errors=errors), 400


@app.route(API_PREFIX + '/flash', methods=['GET', 'POST'])
def api_flash():
    if request.method == 'POST':
        msg = request.form.get('msg')
        category = request.form.get('category')
    else:
        msg = request.args.get('msg')
        category = request.args.get('category')

    if not msg:
        return jsonify(success=False), 400

    flash(msg, category)

    return jsonify(success=True), 200


@app.route(API_PREFIX + '/get/<string:classname>', methods=['GET', 'POST'])
@login_required
def api_get_object(classname):
    '''Return a list of JSON encoded objects of the specified class queried with the provided args.
    Arguments with names preceded by an underscore (e.g. '_full_name=') require partial match, while 
    regular named arguments require full match.
    Automoatically omits the 'submit' args and the csrf_token related args.
    '''
    allowed_models = {
        'employee': Employee
    }
    try:
        cls = allowed_models[classname]
    except KeyError:
        return jsonify(errors=['Unknown object type']), 400
    
    filters = []
    filter_bys = {}
    
    if request.method == 'POST':
        query_data = {key: val for key, val in request.form.items() if val != ''
            and key not in exclude_fields}
    else:
        query_data = {key: val for key, val in request.args.items() if val != ''
            and key not in exclude_fields}

    for key, val in query_data.items():
        if key.startswith('_'):
            col = getattr(cls, key[1:])
            filters.append(col.like('%' + str(val) + '%'))
        else:
            filter_bys[key] = val

    entries = cls.query.filter_by(**filter_bys).filter(*filters).all()

    return jsonify(entries), 200
