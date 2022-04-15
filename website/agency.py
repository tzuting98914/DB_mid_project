from flask import Blueprint, render_template, request, flash, redirect, url_for
import cx_Oracle
import random, string
from datetime import datetime
from website import connectDB
from flask_login import current_user,login_required

connection = connectDB()
cursor = connection.cursor()
agency = Blueprint("agency",__name__)

## Oracle 連線
# cx_Oracle.init_oracle_client(lib_dir="C:/oracle/instantclient_21_3") # init Oracle instant client 位置
# connection = cx_Oracle.connect('Group15', 'group15group15', cx_Oracle.makedsn('140.117.69.58', 1521, 'orcl')) # 連線資訊
# cursor = connection.cursor()


# agency
@agency.route('/agency', methods=['GET', 'POST'])
def Agency():
    data_agencyName = In_agencyName()

    # 資料POST
    if request.method=='POST':
        # 搜尋
        if 'search' in request.values:
            agencyName_search = request.values.get("agencyName_search")
            phone_search = request.values.get("phone_search")
            address_search = request.values.get("address_search")
            area_search = request.values.get("area_search")
            url_search = request.values.get("url_search")

            agencyName_search = ('%' + agencyName_search+ '%') if agencyName_search != None else "%%"
            phone_search = ('%' + phone_search+ '%') if phone_search != None else "%%"
            address_search = ('%' + address_search+ '%') if address_search != None else "%%"
            area_search = ('%' + area_search+ '%') if area_search != None else "%%"
            url_search = ('%' + url_search+ '%') if url_search != None else "%%"

            sql = """
                    SELECT * 
                    FROM LABORAGENCY
                    WHERE 
                        AGENCYNAME LIKE : agencyName_search AND
                        PHONE LIKE : phone_search AND
                        ADDRESS LIKE : address_search AND
                        AREA LIKE : area_search AND
                        URL LIKE : url_search
                    ORDER BY AGENCYNAME ASC
                    """

            cursor.execute(sql,{'agencyName_search':agencyName_search,
                                'phone_search':phone_search,
                                'address_search':address_search,
                                'area_search':area_search,
                                'url_search':url_search})

            agency_row = cursor.fetchall()
            agency_data = []
            for i in agency_row:
                agency = {
                    'agencyName': i[0],
                    'phone': i[1],
                    'address': i[2],
                    'area': i[3],
                    'url': i[4]
                }
                agency_data.append(agency)

            
            return render_template('agency.html', agency_data=agency_data,
                                                    data_agencyName=data_agencyName, 
                                                    user=current_user)
        # 刪除資料
        if 'delete' in request.values:            
            agencyName = request.values.get('delete')
            print("delete", agencyName)
            
            if('A' in agencyName):
                cursor.prepare('DELETE FROM LABORAGENCY WHERE AGENCYNAME = :agencyName ')
                cursor.execute(None, {'agencyName': agencyName})
                connection.commit() # 把這個刪掉
                return redirect(url_for('agency.Agency'))

            else:
                flash('正式的資料，沒辦法刪除喔', category='error')
                return redirect(url_for('agency.Agency'))

        # 修改資料
        if 'edit' in request.values:
            agencyName = request.values.get('edit')                        
            return redirect(url_for('agency.viewAgency',agencyName=agencyName))
    


    # 列出全部
    else:
        sql = 'SELECT * FROM LABORAGENCY ORDER BY AGENCYNAME ASC'
        cursor.execute(sql)
        agency_row = cursor.fetchall()
        agency_data = []
        for i in agency_row:
            agency = {
                'agencyName': i[0],
                    'phone': i[1],
                    'address': i[2],
                    'area': i[3],
                    'url': i[4]
            }
            agency_data.append(agency)

        
        return render_template('agency.html', agency_data=agency_data,
                                                data_agencyName=data_agencyName, 
                                                user=current_user)



# 新增agency基本資訊
@agency.route('/viewAgency', methods=['GET', 'POST'])
@login_required
def viewAgency():
    data_agencyName = In_agencyName()

    # 新增industry資料
    if request.method == 'POST':
        agencyName = request.values.get("agencyName")
        phone = request.values.get("phone")
        address = request.values.get("address")
        area = request.values.get("area")
        url = request.values.get("url")

        # 新增職災資訊
        if request.form['submitBtn'] == "add":
            # 確認資料庫中id不重複
            cursor.prepare('SELECT * FROM LABORAGENCY WHERE AGENCYNAME = :agencyName')
            data = ""
            while ( data != None): 
                # number = str(random.randrange( 100000000, 999999999))
                # iId = "A" + number
                agencyName = "A" + agencyName
                cursor.execute(None, {'agencyName':agencyName})
                data = cursor.fetchone()


            # 使用者沒有輸入
            if len(agencyName) < 1:
                print("no agencyName",agencyName)
                flash('請輸入勞檢單位名稱', category='error')            
            else:
                sql = """
                        INSERT INTO LABORAGENCY 
                            (AGENCYNAME, PHONE, ADDRESS, AREA, URL)
                        VALUES
                            (:agencyName, :phone, :address, :area, :url)
                    """

                cursor.execute(sql, {
                    'agencyName': agencyName, 'phone':phone, 'address':address,
                    'area':area, 'url':url       
                    })
                connection.commit()
                print("新增資料成功")
                flash('新增資料成功！', category='success')

                info = show_agency(agencyName)
                
                # todo: 剛新增完抓不到資料
                if info != None:
                    # return redirect(url_for('industry.viewIndustry', data=info))
                    return redirect(url_for('agency.Agency',data_agencyName=data_agencyName))
                else:               
                    return redirect(url_for('agency.Agency',data_agencyName=data_agencyName))

        # 編輯
        else:
            # inId = request.values.get('inId')
            agencyName = request.args['agencyName']
            sql ="""
                    UPDATE LABORAGENCY
                    SET
                        PHONE = :phone,
                        ADDRESS = :address,
                        AREA = :area,
                        URL = :url
                    WHERE AGENCYNAME = :agencyName
            """
            cursor.execute(sql, {
                'agencyName': agencyName, 'phone':phone, 'address':address,
                'area':area, 'url':url})

            connection.commit()
            flash('更新資料成功！', category='success')
            info = show_agency(agencyName)
            print("info__after update",info)
            
            return redirect(url_for('agency.Agency',data_agencyName=data_agencyName))
    else:
        # 編輯頁面
        if 'agencyName' in request.args:        
            agencyName = request.args['agencyName']
            info = show_agency(agencyName)
            print("進入編輯頁面")
            return render_template("viewAgency.html", data=info,
                                            data_agencyName=data_agencyName, 
                                            user=current_user,
                                            type='edit')
        else:
            # 進入新增頁面    
            return render_template("viewAgency.html", data_agencyName=data_agencyName, 
                                            user=current_user,
                                            type='add')





# 災害名稱
def In_agencyName():
    sql = " SELECT AGENCYNAME FROM LABORAGENCY "
    cursor.execute(sql)
    info_row = cursor.fetchall()
    s = list(set([i[0] for i in info_row]))
    info_data = [{'id':i,'agencyName':k} for i,k in enumerate(sorted(s))]

    return info_data



# 根據編號找資料
def show_agency(agencyName):
    sql = """
            SELECT * 
            FROM LABORAGENCY
            WHERE AGENCYNAME = :agencyName
        """
    cursor.execute(sql, {'agencyName': agencyName})
    data = cursor.fetchone() 
    if data != None:
        data = [i.strip() if isinstance(i, str) else i for i in data]
        info = {
                'agencyName': data[0],
                'phone': data[1],
                'address': data[2],
                'area': data[3],
                'url': data[4]
            }

        return info
    else:
        return None



