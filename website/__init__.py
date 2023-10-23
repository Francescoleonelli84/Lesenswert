from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_admin import Admin
from flask_login import LoginManager
from flask_login import LoginManager
from os import path
from config import MAIL_SERVER, MAIL_USERNAME, MAIL_PASSWORD

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
     app.config.from_object('config')
     app.config['TESTING'] = False
     app.config.get('SQLALCHEMY_DATABASE_URI')
     app.config.get('SECRET_KEY')
     app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
     app.config['MAIL_PORT'] = 465
     app.config['MAIL_USE_SSL'] = True
     app.config['MAIL_USE_TLS'] = False
    #! ->! https://myaccount.google.com/apppasswords 
 #    app.config['MAIL_RECIPIENT'] = 'francesco.leonelli84@libero.it'
     app.config.get('SECRET_KEY')
     app.config.get('MAIL_SERVER')
     app.config.get('MAIL_USERNAME')
     app.config.get('MAIL_PASSWORD')
     app.config.get('MAIL_RECIPIENT')
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