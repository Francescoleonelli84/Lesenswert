from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_admin import Admin
from flask_login import LoginManager
from flask_login import LoginManager
from os import path


# Create directory for file fields to use
##file_path = op.join(op.dirname(__file__), 'files')
#try:
   # os.mkdir(file_path)
#except OSError:
    #pass

db = SQLAlchemy()
DB_NAME = "blog.db"
app = Flask(__name__)
mail = Mail()





def create_app():
     app.config['TESTING'] = False
     app.config['SECRET_KEY'] = 'secretkey'
     app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/franc/OneDrive/Dokumente/Lesenswert/blog.db'
     app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
     app.config['MAIL_SERVER'] = "smtp.gmail.com"
     app.config['MAIL_PORT'] = 465
     app.config['MAIL_USE_SSL'] = True
     app.config['MAIL_USE_TLS'] = False
     app.config['MAIL_USERNAME'] = 'lesenswert23@gmail.com'
     app.config['MAIL_PASSWORD'] = 'bpaq uxsm ilkm lpry'
     app.config['MAIL_DEBUG'] = True
     app.config['EXPLAIN_TEMPLATE_LOADING'] = True
    ## config still not created
        #app.config.from_pyfile('config.py')
     login_manager = LoginManager()
     login_manager.init_app(app)
     mail.init_app(app)
     db.init_app(app)
     from .routes import routes
     #from .auth import auth

     app.register_blueprint(routes, url_prefix="/")
     #app.register_blueprint(auth, url_prefix="/")

     from .models import User, Blogpost

     create_database(app)

     login_manager = LoginManager()
     login_manager.login_view = "auth.login"
     login_manager.init_app(app)

     
     #  create admin view
     #admin.add_view(SecureView(Blogpost, db.session))



     @login_manager.user_loader
     def load_user(id):
         return User.query.get(int(id))

     return app




def create_database(app):
    if not path.exists("website/" + DB_NAME):
        with app.app_context():
            db.create_all()
        print("Created database!")