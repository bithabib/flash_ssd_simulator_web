from app import app
from flask import render_template, session
@app.route('/regenerate')
def json_upload_to_regenerate():
    
    return render_template('json_upload_to_regenerate.html')