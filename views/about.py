from app import app
from flask import render_template
import subprocess
@app.route('/about')
def paper():
    bash_script_path = 'paper_writing/bash_file/latex_to_pdf.sh'
    try:
        # subprocess.run(['bash', bash_script_path], check=True, bufsize=0)
        pass
    except subprocess.CalledProcessError as e:
        print(e)
    return render_template('about.html')