from datetime import datetime
import flask_login
import pdb
import os
import os.path as op
from flask import Flask, abort, render_template, request, redirect, session, url_for, flash
from flask_login import LoginManager, UserMixin, login_required, logout_user
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_admin import Admin, form
from flask_admin.contrib.sqla import ModelView
from markupsafe import Markup



app = Flask(__name__, template_folder='./templates',
            static_folder='./static')

app.config.from_pyfile('config.py')

app.config['TESTING'] = False
app.config['SECRET_KEY'] = 'secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/franc/OneDrive/Dokumente/Lesenswert/blog.db'
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

    
class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(64))
    path = db.Column(db.Unicode(128))



db.create_all()



# Create directory for file fields to use
file_path = op.join(op.dirname(__file__), 'files')
try:
    os.mkdir(file_path)
except OSError:
    pass


# create class to protect admin view, overwrites is_accessible method from Class ModelView
class SecureView(ModelView):
    def is_accessible(self):
        if "logged_in" in session:
            return True
        else:
            abort(403)


class ImageView(ModelView):
    def _list_thumbnail(view, context, model, name):
        if not model.path:
            return ''
        return Markup('<img src="%s">' % url_for('static',
                                                 filename=form.thumbgen_filename(model.path)))

    column_formatters = {
        
        'path': _list_thumbnail
    }

    # Alternative way to contribute field is to override it completely.
    # In this case, Flask-Admin won't attempt to merge various parameters for the field.
    form_extra_fields = {
        'path': form.ImageUploadField('Image',
                                      base_path=file_path,
                                      thumbnail_size=(100, 100, True))
    }




#  create model for admin view
admin.add_view(SecureView(Blogpost, db.session))
# create model for image view
admin.add_view(ImageView(Image, db.session))


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


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and \
                request.form['pw'] == 'secret':
            session['logged_in'] = True 
            return redirect('/admin')
        else:
            return render_template('login.html', failed = True)
    return render_template('login.html')



#secret page to add the post
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
