import os
from flask import Blueprint, render_template
from flask import Flask, render_template, request, redirect, url_for, jsonify, current_app, flash

azure_bp = Blueprint('azure_bp', __name__,
                   template_folder= os.path.join(os.getcwd(), 'iMonitor','azure','templates'),
                   static_folder='static', static_url_path='assets')

#----AZURE OVERVIEW---------------------------------------------------------------------------------------------------#

@azure_bp.route('/overview')
def azure_overview():
    return render_template('azure_overview.html')
