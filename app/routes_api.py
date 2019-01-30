from flask import render_template, redirect, flash, url_for, request, jsonify
from flask_login import login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import EmployeeForm, EmployeeDeleteForm
from app.models import Employee
from app.exceptions import HierarchyLoopError

API_PREFIX = '/api'

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
