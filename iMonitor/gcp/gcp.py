import os
from flask import Blueprint, render_template
from flask import Flask, render_template, request, redirect, url_for, jsonify, current_app, flash

gcp_bp = Blueprint('gcp_bp', __name__,
                   template_folder= os.path.join(os.getcwd(), 'iMonitor','gcp','templates'),
                   static_folder='static', static_url_path='assets')
#----GCP OVERVIEW---------------------------------------------------------------------------------------------------#

@gcp_bp.route('/overview')
def gcp_overview():
    print('in overview')
    return render_template('gcp_overview.html')