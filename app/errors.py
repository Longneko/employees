from flask import render_template, request, jsonify
from app import app, db
from app.routes_api import API_PREFIX, API_PUBLIC_PREFIX
from app.json_encoder import CustomJSONEncoder

def is_api(request):
    return any(request.path.startswith(x) for x in [API_PREFIX, API_PUBLIC_PREFIX])

@app.errorhandler(500)
def internal_error(e):
    db.session.rollback()

    if is_api(request):
        exceptions = [
            {
                'name': e.__class__.__name__,
                'msg' : str(e),
                'args': e.__dict__
            }]
        return jsonify(exceptions=exceptions), 500
    
    return render_template('500.html')
