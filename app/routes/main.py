from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Página inicial do site"""
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin.dashboard'))
        elif current_user.is_barbeiro():
            return redirect(url_for('barbeiro.dashboard'))
        else:
            return redirect(url_for('cliente.dashboard'))
    
    return render_template('index.html', title='Safa Barbeiros CIASC')