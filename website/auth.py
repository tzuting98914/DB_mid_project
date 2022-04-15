from flask import Blueprint, render_template, request, flash, redirect,url_for
from flask_login import login_user, logout_user, login_required, current_user
from website import connectDB, User
import re
auth = Blueprint('auth', __name__)
connection = connectDB()
cursor = connection.cursor()

@auth.route('/login', methods=['GET','POST'])
def login():
	# request得到的data
	if request.method == 'POST':
		account = request.form.get('account')
		password = request.form.get('password')
		
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
				return redirect(url_for('views.index'))
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

# 只要是註冊就是勞動檢查機構(role = 1)
@auth.route('/signup', methods=['GET','POST'])
def signup():
	if request.method == 'POST':
		account = request.form.get('account')
		username = request.form.get('username')
		password = request.form.get('password')

		if (len(account)<1 or len(username)<1 or len(password)<1):
			flash('不能有空值！', category = 'error')
		else:
			# 檢查是否註冊過
			cursor.execute("SELECT ACCOUNT FROM USERACCOUNT")
			exist_account = cursor.fetchall()
			account_list = []

			for i in exist_account:
				account_list.append(i[0])
				
			if(account in account_list):
				flash('此帳號已經註冊過！請登入')
				return redirect(url_for('auth.login'))
			else:
				
				# 抓出資料庫中最後一筆MID，加1
				cursor.execute("SELECT MID FROM USERACCOUNT WHERE ROWNUM =1 ORDER BY MID DESC")
				lastuser = cursor.fetchone()
				lasmid = lastuser[0]
				new_num = str(int(re.search('\d+',lasmid).group(0)) + 1)
				newmid = "A"+new_num.zfill(7)
				cursor.prepare("INSERT INTO USERACCOUNT VALUES (:account, :password, :username, 1, :newmid)")
				cursor.execute(None, {'account': account, 'password':password, 'username':username,'newmid':newmid})
				connection.commit()
				new_user = User()
				new_user.id = newmid
				login_user(new_user,remember = True)
				flash('註冊成功', category='success')
				return redirect(url_for('views.home'))
	return render_template("signup.html", user=current_user)
