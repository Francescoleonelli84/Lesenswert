from datetime import datetime
import flask_login
import pdb
from flask import Flask, abort, render_template, request, redirect, session, url_for, flash
from flask_login import LoginManager, UserMixin, login_required, logout_user
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView


app = Flask(__name__, template_folder='../templates',
            static_folder='../static')


app.config['TESTING'] = False
app.config['SECRET_KEY'] = 'secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/franc/OneDrive - HWR Berlin/Lesenswert/blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = "smtp.gmail.com"
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USERNAME'] = 'username'
app.config['MAIL_PASSWORD'] = 'password'
app.config['MAIL_DEBUG'] = True
app.config['EXPLAIN_TEMPLATE_LOADING'] = True

db = SQLAlchemy(app)
mail = Mail(app)
admin = Admin(app)


login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin):
    pass


class Blogpost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    subtitle = db.Column(db.String(50))
    author = db.Column(db.String(20))
    date_posted = db.Column(db.DateTime)
    content = db.Column(db.Text)


db.create_all()


# create class to protect admin view, overwrites is_accessible method from Class ModelView
class SecureView(ModelView):
    def is_accessible(self):
        if "logged_in" in session:
            return True
        else:
            abort(403)


#  create model for admin view
admin.add_view(SecureView(Blogpost, db.session))


@app.route('/contact', methods=["POST", "GET"])
def contact():

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        phone = request.form.get('phone')
        msg = Message(subject=f"E-Mail da {name}", body=f"Name: {name}\nE-Mail: {email}\nTelefono: {phone}\nMessaggio: {message}",
                      sender="francesco.leonelli84@gmail.com", recipients=['francesco.leonelli84@gmail.com'])

        mail.send(msg)

        return render_template('contact.html', success=True)

    return render_template('contact.html')


@app.route('/')
def index():
    posts = Blogpost.query.order_by(Blogpost.date_posted.desc()).all()
    return render_template('index.html', posts=posts)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/post/<int:post_id>', methods=['POST', 'GET'])
def post(post_id):
    post = Blogpost.query.filter_by(id=post_id).one()
    date_posted = post.date_posted.strftime('%d %B, %Y')
    return render_template('post.html', post=post, date_posted=date_posted)


@login_manager.user_loader
def user_loader(username):
    # if username not in users:
    # return
    user = User()
    user.id = username
    return user


# @login_manager.request_loader
# def request_loader(request):
#     username = request.form.get("username")
#    # if username not in users:
#         #return
#     user = User()
#     user.id = username
#     #user.is_authenticated = request.form["pw"] == users[username]["pw"]
#     return user


@app.route('/login', methods=["POST", "GET"])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or \
                request.form['pw'] != 'secret':
            error = 'Invalid credentials. You should actually not be here ;)'
        else:
            flash('You were successfully logged in')
            session['logged_in'] = True
            return redirect("/admin")
    return render_template('login.html', error=error)


@app.route('/add')
@login_required
def add():
    return render_template('add.html')


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route('/prova')
def prova():
    return render_template('prova.html')


@app.route('/addpost', methods=['POST'])
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


if __name__ == "__main__":
    app.run(debug=True)
