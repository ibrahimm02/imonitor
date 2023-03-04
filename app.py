from flask import Flask, render_template
from flask_cors import CORS
from operator import itemgetter
import os

from werkzeug.middleware.profiler import ProfilerMiddleware

app = Flask(__name__)
CORS(app)
app.secret_key = 'flash-secret'
app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[5], profile_dir='./profs')  #performance testing
#----------------------------------------------------------------------------------------------------------------#

from iMonitor.aws.aws import aws_bp
from iMonitor.azure.azure import azure_bp
from iMonitor.gcp.gcp import gcp_bp

#---- BLUEPRINTS ------------------------------------------------------------------------------------------------#
app.register_blueprint(aws_bp, url_prefix='/aws')
app.register_blueprint(azure_bp, url_prefix='/azure')
app.register_blueprint(gcp_bp, url_prefix='/gcp')

#---- INDEX ------------------------------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('landing.html')

#---- ERROR HANDLERS ------------------------------------------------------------------------------------------------#

# Page not found
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

# Internal server error
@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500

@app.route('/status')
def status():
    return 
    


if __name__ == "__main__":
    app.run(debug=True)
