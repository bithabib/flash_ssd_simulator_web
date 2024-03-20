from flask import Flask, request, redirect, send_from_directory
app = Flask(__name__)
from views import flash_ssd_simulation
from views import cell_simulator
from views import paper
# from views import sitemap_xml

@app.before_request
def redirect_to_domain():
    if request.host.startswith('3.89.197.36') and request.host.endswith(':3000'):
        return redirect('https://ssd.qbithabib.com', code=301)

@app.route('/robots.txt')
@app.route('/sitemap.xml')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])