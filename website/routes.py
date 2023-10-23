from datetime import datetime
import os.path as op
from flask import Blueprint,  abort, render_template, request, redirect, session, url_for, flash
from flask_login import  login_required, logout_user
from flask_mail import  Message
from flask_admin import Admin, expose
from flask_admin.contrib.sqla import ModelView
from markupsafe import Markup
from .models import Blogpost, Comment, User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from . import db, mail, app
from flask_humanize import Humanize
from google_recaptcha import ReCaptcha


routes = Blueprint("routes", __name__)
admin = Admin(app)
humanize = Humanize(app)



# create class to protect admin view, overwrites is_accessible method from Class ModelView
class SecureView(ModelView):

    def is_accessible(self):
        if "logged_in" in session:
            return True
        else:
            abort(403)


class CommentView(ModelView):
    column_list = ('id', 'username', 'text', 'email',
                   'date_created', 'status', 'approved', 'post_id')

    def approve_comment(view, context, model, name):

        approve_url = url_for('.approve_view', id=model.id)
        html = '''
                    <form action="{approve_url}" method="POST">
                    <button type='submit'>
                    Approve </button>
                     </form
            '''.format(approve_url=approve_url)

        return Markup(html)

    column_formatters = {
        'approved': approve_comment
    }

    @expose('approve/<int:id>', methods=['POST'])
    def approve_view(self, id):
        comment = Comment.query.get(id)
        if comment:
            comment.status = "approved"
            comment.approved = True
            db.session.commit()
            msg = Message(
                'Comment Approved', sender=app.config.get('MAIL_USERNAME'), recipients=[comment.email])
            msg.body = 'Your comment has been approved! Thank you very much!\n\nFrancesco from Lesenswert'
            mail.send(msg)
            flash('Comment has been posted!', 'success')
        else:
            flash("Comment not found", "error")
        return redirect(url_for('.index_view'))


# create admin view
admin.add_view(SecureView(Blogpost, db.session))
admin.add_view(CommentView(Comment, db.session))


@routes.route('/contact', methods=["GET", "POST"])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        sender_mail = app.config.get('MAIL_USERNAME')
        recipients_mail = app.config.get('MAIL_RECIPIENT')
        msg = Message(subject=f"E-Mail da {name}", body=f"Name: {name}\nE-Mail: {email}\nMessaggio: {message}",
                      sender=sender_mail, recipients=[recipients_mail])
        mail.send(msg)
        flash('The message has been sent. I will get to you as soon as possible', 'success')
        return redirect('/contact')
    return render_template('contact.html')


@routes.route('/')
@routes.route("/index")
def index():
    posts = Blogpost.query.order_by(Blogpost.date_posted.desc()).all()
    return render_template('index.html', posts=posts)
   

@routes.route('/about')
def about():
    return render_template('about.html')


@routes.route('/login', methods=["GET", "POST"])
def admin_login():
    if request.method == 'POST':
        if request.form['username'] == app.config.get('ADMIN_USERNAME') and \
                request.form['pw'] == app.config.get('ADMIN_PW'):
            session['logged_in'] = True
            return redirect('/admin')
        else:
            return render_template('login.html', failed=True)
    return render_template('login.html')


@routes.route("/logout")
def admin_logout():
    session.clear()
    return redirect("/")


# secret page to add the post
@routes.route('/add')
@login_required
def add():
    return render_template('add.html')


@routes.route('/sign_in')
def prova():
    return render_template('sign_in.html')


@routes.route('/addpost', methods=['POST'])
def addpost():
    title = request.form['title']
    subtitle = request.form['subtitle']
    author = request.form["author"]
    content = request.form['content']
    post = Blogpost(title=title, subtitle=subtitle, author=author,
                    content=content, date_posted=datetime.now())
    db.session.add(post)
    db.session.commit()
    return redirect(url_for('index'))


@routes.route("/login", methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash("Logged in!", category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Password is incorrect.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


@routes.route("/sign_up", methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get("email")
        username = request.form.get("username")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        email_exists = User.query.filter_by(email=email).first()
        username_exists = User.query.filter_by(username=username).first()
        if email_exists:
            flash('Email is already in use.', category='error')
        elif username_exists:
            flash('Username is already in use.', category='error')
        elif password1 != password2:
            flash('Password don\'t match!', category='error')
        elif len(username) < 2:
            flash('Username is too short.', category='error')
        elif len(password1) < 6:
            flash('Password is too short.', category='error')
        elif len(email) < 4:
            flash("Email is invalid.", category='error')
        else:
            new_user = User(email=email, username=username, password=generate_password_hash(
                password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('User created!')
            return redirect(url_for('views.home'))
    return render_template("sign_up.html", user=current_user)


@routes.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("views.home"))


@routes.route('/post/<int:post_id>', methods=['POST', 'GET'])
def post(post_id):
    post = Blogpost.query.filter_by(id=post_id).one()
    date_posted = post.date_posted.strftime('%d %B, %Y')
    return render_template('post.html', post=post, date_posted=date_posted)


@app.route('/create-comment/<post_id>', methods=['POST'])
def create_comment(post_id):
    text = request.form.get('text')
    username = request.form.get('username')
    email = request.form.get('email')
   # date_posted = post.date_posted.strftime('%d %B, %Y')
    if not text:
        flash("Comment cannot be empty ", category='error')
    else:
        post = Blogpost.query.filter_by(id=post_id)

        if post:

            comment = Comment(username=username, text=text,
                                   email=email, post_id=post_id)
            db.session.add(comment)
            db.session.commit()
        flash("Thank you for posting! You comment is waiting for approval",
              category="warning")
    return redirect(url_for('routes.post', post_id=post_id))