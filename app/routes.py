from flask import render_template, flash, redirect, url_for, request
from app import app, login, db
from app.forms import (LoginForm, RegistrationForm, EditProfileForm,
                       NewPostForm)
from app.models import User, Post, PostComment
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from random import randrange
from datetime import datetime
import os

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def delete_file(filename):
    try:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    except:
        # flash(f'{filename} not found.')
        pass
    else:
        flash(f'{filename} delete.')

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = NewPostForm()
    posts = Post.query.all()[::-1]
    users = User.query.all()
    if form.validate_on_submit():
        userid = current_user.get_id()
        post = Post(body=form.postbody.data, timestamp=datetime.utcnow(),
                    user_id=userid)
        db.session.add(post)
        db.session.commit()
        flash('New post successful.')
        return redirect(url_for('index'))

    return render_template('index.html', title='Home',
                           posts=posts, users=users, form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(user_id=user.id)[:-100:-1]
    return render_template('user.html', user=user, posts=posts)

@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first_or_404()
    if current_user.id != user.id:
        current_user.follow(user)
        db.session.commit()
        flash(f'Now following {username}!')
    else:
        flash('You cannot follow yourself!')
    return redirect(request.referrer)

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first_or_404()
    if current_user.id != user.id:
        current_user.unfollow(user)
        db.session.commit()
        flash(f'Unfollowed {username}.')
    else:
        flash('You cannot unfollow yourself!')
    return redirect(request.referrer)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)

@app.route('/new_post', methods=['GET', 'POST'])
@login_required
def new_post():
    form = NewPostForm()
    if form.validate_on_submit():
        userid = current_user.get_id()
        post = Post(body=form.postbody.data, timestamp=datetime.utcnow(),
                    user_id=userid)
        if form.attachment.data:
            f = form.attachment.data
            name_append = ''.join([str(randrange(9)) for n in range(9)])
            filename = str(current_user.id) + '_' + name_append + '_' + secure_filename(f.filename)
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            post.attachment = filename
            flash(f'Uploaded {filename}.')
        db.session.add(post)
        db.session.commit()
        flash('New post successful.')
        return redirect(url_for('index'))
    return render_template('new_post.html', title='New Post',
                           form=form)

@app.route('/getpost/<post_id>', methods=['GET', 'POST'])
@login_required
def getpost(post_id):
    post = Post.query.get(post_id)
    comments = PostComment.query.filter_by(post_id=post.id)
    op = User.query.get(post.user_id)
    form = NewPostForm()
    if form.validate_on_submit():
        userid = current_user.get_id()
        comment = PostComment(body=form.postbody.data, timestamp=datetime.utcnow(),
                              user_id=userid, post_id=post.id)
        db.session.add(comment)
        db.session.commit()
        flash('Comment posted.')
        return redirect(request.referrer)
    else:
        return render_template('getpost.html', title=f"{post.username}'s post.",
                               form=form, post=post, comments=comments)

@app.route('/delete_post/<post_id>', methods=['GET'])
@login_required
def delete_post(post_id):
    post = Post.query.get(post_id)
    if not post:
        return 404
    if current_user.admin == 1 or current_user.username == post.username:
        if post.attachment:
            delete_file(post.attachment)
        db.session.delete(post)
        db.session.commit()
        flash(f'Post {post_id} deleted.')
        return redirect(url_for('index'))
    else:
        flash('You do not have permission to do that.')
        return redirect(request.referrer)


@app.route('/admin', methods=['GET'])
@login_required
def admin():
    if current_user.admin == 1:
        users = User.query.all()
        return render_template('admin.html', title='Admin Panel',
                               users=users)
    else:
        flash('You do not have permission to do that.')
        return redirect(request.referrer)


@app.route('/delete_user/<user_id>', methods=['GET'])
@login_required
def delete_user(user_id):
    u = User.query.get(user_id)
    if not u:
        return 404
    elif u.admin == 1:
        flash('Cannot delete admin.')
        return redirect(request.referrer)
    elif current_user.admin == 1:
        u_posts = Post.query.filter_by(user_id=user_id)
        if u_posts:
            for post in u_posts:
                if post.attachment:
                    delete_file(post.attachment)
                db.session.delete(post)
        db.session.delete(u)
        db.session.commit()
        flash('User deleted.')
        return redirect(request.referrer)
    else:
        flash('You do not have permission to do that.')
        return redirect(request.referrer)
