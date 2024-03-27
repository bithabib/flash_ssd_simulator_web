from app import app
from flask import render_template
@app.route('/advance_ssd')
def advance_ssd_simulator():
    return render_template('advance_ssd_simulator.html')