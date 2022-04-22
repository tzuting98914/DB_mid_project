from flask import Blueprint, render_template, request, flash, redirect, url_for
import cx_Oracle
import random, string
from datetime import datetime
from website import connectDB
from flask_login import current_user,login_required

connection = connectDB()
cursor = connection.cursor()
injury = Blueprint("injury",__name__)

## Oracle 連線
# cx_Oracle.init_oracle_client(lib_dir="C:/oracle/instantclient_21_3") # init Oracle instant client 位置
# connection = cx_Oracle.connect('Group15', 'group15group15', cx_Oracle.makedsn('140.117.69.58', 1521, 'orcl')) # 連線資訊
# cursor = connection.cursor()


# injury
@injury.route('/injury', methods=['GET', 'POST'])
def Injury():
    data_injuryName = In_injuryName()

    # 資料POST
    if request.method=='POST':
        # 搜尋
        if 'search' in request.values:
            iId_search = request.values.get("iId_search")
            injuryName_search = request.values.get("injuryName_search")
            injuryDesc_search = request.values.get("injuryDesc_search")

            iId_search = ('%' + iId_search+ '%') if iId_search != None else "%%"
            injuryName_search = ('%' + injuryName_search+ '%') if injuryName_search != None else "%%"
            injuryDesc_search = ('%' + injuryDesc_search+ '%') if injuryDesc_search != None else "%%"

            sql = """
                    SELECT * 
                    FROM INJURYTYPE
                    WHERE 
                        IID LIKE : iId_search AND
                        INJURYNAME LIKE : injuryName_search AND
                        INJURYDESC LIKE : injuryDesc_search
                    ORDER BY IID ASC
                    """

            # cursor.prepare(sql)
            # cursor.execute(None,{'inid_search':inid_search,
            #                     'category_search':category_search,
            #                     'inName_search':inName_search,})
            cursor.execute(sql,{'iId_search':iId_search,
                                'injuryName_search':injuryName_search,
                                'injuryDesc_search':injuryDesc_search,})

            injury_row = cursor.fetchall()
            injury_data = []
            for i in injury_row:
                injury = {
                    'iId': i[0],
                    'injuryName': i[1],
                    'injuryDesc': i[2]
                }
                injury_data.append(injury)

            
            return render_template('injury.html', injury_data=injury_data,
                                                    data_injuryName=data_injuryName, 
                                                    user=current_user)
        # 刪除資料
        if 'delete' in request.values:            
            iId = request.values.get('delete')
            print("delete", iId)
            
            if('I' in iId):
                cursor.prepare('DELETE FROM INJURYTYPE WHERE IID = :iId ')
                cursor.execute(None, {'iId': iId})
                connection.commit() # 把這個刪掉
                return redirect(url_for('injury.Injury'))

            else:
                flash('正式的資料，沒辦法刪除喔', category='error')
                return redirect(url_for('injury.Injury'))

        # 修改資料
        if 'edit' in request.values:
            iId = request.values.get('edit')                        
            return redirect(url_for('injury.viewInjury',iId=iId))
    


    # 列出全部
    else:
        sql = 'SELECT * FROM INJURYTYPE ORDER BY IID ASC'
        cursor.execute(sql)
        injury_row = cursor.fetchall()
        injury_data = []
        for i in injury_row:
            injury = {
                'iId': i[0],
                'injuryName': i[1],
                'injuryDesc': i[2]
            }
            injury_data.append(injury)

        
        return render_template('injury.html', injury_data=injury_data,
                                                data_injuryName=data_injuryName, 
                                                user=current_user)



# 新增injury基本資訊
@injury.route('/viewInjury', methods=['GET', 'POST'])
@login_required
def viewInjury():
    data_industryName = In_injuryName()

    # 新增injury資料
    if request.method == 'POST':
        injuryName = request.values.get('injuryName')
        injuryDesc = request.values.get('injuryDesc')

        # 新增職災資訊
        if request.form['submitBtn'] == "add":
            # 確認資料庫中id不重複
            cursor.prepare('SELECT * FROM INJURYTYPE WHERE IID = :iId')
            data = ""
            while ( data != None): 
                number = str(random.randrange( 100000000, 999999999))
                iId = "I" + number             
                cursor.execute(None, {'iId':iId})
                data = cursor.fetchone()


            # 使用者沒有輸入
            if len(injuryName) < 1:
                print("no injuryName",injuryName)
                flash('請輸入災害名稱', category='error')            
            else:
                sql = """
                        INSERT INTO INJURYTYPE 
                            (IID, INJURYNAME, INJURYDESC)
                        VALUES
                            (:iId, :injuryName, :injuryDesc)
                    """

                cursor.execute(sql, {
                    'iId': iId, 'injuryName':injuryName,
                    'injuryDesc':injuryDesc           
                    })
                connection.commit()
                print("新增資料成功")
                flash('新增資料成功！', category='success')

                info = show_injury(iId)
                
                # todo: 剛新增完抓不到資料
                if info != None:
                    # return redirect(url_for('industry.viewIndustry', data=info))
                    return redirect(url_for('injury.Injury'))
                else:               
                    return redirect(url_for('injury.Injury'))

        # 編輯
        else:
            # inId = request.values.get('inId')
            iId = request.args['iId']
            sql ="""
                    UPDATE INJURYTYPE
                    SET
                        INJURYNAME = :injuryName,
                        INJURYDESC = :injuryDesc
                    WHERE IID = :iId
            """
            cursor.execute(sql, {
                'iId':iId, 'injuryName': injuryName, 
                'injuryDesc':injuryDesc})

            connection.commit()
            flash('更新資料成功！', category='success')
            info = show_injury(iId)
            print("info__after update",info)
            
            return redirect(url_for('injury.Injury'))
    else:
        # 編輯頁面
        if 'iId' in request.args:        
            iId = request.args['iId']
            info = show_injury(iId)
            print("進入編輯頁面")
            return render_template("viewInjury.html", data=info, 
                                            user=current_user,
                                            type='edit')
        else:
            # 進入新增頁面    
            return render_template("viewInjury.html", 
                                            user=current_user,
                                            type='add')





# 災害名稱
def In_injuryName():
    sql = " SELECT INJURYNAME FROM INJURYTYPE "
    cursor.execute(sql)
    info_row = cursor.fetchall()
    s = list(set([i[0] for i in info_row]))
    info_data = [{'id':i,'injuryName':k} for i,k in enumerate(sorted(s))]

    return info_data



# 根據編號找資料
def show_injury(iId):
    sql = """
            SELECT * 
            FROM INJURYTYPE
            WHERE IID = :iId
        """
    cursor.execute(sql, {'iId': iId})
    data = cursor.fetchone() 
    if data != None:
        data = [i.strip() if isinstance(i, str) else i for i in data]
        info = {
                'iId': data[0],
                'injuryName': data[1],
                'injuryDesc': data[2]
            }
        return info
    else:
        return None

