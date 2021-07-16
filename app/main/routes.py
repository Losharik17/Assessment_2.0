from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, jsonify, current_app
from flask_login import current_user, login_required
from app import db
from app.main.forms import EditProfileForm, EmptyForm, GradeForm, UserForm, TableForm
from app.models import User, Expert, Grade, Viewer, Admin
from app.main import bp


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/T-Park', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('main.html')


@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first()
    return render_template('user.html', user=user)


@bp.route('/expert/<expert_id>', methods=['GET', 'POST'])
@login_required
def expert(expert_id):
    expert = Expert.query.filter_by(expert_id=expert_id).first()
    form = UserForm()
    if form.validate_on_submit():
        user = User.query.filter_by(user_id=form.user_id.data).first()
        if user is None:
            flash('En')
            return redirect(url_for('main.expert'))
        return redirect(url_for('main.expert_grade'))
    return render_template('expert.html', form=form, expert=expert)


@bp.route('/expert/<expert_id>/<user_id>', methods=['GET', 'POST'])
@login_required
def expert_grade(expert_id, user_id):
    expert = Expert.query.filter_by(expert_id=expert_id).first()
    form = GradeForm()
    if form.validate_on_submit():
        grade = Grade(user_id=user_id, expert_id=current_user.id.data)
        parameters = [form.parameter_0.data, form.parameter_1.data, form.parameter_2.data, form.parameter_3.data, form.parameter_4.data]
        grade.set_points(parameters)
        db.session.add(grade)
        grade.user.sum_grades()
        expert.quantity_grade()
        db.session.commit()

        flash('Text')
        return redirect(url_for('main.expert'))
    return render_template('expert_grade.html', expert=expert, form=form)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved')
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)


@bp.route('/viewer/<viewer_id>', methods=['GET', 'POST'])
@login_required
def viewer(viewer_id):
    viewer = Viewer.query.filter_by(viewer_id=viewer_id).first()
    return render_template('viewer.html', viever=viewer)


@bp.route('/admin/<admin_id>', methods=['GET', 'POST'])
@login_required
def admin(admin_id):
    admin = Admin.query.filter_by(admin_id=admin_id).first()
    return render_template('admin.html', admin=admin)


@bp.route('/admin_table', methods=['GET', 'POST'])
@login_required
def admin_table(admin_id):
    admin = Admin.query.filter_by(admin_id=admin_id).first()
    page = request.args.get('page', 1, type=int)
    users = User.query.all().paginate(page, current_app.config['USER_PER_PAGE'], False)
    next_url = url_for('main.admin_table', page=users.next_num) \
        if users.has_next else None
    prev_url = url_for('main.admin_table', page=users.prev_num) \
        if users.has_prev else None
    return render_template('admin_table.html', title='Rating', admin=admin,
                           users=users.items, next_url=next_url,
                           prev_url=prev_url)
