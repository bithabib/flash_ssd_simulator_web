from flask import render_template, request, jsonify
from app import app

@app.route('/converter')
def trace_file_converter():
    return render_template('trace_file_converter.html')