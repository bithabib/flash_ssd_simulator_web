from app import app
from flask import render_template
@app.route('/presentation')
def presentation():
    return render_template('presentation.html')