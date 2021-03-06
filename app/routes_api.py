from flask import render_template, redirect, flash, url_for, request, jsonify
from flask_login import login_required
from werkzeug.urls import url_parse
from sqlalchemy import and_, or_
from app import app, db
from app.forms import EmployeeForm, EmployeeDeleteForm
from app.models import Employee
from app.exceptions import HierarchyLoopError

API_PREFIX = '/api'
API_PUBLIC_PREFIX = '/api_public'
CSRF_TOKEN_NAME = 'csrf_token'
exclude_fields = [CSRF_TOKEN_NAME, 'submit']

def request_to_query(query_data, cls):
    """Return an sqlalchemy query instance to be used in filter() method.
    :param query_data: A dictionary, where keys and values are column names and filter values
        respectively. Keys are combined as AND conditions. Values can be list of values, that will
        be combined as OR conditions. Keys can be prefixed with underscore resulting in ILIKE filter
        rather than '==' filter. 
    :param cls: A class, Model class that is being queried.
    """
    filter_conditions = []
    for key, val in query_data.items():
        col = getattr(cls, key[1:] if key.startswith('_') else key)
        values = val if isinstance(val, list) else [val]
        or_conditions = []
        for item in values:
            if key.startswith('_'):
                or_conditions.append(col.ilike('%' + str(item) + '%'))
            else:
                or_conditions.append(col==item)
        filter_conditions.append(or_(*or_conditions))

    return and_(*filter_conditions)


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

    request_data = next((x for x in [request.get_json(), request.form, request.args] if x), {})
    query_data = {key: val for key, val in request_data.items() if val != ''
        and key not in exclude_fields}
        
    query_data = request_to_query(query_data, cls)
    entries = cls.query.filter(query_data).all()
    return jsonify(entries), 200


@app.route(API_PUBLIC_PREFIX + '/get/<string:classname>', methods=['GET', 'POST'])
def api_public_get_object(classname):
    '''A limited version of api_get_object method available for anonymous users. Return object
    dictionaries as well as search parameters are restricted to specific fields.
    '''
    allowed_models = {
        'employee': Employee
    }
    try:
        cls = allowed_models[classname]
    except KeyError:
        return jsonify(errors=['Unknown or forbidden object type']), 400

    allowed_fields = {
        Employee: ['id', 'name', 'position', 'subordinates_id', 'supervisor_id']
    }

    request_data = next((x for x in [request.get_json(), request.form, request.args] if x), {})
    query_data = {key: val for key, val in request_data.items() if val != ''
        and key not in exclude_fields and key in allowed_fields[cls]}
        
    query_data = request_to_query(query_data, cls)
    entries = cls.query.filter(query_data).all()
    result = [e.toJSONifiable(include_fields=allowed_fields[cls]) for e in entries]
    return jsonify(result), 200
