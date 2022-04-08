from flask import Blueprint, render_template, request, flash
from flask_login import current_user
from website import connectDB

connection = connectDB()
cursor = connection.cursor()

enterprise = Blueprint('enterprise', __name__)

@enterprise.route('/enterprise')
def showEnterprise():
	
	sql = 'SELECT * FROM ENTERPRISE NATURAL JOIN INDUSTRY WHERE ENTERPRISENO IS NOT NULL AND ROWNUM <= 10'
	
	cursor.execute(sql)
	allEnterprise = cursor.fetchall()
	
	Enterprise_list = []
	count = 0
	for data in allEnterprise:
		count = count+1
		enterprise = {
			'序號':count,
			'事業單位編號': data[1],
            '統一編號': data[2],
            '公司名稱': data[6],
			'資本額': data[3],
			'代表人': data[4],
			'地址': data[5],
			'行業別': data[8]
        }
		Enterprise_list.append(enterprise)
	# print(len(allEnterprise))
	return render_template("enterprise.html",enterpriseData = Enterprise_list, user=current_user)

@enterprise.route('/enterprise/update', methods=['GET','POST'])
def update():
	# request得到的data
	eid = request.values.get('eid')
	# print(eid)
	# sql = 'UPDATE ENTERPRISE SET '
	# cursor.execute(sql)

	return render_template("home.html", user=current_user)

@enterprise.route('/enterprise/delect')
def delect():
	return render_template("home.html", user=current_user)