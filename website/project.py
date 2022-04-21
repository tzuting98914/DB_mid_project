from flask import Blueprint, render_template, request, flash, redirect,url_for
from website import connectDB
from flask_login import current_user,login_required
import re
from website import enterprise
from website.enterprise import getEnterprise, get_search_term,enterprise_to_list,checkLength

connection = connectDB()
cursor = connection.cursor()
project = Blueprint('project', __name__)

def getProject(data):
	# sql = 'SELECT * FROM POJECT NATURAL JOIN ENTERPRISE ORDER BY POJECT.PID'
	# cursor.execute(sql)
	# allproject = cursor.fetchall()
	
	project_list = []
	count = 0
	for data in data:
		count = count+1
		project = {
			'count':count,
			'eid':data[0],
			'pid':data[1],
            'projectname': data[2],
			'enterpriseNo': data[3],
			'capital': data[4],
			'principal': data[5],
			'address': data[6],
			'inid': data[7],
			'enterpriseName': data[8]
        }
		project_list.append(project)
	return project_list


@project.route('/project')
def showproject():
	sql = 'SELECT * FROM POJECT NATURAL JOIN ENTERPRISE ORDER BY POJECT.PID DESC'
	cursor.execute(sql)
	allProject = cursor.fetchall()
	projectData = getProject(allProject)
	enterpriseData = enterprise_to_list(getEnterprise())
	
	return render_template("project.html",projectData = projectData,enterpriseData = enterpriseData, user = current_user)

@project.route('/project/search', methods=['GET','POST'])
def search():
	enterpriseData = getEnterprise()
	pId_search = get_search_term(request.form.get('pId_search'))
	pName_search = get_search_term(request.form.get('pName_search'))
	eId_search = get_search_term(request.form.get('eId_search'))

	sql = """SELECT * 
			 FROM POJECT NATURAL JOIN ENTERPRISE
			 WHERE 
			 	PID LIKE (:pId_search) AND
				PROJECTNAME LIKE (:pName_search) AND
				EID LIKE (:eId_search) 
				ORDER BY POJECT.PID
			 """
	cursor.prepare(sql)
	cursor.execute(None, {'pId_search':pId_search, 'pName_search':pName_search, 'eId_search':eId_search})
	
	allProject = cursor.fetchall()
	projectData = getProject(allProject)

	return render_template("project.html",projectData = projectData, enterpriseData = enterpriseData, user = current_user)


@project.route('/project/update', methods=['GET','POST'])
def update():
	EnterpriseData = enterprise_to_list(getEnterprise())
	# 新增資料
	if (request.values.get('add')):
		# 系統生成新的eid
		cursor.execute('SELECT PID FROM POJECT WHERE ROWNUM =1 ORDER BY PID DESC')
		lastProject = cursor.fetchone()
		lastPid = lastProject[0]
		
		newPid = "P"+str(int(re.search('\d+',lastPid).group(0)) + 1).zfill(9)	
		
		# print(lastEid)
		if request.method == 'POST':
			# request得到的data
			new_pid = request.values.get('newPid')
			new_pName = request.values.get('pName')
			new_eid = request.values.get('eid')
			if(checkLength(new_pName)):
				# 新增到資料庫中
				cursor.prepare("INSERT INTO POJECT VALUES (:new_pid, :new_pName, :new_eid)")
				cursor.execute(None, {'new_pid':new_pid, 'new_pName':new_pName, 'new_eid':new_eid})
				connection.commit()
				
				flash('新增工程資料成功', category='success')
				return redirect(url_for('project.showproject'))
			else:
				flash('輸入失敗！！！輸入內容超過範圍', category = 'error')
		return render_template("project_new.html",newPid = newPid,EnterpriseData = EnterpriseData, user = current_user)
	# 修改完畢
	elif(request.values.get('update_finish')):
		pid = request.values.get('up_Pid')
		# request得到的data
		up_pName = request.values.get('pName')
		up_eid = request.values.get('eid')
		if(checkLength(up_pName)):
			cursor.prepare("""UPDATE POJECT 
							SET 
								PROJECTNAME=:up_pName,
								EID=:up_eid
							WHERE PID=:pid
							""")
			cursor.execute(None, {'up_pName':up_pName,'up_eid':up_eid,'pid':pid})
			connection.commit()

			flash('修改工程資料成功', category='success')
		else:
			flash('輸入失敗！！！輸入內容超過範圍', category = 'error')
		return redirect(url_for('project.showproject'))
	# 刪除資料
	elif(request.values.get('delete')):
		pid = request.values.get('delete')
		cursor.prepare('DELETE FROM POJECT WHERE PID=:pid')
		cursor.execute(None, {'pid':pid})
		connection.commit()

		flash('刪除工程資料成功', category='success')
		return redirect(url_for('project.showproject'))
	# 編輯資料
	elif(request.values.get('edit')):
		pid = request.values.get('edit')
		cursor.prepare("SELECT * FROM POJECT NATURAL JOIN ENTERPRISE WHERE PID =:pid")
		cursor.execute(None, {'pid':pid})
		connection.commit()
		update_project = cursor.fetchone()
		Project_list = list(update_project)

		return render_template("project_new.html",ProjectData = Project_list,EnterpriseData = EnterpriseData, user = current_user)
	else:
		return redirect(url_for('project.showproject'))