from flask import Blueprint, render_template, request, flash, redirect,url_for
from flask_login import current_user,login_required
from website import connectDB
import re

connection = connectDB()
cursor = connection.cursor()

enterprise = Blueprint('enterprise', __name__)

def getIndustry():
	sql = 'SELECT DISTINCT * FROM INDUSTRY ORDER BY INDUSTRYNAME'
	cursor.execute(sql)
	industryData = cursor.fetchall()
	industry_list = []
	for data in industryData:
		industry = {
			'inId':data[0],
			'industryName':data[2]
		}
		industry_list.append(industry)
	return industry_list

def getEnterprise():
	# sql = 'SELECT * FROM ENTERPRISE NATURAL JOIN INDUSTRY WHERE ENTERPRISENO IS NOT NULL ORDER BY EID DESC'
	sql = 'SELECT * FROM ENTERPRISE NATURAL JOIN INDUSTRY ORDER BY EID DESC'
	cursor.execute(sql)
	allEnterprise = cursor.fetchall()
	return allEnterprise
	

def enterprise_to_list(TotalData):
	Enterprise_list = []
	count = 0
	for data in TotalData:
		count = count+1
		enterprise = {
			'count':count,
			'eid': data[1],
            'enterpriseNo': data[2],
            'enterpriseName': data[6],
			'capital': data[3],
			'principal': data[4],
			'address': data[5],
			'industryType': data[8]
        }
		Enterprise_list.append(enterprise)
	return Enterprise_list

def get_search_term(term):
	# 字串轉換成 %term% 格式
	if term!= None:
		search_term = '%' + term + '%'
	else:
		search_term = "%%"
	return search_term

@enterprise.route('/enterprise')
def showEnterprise():
	enterpriseData = enterprise_to_list(getEnterprise())
	industryData = getIndustry()
	# print(industryData)

	# print(len(enterpriseData))
	return render_template("enterprise.html",enterpriseData = enterpriseData,industryData = industryData, user=current_user)


@enterprise.route('/enterprise/search', methods=['GET','POST'])
def search():
	industryData = getIndustry()

	eId_search = get_search_term(request.form.get('eId_search'))
	eNo_search = get_search_term(request.form.get('eNo_search'))
	eName_search = get_search_term(request.form.get('eName_search'))
	eCap_search = request.form.get('eCap_search')
	eCap_search = int(eCap_search) if len(eCap_search) != 0 else 0
	ePr_search = get_search_term(request.form.get('ePr_search'))
	eAdd_search = get_search_term(request.form.get('eAdd_search'))
	inId_search = get_search_term(request.form.get('inName_search'))

	# 不搜尋資本額
	if eCap_search==0:
		sql = """SELECT *
				FROM ENTERPRISE NATURAL JOIN INDUSTRY 
				WHERE  
					EID LIKE (:eId_search) AND
					ENTERPRISENO LIKE (:eNo_search) AND
					PRINCIPAL LIKE (:ePr_search) AND
					ADDRESS LIKE (:eAdd_search) AND
					ENTERPRISENAME LIKE (:eName_search) AND
					INDUSTRYNAME LIKE (:inId_search) AND
					CAPITAL >= (:eCap_search)
				ORDER BY ENTERPRISE.EID FETCH FIRST 10 ROWS ONLY """
	# 搜尋資本額
	else:
		sql = """SELECT *
			FROM ENTERPRISE NATURAL JOIN INDUSTRY 
			WHERE  
				EID LIKE (:eId_search) AND
				ENTERPRISENO LIKE (:eNo_search) AND
				PRINCIPAL LIKE (:ePr_search) AND
				ADDRESS LIKE (:eAdd_search) AND
				ENTERPRISENAME LIKE (:eName_search) AND
				INDUSTRYNAME LIKE (:inId_search) AND
				CAPITAL = (:eCap_search)
			ORDER BY ENTERPRISE.EID FETCH FIRST 10 ROWS ONLY """
	# print(sql)
	cursor.prepare(sql)
	cursor.execute(None, {'eId_search': eId_search, 'eNo_search':eNo_search,'eName_search':eName_search, 'ePr_search': ePr_search,
						  'eAdd_search': eAdd_search,'inId_search':inId_search,'eCap_search':eCap_search})
	
	allEnterprise = cursor.fetchall()
	Enterprise_list = enterprise_to_list(allEnterprise)
	
	return render_template("enterprise.html",enterpriseData = Enterprise_list,industryData = industryData,user=current_user)
	# return render_template("enterprise.html",user=current_user)

@enterprise.route('/enterprise/update', methods=['GET','POST'])
def update():
	industryData = getIndustry()
	# 新增資料
	if (request.values.get('add')):
		# 系統生成新的eid
		cursor.execute('SELECT EID FROM ENTERPRISE WHERE ROWNUM =1 ORDER BY EID DESC')
		lastEnterprise = cursor.fetchone()
		lastEid = lastEnterprise[0]
		newEid = "E"+str(int(re.search('\d+',lastEid).group(0)) + 1).zfill(9)		
		# print(lastEid)
		if request.method == 'POST':
			# request得到的data
			new_eid = request.values.get('newEid')
			new_eNo = request.values.get('eNo')
			new_inId = request.values.get('inId')
			new_eName = request.values.get('eName')
			new_eCap = request.values.get('eCap')
			new_ePri = request.values.get('ePri')
			new_eAdd = request.values.get('eAddress')

			# 新增到資料庫中
			cursor.prepare("INSERT INTO ENTERPRISE VALUES (:new_eid, :new_eNo, :new_eCap, :new_ePri, :new_eAdd, :new_inId, :new_eName)")
			cursor.execute(None, {'new_eid':new_eid, 'new_eNo':new_eNo, 'new_eCap':new_eCap, 'new_ePri':new_ePri, 'new_eAdd':new_eAdd, 'new_inId':new_inId, 'new_eName':new_eName})
			connection.commit()
			flash('新增事業單位資料成功', category='success')
			return redirect(url_for('enterprise.showEnterprise'))
		return render_template("enterprise_new.html",newEid = newEid,industryData = industryData, user = current_user)
	# 修改完畢
	elif(request.values.get('update_finish')):
		eid = request.values.get('up_Eid')
		# request得到的data
		up_eNo = request.values.get('eNo')
		up_inId = request.values.get('inId')
		up_eName = request.values.get('eName')
		up_eCap = request.values.get('eCap')
		up_ePri = request.values.get('ePri')
		up_eAdd = request.values.get('eAddress')
		# print(up_eCap)
		cursor.prepare("""UPDATE ENTERPRISE 
						  SET 
						  	ENTERPRISENO=:up_eNo,
						  	CAPITAL=:up_eCap,
							PRINCIPAL=:up_ePri,
							ADDRESS=:up_eAdd,
							INID=:up_inId,
							ENTERPRISENAME=:up_eName
						  WHERE EID=:eid
						""")
		cursor.execute(None, {'eid':eid,'up_eNo':up_eNo,'up_inId':up_inId,'up_eName':up_eName,'up_eCap':up_eCap,'up_ePri':up_ePri,'up_eAdd':up_eAdd})
		connection.commit()
		flash('修改事業單位資料成功', category='success')
		return redirect(url_for('enterprise.showEnterprise'))
	# 刪除資料
	elif(request.values.get('delete')):
		eid = request.values.get('delete')
		cursor.prepare('DELETE FROM ENTERPRISE WHERE EID=:eid')
		cursor.execute(None, {'eid':eid})
		# print('delete'+eid)
		connection.commit()
		flash('刪除事業單位資料成功', category='success')
		return redirect(url_for('enterprise.showEnterprise'))
	# 編輯資料
	elif(request.values.get('edit')):
		eid = request.values.get('edit')
		# print(eid)
		cursor.prepare("SELECT * FROM ENTERPRISE NATURAL JOIN INDUSTRY WHERE EID =:eid")
		cursor.execute(None, {'eid':eid})
		connection.commit()
		update_enterprise = cursor.fetchone()
		Enterprise_list = list(update_enterprise)
		return render_template("enterprise_new.html",Enterprisedata = Enterprise_list,industryData = industryData, user = current_user)
	else:
		return redirect(url_for('enterprise.showEnterprise'))
	
