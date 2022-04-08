from flask import Blueprint, render_template, request, flash, redirect,url_for
from flask_login import login_user, logout_user, login_required, current_user
from website import connectDB, User
auth = Blueprint('auth', __name__)
connection = connectDB()



@auth.route('/login', methods=['GET','POST'])
def login():
	# request得到的data
	if request.method == 'POST':
		account = request.form.get('account')
		password = request.form.get('password')
		cursor = connection.cursor()
		cursor.prepare("SELECT * FROM USERACCOUNT WHERE ACCOUNT = (:account)")
		cursor.execute(None, {'account': account})
		userdata =cursor.fetchone()
		# print(userdata)
		if userdata:
			if(password == userdata[1]):
				user = User()
				user.id = userdata[4]
				# print(userdata[4])
				login_user(user,remember = True)
				flash('登入成功', category='success')
				return redirect(url_for('views.home'))
			else:
				flash('密碼錯誤', category='error')
		else:
			flash('沒有這個帳號唷', category='error')
	# print(data)
	return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/signup', methods=['GET','POST'])
def signup():
	if request.method == 'POST':
		account = request.form.get('account')
		username = request.form.get('username')
		password = request.form.get('password')
		if len(account)<2:
			flash('Too short', category = 'error')
		else:
			cursor = connection.cursor()
			cursor.prepare("INSERT INTO USERACCOUNT VALUES (:account, :password, :username, 0, 'A0000004')")
			cursor.execute(None, {'account': account, 'password':password, 'username':username})
			connection.commit()
			new_user = User()
			new_user.id = 'A0000004'
			login_user(new_user,remember = True)
			flash('註冊成功', category='success')
			return redirect(url_for('views.home'))
	return render_template("signup.html", user=current_user)
