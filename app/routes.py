from flask import render_template, flash, redirect, url_for, request
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

@app.route('/')
@app.route('/index')
def index():
    # form = PostForm()
    #user = User.query.filter_by(username=current_user.username).first()
    # if form.validate_on_submit():
    #     post = Post(body=form.post.data, author=current_user, topic_type="General")
    #     db.session.add(post)
    #     db.session.commit()
    #     flash('Your post is now live!')
    #     return redirect(url_for('index'))
    # page = request.args.get('page', 1, type=int)
    # posts = current_user.followed_posts().paginate(
    #     page, app.config['POSTS_PER_PAGE'], False)
    # next_url = url_for('index', page=posts.next_num) \
    #     if posts.has_next else None
    # prev_url = url_for('index', page=posts.prev_num) \
    #     if posts.has_prev else None
    return render_template('index.html', title='Home')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm(request.form)
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember_me = request.form['remember_me']

        if form.validate_on_submit():
            user = User.query.filter_by(username=username).first()
            if user is None or not user.check_password(password):
                flash('Invalid username or password')
                return redirect(url_for('login'))
            login_user(user, remember=remember_me)
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

    form = RegistrationForm(request.form)
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        password2 = request.form['password2']

        if form.validate_on_submit():
            user = User(username=username, email=email, admin=False)
            user.set_password(password=password)
            db.session.add(user)
            db.session.commit()
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()

    admin_form = AdminForm(request.form)
    users = User.query.filter(User.username!=username).all()
    choices = [('Please Select', 'Please Select')]
    for u in users:
        choices.append((u.username, u.username))
    admin_form.username.choices = choices

    if request.method == 'POST':
        username = request.form['username']

        if admin_form.validate_on_submit():
            username = User.query.filter_by(username=username).first()
            username.admin = True
            db.session.commit()
            flash("{} is now an admin".format(username.username))
            return redirect(url_for('user', username=current_user.username))

    return render_template('user.html', users=users, user=user, admin_form=admin_form)

from app.forms import EditProfileForm

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(request.form)

    if request.method == 'POST':
        username=request.form['username']
        about_me=request.form['about_me']

        if form.validate_on_submit():
            current_user.username = username
            current_user.about_me = about_me
            db.session.commit()
            flash('Your changes have been saved.')
            return redirect(url_for('edit_profile'))
        elif request.method == 'GET':
            username = current_user.username
            about_me = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)

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

@app.route('/add_movie', methods=['GET', 'POST'])
@login_required
def add_movie():

    add_form = CreateMovieForm(request.form)

    if request.method == 'POST':

        if "add" in request.form:
            title = request.form['title']
            genre = request.form['genre']

            if add_form.validate_on_submit():
                new_movie = Movie(title=title, genre=genre, votes=0)
                db.session.add(new_movie)
                db.session.commit()
                flash('Congratulations, you are now added a new movie')
                return redirect(url_for('add_movie'))


    movies = db.session.query(Movie).order_by(Movie.votes.desc()).from_self()
    movie_list = movies.all()
    genre_list = ['Please Select','Action','Comedy','Drama', 'Horror','Adventure']

    return render_template('add_movie.html', title='Add Movie', movie_list=movie_list, add_form=add_form, genre_list=genre_list)


@app.route('/delete_movie', methods=['GET', 'POST'])
@login_required
def delete_movie():

    form = DeleteMovieForm(request.form)

    if request.method == 'POST':

        if "delete" in request.form:
            title = request.form['title']

            if form.validate_on_submit():
                delete_movie = Movie.query.filter_by(title=title).first()
                db.session.delete(delete_movie)
                db.session.commit()
                flash('You successfully deleted the movie')
                return redirect(url_for('delete_movie'))

    movies = db.session.query(Movie).order_by(Movie.votes.desc()).from_self()
    movie_list = movies.all()

    return render_template('delete_movie.html', title='Delete Movie', movie_list=movie_list, form=form)


@app.route('/vote', methods=['GET', 'POST'])
@login_required
def vote():
    form = VoteForm(request.form)
    choices = [('Please Select', 'Please Select')]
    movies = Movie.query.all()
    for m in movies:
        choices.append((m.title, m.title))
    form.vote1.choices = choices
    form.vote2.choices = choices
    form.vote3.choices = choices
    form.vote4.choices = choices
    form.vote5.choices = choices
    if request.method == 'POST':
        vote1 = request.form['vote1']
        vote2 = request.form['vote2']
        vote3 = request.form['vote3']
        vote4 = request.form['vote4']
        vote5 = request.form['vote5']

        if form.validate_on_submit():

            username = current_user.username
            user = User.query.filter_by(username=username).first()

            if user.voted==True:
                movie1 = Movie.query.filter_by(title=user.movie_vote1).first()
                movie1.votes -= 1

                movie2 = Movie.query.filter_by(title=user.movie_vote2).first()
                movie2.votes -= 1

                movie3 = Movie.query.filter_by(title=user.movie_vote3).first()
                movie3.votes -= 1

                movie4 = Movie.query.filter_by(title=user.movie_vote4).first()
                movie4.votes -= 1

                movie5 = Movie.query.filter_by(title=user.movie_vote5).first()
                movie5.votes -= 1
                db.session.commit()

            movie1 = Movie.query.filter_by(title=vote1).first()
            movie1.votes += 1

            movie2 = Movie.query.filter_by(title=vote2).first()
            movie2.votes += 1

            movie3 = Movie.query.filter_by(title=vote3).first()
            movie3.votes += 1

            movie4 = Movie.query.filter_by(title=vote4).first()
            movie4.votes += 1

            movie5 = Movie.query.filter_by(title=vote5).first()
            movie5.votes += 1

            user.movie_vote1 = vote1
            user.movie_vote2 = vote2
            user.movie_vote3 = vote3
            user.movie_vote4 = vote4
            user.movie_vote5 = vote5
            user.last_vote = datetime.utcnow()
            db.session.commit()

            if user.voted == True:
                flash("Thank you, we have updated your votes")
            else:
                flash("Thank you your votes have been submitted")
                user.voted = True
                db.session.commit()
            return redirect(url_for('vote'))
    movies = db.session.query(Movie).order_by(Movie.votes.desc()).from_self()
    movie_list = movies.all()
    return render_template("vote.html", title="Vote", movie_list=movie_list, form=form)

@app.route('/leaderboard', methods=['GET', 'POST'])
def leaderboard():
    form = PostForm(request.form)
    if request.method == 'POST':
        post=request.form['post']

        if form.validate():
            new_post = Post(body=post, author=current_user, topic_type="leaderboard")
            db.session.add(new_post)
            db.session.commit()
            flash("Thank you for your comment")
            return redirect(url_for('leaderboard'))
        else:
            flash('Error')
    movies = db.session.query(Movie).order_by(Movie.votes.desc()).from_self()
    movie_list = movies.all()

    last_vote = db.session.query(User).order_by(User.last_vote.desc()).first()
    last_vote = last_vote.last_vote

    posts = Post.query.all()
    #page = request.args.get('page', 1, type=int)
    # posts = Post.query.order_by(Post.timestamp.desc()).paginate(
    #     page, app.config['POSTS_PER_PAGE'], False)
    # next_url = url_for('explore', page=posts.next_num) \
    #     if posts.has_next else None
    # prev_url = url_for('explore', page=posts.prev_num) \
    #     if posts.has_prev else None
    return render_template("leaderboard2.html", title="Leaderboard", form = form, movie_list=movie_list, posts=posts, last_vote=last_vote)

@app.route('/suggestions', methods=['GET', 'POST'])
@login_required
def suggestions():
    form = SuggestForm(request.form)

    if request.method == 'POST':
        post = request.form['post']

    if form.validate_on_submit():
        new_post = Post(body=post, author=current_user, topic_type="Suggestion")
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

@app.route('/user/<username>/popup')
@login_required
def user_popup(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user_popup.html', user=user)
