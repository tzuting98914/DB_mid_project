from flask import Blueprint, render_template, request, flash
from flask_login import current_user,login_required
from website import connectDB

connection = connectDB()
cursor = connection.cursor()

enterprise = Blueprint('enterprise', __name__)

def getIndustry():
	sql = 'SELECT DISTINCT * FROM INDUSTRY ORDER BY CATEGORY'
	cursor.execute(sql)
	industryData = cursor.fetchall()
	industry_list = []
	for data in industryData:
		industry = {
			'iid':data[0],
			'industryName':data[2]
		}
		industry_list.append(industry)
	return industry_list

def getEnterprise():
	sql = 'SELECT * FROM ENTERPRISE NATURAL JOIN INDUSTRY WHERE ENTERPRISENO IS NOT NULL'
	
	cursor.execute(sql)
	allEnterprise = cursor.fetchall()
	# print(current_user.role)
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
	return Enterprise_list


@enterprise.route('/enterprise')
def showEnterprise():
	enterpriseData = getEnterprise()
	industryData = getIndustry()
	# print(industryData)

	print(len(enterpriseData))
	return render_template("enterprise.html",enterpriseData = enterpriseData[0:10],industryData = industryData, user=current_user)


@enterprise.route('/enterprise/search', methods=['GET','POST'])
def search():
	eId_search = request.form.get('eId_search')
	eNo_search = request.form.get('eNo_search')
	eName_search = request.form.get('eName_search')
	eCap_search = request.form.get('eCap_search')
	ePr_search = request.form.get('ePr_search')
	eAdd_search = request.form.get('eAdd_search')




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

@enterprise.route('/enterprise/new', methods=['GET','POST'])
@login_required
def new():
	# request得到的data
	pid = request.values.get('pid')
	# print(eid)
	# sql = 'UPDATE ENTERPRISE SET '
	# cursor.execute(sql)
	return render_template("enterprise_new.html", user = current_user)