from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import cx_Oracle
from flask_login import LoginManager, UserMixin

class User(UserMixin):
    pass

def create_app():
	app = Flask(__name__)
	app.config['SECRET_KEY'] = 'sdojrie'
	cx_Oracle.init_oracle_client(lib_dir='../../instantclient_19_8')
	connection = connectDB()
	cursor = connection.cursor()
	
	from .views import views
	from .auth import auth
	from .project import project
	from .enterprise import enterprise

	app.register_blueprint(views, url_prefix = '/')
	app.register_blueprint(auth, url_prefix = '/')
	app.register_blueprint(project, url_prefix = '/')
	app.register_blueprint(enterprise, url_prefix = '/')

	login_manager = LoginManager()
	login_manager.login_view = 'auth.login'
	login_manager.login_message = "請先登入"
	login_manager.init_app(app)

	@login_manager.user_loader
	def user_loader(mid):
		# print(mid)
		user = User()
		user.id = mid
		cursor.prepare('SELECT MID,ACCOUNT,USERNAME,ROLE FROM USERACCOUNT WHERE MID = (:MID) ')
		cursor.execute(None, {'MID':mid})
		data = cursor.fetchone()
		user.mid = data[0]
		user.account = data[1]
		user.username = data[2]
		user.role = data[3]
		return user 

	return app

def connectDB():
	connection = cx_Oracle.connect('Group15','group15group15',cx_Oracle.makedsn('140.117.69.58',1521,'orcl'))
	# cursor = connection.cursor()
	return connection
