from flask import render_template, redirect, url_for
from app import db
from app.errors import bp


@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500


@bp.app_errorhandler(403)
def page_not_found(error):
    return redirect(url_for('main.index'))