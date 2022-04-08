from flask import Blueprint, render_template, request, flash
from website import connectDB

connection = connectDB()
cursor = connection.cursor()
project = Blueprint('project', __name__)

@project.route('/project')
def showproject():
	sql = 'SELECT * FROM POJECT NATURAL JOIN ENTERPRISE WHERE ROWNUM <= 10'
	
	cursor.execute(sql)
	
	allproject = cursor.fetchall()
	
	project_list = []
	count = 0
	for data in allproject:
		count = count+1
		project = {
			'序號':count,
            '工程名稱': data[2],
			'業主名稱': data[8]
        }
		project_list.append(project)
	# print(len(allEnterprise))
	return render_template("project.html",projectData = project_list)