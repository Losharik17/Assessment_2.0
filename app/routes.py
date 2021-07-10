import logging
import os
from datetime import datetime
from logging.handlers import SMTPHandler, RotatingFileHandler

from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm
from app.models import User

if __name__ == '__main__':
    app.run(debug=True)
