from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm
from flask_login import current_user, login_user
from app.models import User, Movie
from flask_login import logout_user
from flask_login import login_required
from flask import request
from werkzeug.urls import url_parse
from app import db
from app.forms import RegistrationForm, CreateMovieForm, VoteForm, DeleteMovieForm, SuggestForm
from datetime import datetime
from app.forms import PostForm, AdminForm
from app.models import Post
from app.forms import ResetPasswordRequestForm
from app.email import send_password_reset_email

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    user = User.query.filter_by(username=current_user.username).first()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user, topic_type="General")
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title='Home', form=form,
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url, user=user)

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
        user = User(username=form.username.data, email=form.email.data, admin=False)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None

    admin_form = AdminForm()
    users = User.query.filter(User.username!=username).all()
    choices = [('Please Select', 'Please Select')]
    for u in users:
        choices.append((u.username, u.username))

    admin_form.username.choices = choices

    if admin_form.validate_on_submit():
        user = User.query.filter_by(username=admin_form.username.data).first()
        user.admin = True
        db.session.commit()
        flash("User is now an admin")
        return redirect(url_for('user'))

    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url, admin_form=admin_form)

from app.forms import EditProfileForm

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
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

@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('user', username=username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('user', username=username))

@app.route('/explore')
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template("index.html", title='Explore', posts=posts.items,
                          next_url=next_url, prev_url=prev_url)

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)

from app.forms import ResetPasswordForm

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

@app.route('/add_delete_movie', methods=['GET', 'POST'])
@login_required
def add_delete_movie():
    Add_form = CreateMovieForm()
    if Add_form.validate_on_submit():
        new_movie = Movie(title=Add_form.title.data, genre=Add_form.genre.data, votes=0)
        db.session.add(new_movie)
        db.session.commit()
        flash('Congratulations, you are now added a new movie')
        return redirect(url_for('add_delete_movie'))

    Delete_form = DeleteMovieForm()
    movies = Movie.query.all()
    choices = [('Please Select', 'Please Select')]
    for m in movies:
        choices.append((m.title, m.title))
    Delete_form.title.choices = choices

    if Delete_form.validate_on_submit():
        delete_movie = Movie.query.filter_by(title=Delete_form.title.data).first()
        db.session.delete(delete_movie)
        db.session.commit()
        flash('You successfully deleted the movie')
        return redirect(url_for('add_delete_movie'))

    movies = db.session.query(Movie).order_by(Movie.votes.desc()).from_self()
    movie_list = movies.all()
    return render_template('add_delete_movie.html', title='Add Movie', title2='Delete Movie', movie_list=movie_list, add_form=Add_form, delete_form=Delete_form)

@app.route('/vote', methods=['GET', 'POST'])
@login_required
def vote():
    form = VoteForm()
    choices = [('Please Select', 'Please Select')]
    movies = Movie.query.all()
    for m in movies:
        choices.append((m.title, m.title))
    form.vote1.choices = choices
    form.vote2.choices = choices
    form.vote3.choices = choices
    form.vote4.choices = choices
    form.vote5.choices = choices
    if form.validate_on_submit():
        movie1 = Movie.query.filter_by(title=form.vote1.data).first()
        movie1.votes += 1
        db.session.commit()

        movie2 = Movie.query.filter_by(title=form.vote2.data).first()
        movie2.votes += 1
        db.session.commit()

        movie3 = Movie.query.filter_by(title=form.vote3.data).first()
        movie3.votes += 1
        db.session.commit()

        movie4 = Movie.query.filter_by(title=form.vote4.data).first()
        movie4.votes += 1
        db.session.commit()

        movie5 = Movie.query.filter_by(title=form.vote5.data).first()
        movie5.votes += 1
        db.session.commit()

        username = current_user.username
        user = User.query.filter_by(username=username).first()
        user.voted = True
        db.session.commit()

        user.movie_vote1 = form.vote1.data
        user.movie_vote2 = form.vote2.data
        user.movie_vote3 = form.vote3.data
        user.movie_vote4 = form.vote4.data
        user.movie_vote5 = form.vote5.data
        db.session.commit()

        flash("Thank you your votes have been submitted")
        return redirect(url_for('vote'))
    movies = db.session.query(Movie).order_by(Movie.votes.desc()).from_self()
    movie_list = movies.all()
    return render_template("vote.html", title="Vote", movie_list=movie_list, form=form)

@app.route('/leaderboard', methods=['GET', 'POST'])
def leaderboard():
    form = PostForm()
    if request.method == 'POST':
        post=request.form['post']

        if form.validate_on_submit():
            new_post = Post(body=post, author=current_user, topic_type="leaderboard")
            db.session.add(new_post)
            db.session.commit()
            flash("Thank you for your comment")
            return redirect(url_for('leaderboard'))
        else:
            flash('Error')
    movies = db.session.query(Movie).order_by(Movie.votes.desc()).from_self()
    movie_list = movies.all()
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template("leaderboard2.html", title="Leaderboard", form = form, movie_list=movie_list, posts=posts.items, next_url=next_url, prev_url=prev_url)

@app.route('/suggestions', methods=['GET', 'POST'])
@login_required
def suggestions():
    form = SuggestForm()
    if form.validate_on_submit():
        new_post = Post(body=form.post.data, author=current_user, topic_type="Suggestion")
        db.session.add(new_post)
        db.session.commit()
        flash("Thank you for your suggestion")
        return redirect(url_for('suggestions'))
    page = request.args.get('page', 1, type=int)
    posts = db.session.query(Post).filter_by(topic_type="Suggestion").order_by(Post.timestamp.desc()).from_self()
    ##posts = Post.query.filter_by(topic_type="Suggestion").order_by(Post.timestamp.desc()).paginate(
    ##    page, app.config['POSTS_PER_PAGE'], False)
    ##osts = posts.filter_by(topic_type="Suggestion")
    return render_template("suggestions.html", title="suggestions", form=form, posts=posts)
