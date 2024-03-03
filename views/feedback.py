from app import app
from flask import render_template
@app.route('/feedback')
def feedback():
    return render_template('feedback.html')