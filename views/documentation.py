from app import app
from flask import render_template_string
import markdown

@app.route('/documentation')
def documentation():
    documentation_file_path = 'templates/documentation.md'
    md_template_file = open(documentation_file_path, 'r')
    md_template_string = markdown.markdown(
            md_template_file.read(),
            extensions=['fenced_code']
        )
    return md_template_string
    # return render_template_string()