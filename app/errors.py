from flask import render_template, request, jsonify
from app import app
from app.routes_api import API_PREFIX
from app.json_encoder import CustomJSONEncoder

def is_api(request):
    return request.path.startswith(API_PREFIX)

@app.errorhandler(500)
def internal_error(e):
    if is_api(request):
        exceptions = [
            {
                'name': e.__class__.__name__,
                'msg' : str(e),
                'args': e.__dict__
            }]
        return jsonify(exceptions=exceptions), 500
    
    return render_template('500.html')
