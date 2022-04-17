# store routes
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from flask import jsonify
from website import connectDB
from json import dumps
import random, string
from datetime import datetime

connection = connectDB()
cursor = connection.cursor()

views = Blueprint('views', __name__)

def test():
    sql = "SELECT * FROM workinjury_test FETCH FIRST 3 ROWS ONLY"
    cursor.prepare(sql)
    cursor.execute(None)
    info_row = cursor.fetchall()
    info_data = []
    for i in info_row:
        info = {
            'wid': i[0],
            'pid': i[1],
            'iid': i[2],
            'injuryname': i[4],
            'num': i[5],
            'projectname': i[6],
            'enterprisename': i[7],
            'agencyname': i[8],
        }
        info_data.append(info)
    print("info_data",info_data)
    print("test_",sql)
# test()

# 職業災害首頁
@views.route('/', methods=['GET', 'POST'])
def index():
    
    enterprise_data = enterprise()
    project_data = project()  
    injurytype_data = injurytype()
    agency_data = agency()
    
    # 刪除職災
    if 'delete' in request.values:            
        wid = request.values.get('delete')
        print("delete", wid)
        
        if('w' in wid):
            cursor.prepare('DELETE FROM workinjury WHERE wid = :wid ')
            cursor.execute(None, {'wid': wid})
            connection.commit() # 把這個刪掉
        else:
            flash('正式的職災資料，沒辦法刪除喔', category='error') 
                    
    # 修改職災
    elif 'edit' in request.values: 
            wid = request.values.get('edit')                        
            return redirect(url_for('views.viewWorkInjury', wid=wid, user = current_user))

    # 查詢資料
    if 'search' in request.values:
        wid_search = request.values.get('wid_search')
        estr_search = request.values.get('estr_search')
        pstr_search = request.values.get('pstr_search')
        iid_search = request.values.get('iid_search')       
        agencyname_search = request.values.get('agencyname_search')
                
        wid_search = ('%' + wid_search+ '%') if wid_search != None else "%%"
        estr_search = ('%' + estr_search+ '%') if estr_search != None else "%%"
        pstr_search = ('%' + pstr_search+ '%') if pstr_search != None else "%%"
        iid_search = ('%' + iid_search+ '%') if iid_search != None else "%%"        
        agencyname_search = ('%' + agencyname_search+ '%') if agencyname_search != None else '%%'

        # print(
        #     wid_search+"___"+
        #     estr_search+"___"+
        #     pstr_search+"___"+
        #     iid_search+"___"+
        #     agencyname_search
        # )                        
        sql = """
                SELECT 
                    w.wid,p.pid,i.iid, w.wdate,
                    i.injuryname, w.num,p.projectname,
                    e.enterprisename,w.agencyname
                FROM workinjury w                
                    LEFT JOIN enterprise e
                    ON w.eid = e.eid                
                    LEFT JOIN Poject p
                    ON w.pid = p.pid                
                    LEFT JOIN injurytype i
                    ON w.iid = i.iid                    
                WHERE  
                    w.wid LIKE : wid_search AND
                    e.enterprisename LIKE :estr_search AND
                    p.projectname LIKE :pstr_search AND
                    i.injuryname LIKE : iid_search AND
                    w.agencyname LIKE : agencyname_search
                                        
                ORDER BY p.pid FETCH FIRST 50 ROWS ONLY
            """
                        
        cursor.prepare(sql)
        cursor.execute(None, {
            'wid_search': wid_search, 'estr_search':estr_search, 
            'pstr_search':pstr_search, 'iid_search':iid_search,
            'agencyname_search': agencyname_search,       
            })

        info_row = cursor.fetchall()
        info_data = []
        for i in info_row:
            info = {
                'wid': i[0],
                'pid': i[1],
                'iid': i[2],
                'wdate': i[3].strftime('%Y-%m-%d'),
                'injuryname': i[4],
                'num': i[5],
                'projectname': i[6],
                'enterprisename': i[7],
                'agencyname': i[8],
            }
            info_data.append(info)
            
    # 剛進入主頁
    else:
        # 查看測試資料
        info_data = workInjury()
        
    return render_template("home.html", info_data=info_data,    
                                        enterprise_data = enterprise_data,
                                        project_data = project_data,
                                        injurytype_data = injurytype_data,
                                        agency_data = agency_data, 
                                        user = current_user)


# 新增職災基本資訊
@views.route('/viewWorkInjury', methods=['GET', 'POST'])
@login_required
def viewWorkInjury():
    
    enterprise_data = enterprise()
    project_data = project()  
    injurytype_data = injurytype()
    agency_data = agency()
                
    # 新增職災資料
    if request.method == 'POST':    
             
        # 抓取form資料
        eid = request.values.get('eid')
        pid = request.values.get('pid')
        agencyname = request.values.get('agencyname')
        iid = request.values.get('iid')        
        location = request.values.get('location')
        wdate = request.values.get('wdate')
        num = request.values.get('num')
        note = request.values.get('note')
        address = request.values.get('address')
        
        wdate = str(datetime.strptime(wdate, '%Y-%m-%d'))
        format = 'yyyy/mm/dd hh24:mi:ss'
        
        print("request.form['submitBtn']",request.form['submitBtn'])
        # 新增職災資訊
        if request.form['submitBtn'] == "add":        
            # 確認資料庫中wid不重複
            cursor.prepare('SELECT * FROM WORKINJURY WHERE wId=:wid')
            data = ""
            while ( data != None): 
                number = str(random.randrange( 10000, 99999))
                wid = "w" + number             
                cursor.execute(None, {'wid':wid})
                data = cursor.fetchone()            
            print(
                wid,eid,pid,agencyname,
                iid,location,wdate,
                num,note,address
            )

            # 使用者沒有輸入
            if (len(eid) < 1):
                print("no eid",eid)
                flash('請輸入事業單位', category='error')
            elif len(agencyname) < 1:
                print("no agencyname",agencyname)
                flash('請輸入勞檢機構', category='error')            
                # return
            elif len(iid) < 1:
                print("no iid",iid)
                flash('請輸入災害類型', category='error')
            else:                    
                sql = """
                        INSERT INTO workinjury w ( 
                            wid,eid,pid,agencyname,
                            iid,location,wdate,
                            num,note,address)
                        VALUES 
                            (:wid, :eid, :pid, :agencyname,
                            :iid,:location, TO_DATE( :wdate, :format ) , 
                            :num, :note, :address )
                    """
                cursor.prepare(sql)
                cursor.execute(None, {
                    'wid': wid, 'eid':eid, 'pid':pid, 'agencyname':agencyname,
                    'iid': iid, 'location':location, 'wdate':wdate, 'format':format,
                    'num':num , 'note':note, 'address':address            
                    })
                connection.commit()
                print("新增資料成功")
                flash('新增資料成功！', category='success')
                
                info = show_workinjury(wid)                
                wid = info['wid']                                
                if info != None:
                    return redirect(url_for('views.viewWorkInjury', wid=wid, user = current_user))
                else:               
                    flash('資料庫發生問題，請聯繫管理員', category='error')

        else:
            print("編輯職災資訊")          
            wid = request.args['wid']                        
            sql = """
                    UPDATE workinjury 
                    SET 
                        eid=:eid, 
                        pid=:pid, 
                        agencyname=:agencyname ,
                        iid=:iid ,
                        location=:location ,
                        wdate= TO_DATE( :wdate, :format ) ,
                        num=:num ,
                        note=:note ,
                        address=:address
                    WHERE wid=:wid
                """
                
            cursor.prepare(sql)
            cursor.execute(None, {
                'wid': wid, 'eid':eid, 'pid':pid, 'agencyname':agencyname,
                'iid': iid, 'location':location, 'wdate':wdate, 'format':format,
                'num':num , 'note':note, 'address':address            
                })
                        
            connection.commit()
            flash('更新資料成功！', category='success')
            info = show_workinjury(wid)
            # print("info__after update",info)
            
            return redirect(url_for('views.viewWorkInjury', wid=wid, user = current_user))
    else:
        # 編輯頁面
        if 'wid' in request.args:        
            wid = request.args['wid']
            info = show_workinjury(wid)
            return render_template("viewWorkInjury.html", data=info,    
                                        enterprise_data = enterprise_data,
                                        project_data = project_data,
                                        injurytype_data = injurytype_data,
                                        agency_data = agency_data, user = current_user)
        else:
            # 進入新增頁面    
            return render_template("viewWorkInjury.html",    
                                            enterprise_data = enterprise_data,
                                            project_data = project_data,
                                            injurytype_data = injurytype_data,
                                            agency_data = agency_data, user = current_user)

# 根據職災編號找資料
def show_workinjury(wid):    
    sql = """
            SELECT 
                w.wid,p.pid,i.iid, w.wdate,
                i.injuryname, w.num,p.projectname,
                e.enterprisename,w.agencyname,                
                w.location, w.address,
                ii.inid, ii.industryname,e.eid, w.note
                
            FROM workinjury w                
                LEFT JOIN enterprise e
                ON w.eid = e.eid                
                LEFT JOIN Industry ii
                ON e.inid = ii.inid               
                LEFT JOIN Poject p
                ON w.pid = p.pid                    
                LEFT JOIN injurytype i
                ON w.iid = i.iid
            WHERE w.wid = """ + "\'" + wid + "\'"
        
    cursor.execute(sql)
    data = cursor.fetchone()     
    if data != None:
        info = {
                'wid': data[0],
                'pid': data[1],
                'iid': data[2],
                'wdate': data[3].strftime('%Y-%m-%d'),
                'injuryname': data[4],
                'num': data[5],
                'projectname': data[6],
                'enterprisename': data[7],
                'agencyname': data[8],            
                'location': data[9],
                'address': data[10],
                'inid': data[11],
                'industryname': data[12],
                'eid': data[13],
                'note': data[14],
        }
        return info

    else:
        return None

def workInjury():
    sql = """
            SELECT 
                w.wid,p.pid,i.iid, w.wdate,
                i.injuryname, w.num,p.projectname,
                e.enterprisename,w.agencyname,e.eid

            FROM workinjury w                
                LEFT JOIN enterprise e
                ON w.eid = e.eid                
                LEFT JOIN Poject p
                ON w.pid = p.pid                
                LEFT JOIN injurytype i
                ON w.iid = i.iid
            
            WHERE  w.wid LIKE 'w%'
            ORDER BY p.pid
            FETCH FIRST 20 ROWS ONLY
        """

    cursor.execute(sql)
    info_row = cursor.fetchall()
    info_data = []
    for i in info_row:
        info = {
            'wid': i[0],
            'pid': i[1],
            'iid': i[2],
            'wdate': i[3].strftime('%Y-%m-%d'),
            'injuryname': i[4],
            'num': i[5],
            'projectname': i[6],
            'enterprisename': i[7],
            'agencyname': i[8],
            'eid': i[9],
        }
        info_data.append(info)
    return info_data

def project():
    sql = " SELECT pid, projectname FROM poject "
    cursor.execute(sql)
    info_row = cursor.fetchall()
    info_data = []
    for i in info_row:
        info = {
            'pid': i[0].strip(),
            'projectname': i[1],
        }
        info_data.append(info)
    return info_data

def injurytype():
    sql = " SELECT iid, injuryname FROM injurytype "
    cursor.execute(sql)
    info_row = cursor.fetchall()
    info_data = []
    for i in info_row:
        info = {
            'iid': i[0].strip(),
            'injuryname': i[1],
        }
        info_data.append(info)
    return info_data

def agency():
    sql = "SELECT agencyname FROM laboragency"
    cursor.execute(sql)
    info_row = cursor.fetchall()
    info_data = []
    for i in info_row:
        info = {
            'agencyname': i[0],
        }
        info_data.append(info)
    return info_data

@views.route('/get_detail')
def get_prediction():
    word = request.values.get('word')
    infotype = request.values.get('infotype')
    if infotype == 'a':
        result = agencyInfo(word)
    elif infotype == 'e':
        result = enterpriseInfo(word)
    elif infotype == 'p':
        result = projectInfo(word)
    print(result)
    
    return jsonify({'result':result})

def enterpriseInfo(eid):
    sql = """SELECT * 
        FROM enterprise e
            LEFT JOIN industry i
            ON e.inid = i.inid
        WHERE eid=:eid
        """
    cursor.prepare(sql)
    cursor.execute(None, {
                    'eid':eid,
                    })

    data = cursor.fetchone()     
    if data != None:
        info = {
                'eid': data[0],
                'address': data[1],
                'enterpriseno': data[2],
                'principal': data[3],
                'capital': data[4],
                'inid': data[5],
                'enterprisename': data[6],
                'industryname': data[9],
        }
        return info
    else:
        return None    

def projectInfo(pid):
    sql = """
        SELECT * 
        FROM poject p       
            LEFT JOIN enterprise e
            ON p.eid = e.eid
        WHERE pid=:pid
    """
    cursor.prepare(sql)
    cursor.execute(None, {
                    'pid':pid,
                    })

    data = cursor.fetchone()     
    if data != None:
        info = {
                'pid': data[0],
                'projectname': data[1],
                'eid': data[2],
                'enterprisename': data[9],
        }
        print(data)
        return info
    else:
        return None    

def agencyInfo(agencyname):
    sql = "SELECT * FROM laboragency WHERE agencyname=:agencyname"
    cursor.prepare(sql)
    cursor.execute(None, {
                    'agencyname':agencyname,
                    })

    data = cursor.fetchone()     
    if data != None:
        info = {
                'agencyname': data[0],
                'phone': data[1],
                'address': data[2],
                'area': data[3],
                'url': data[4]
        }
        return info
    else:
        return None

def enterprise():
    sql = "SELECT eid,enterprisename FROM enterprise"
    cursor.execute(sql)
    info_row = cursor.fetchall()
    info_data = []
    for i in info_row:
        info = {
            'eid': i[0].strip(),
            'enterprisename': i[1],
        }
        info_data.append(info)
    return info_data


# 統計職災基本資訊
# @views.route('/plot', methods=['GET', 'POST'])
# def plot():
#     return render_template("plot.html")                   

@views.route('/plot')
def plot():
    revenue = []
    dataa = []
    for i in range(1,13):
        cursor.prepare('SELECT EXTRACT(MONTH FROM wdate), SUM(num) FROM workinjury WHERE EXTRACT(MONTH FROM wdate)=:mon GROUP BY EXTRACT(MONTH FROM wdate)')
        cursor.execute(None, {"mon": i})
        
        row = cursor.fetchall()
        if cursor.rowcount == 0:
            revenue.append(0)
        else:
            for j in row:
                revenue.append(j[1])
                
        cursor.prepare('SELECT EXTRACT(MONTH FROM wdate), COUNT(wid) FROM workinjury WHERE EXTRACT(MONTH FROM wdate)=:mon GROUP BY EXTRACT(MONTH FROM wdate)')
        cursor.execute(None, {"mon": i})
        
        row = cursor.fetchall()
        if cursor.rowcount == 0:
            dataa.append(0)
        else:
            for k in row:
                dataa.append(k[1])
    
    sql3 = """
                SELECT *
                FROM
                (
                    SELECT COUNT(wid) wc, w.iid
                    FROM workinjury w
                    GROUP BY w.iid
                    ORDER BY COUNT(wid) DESC
                ) g
                LEFT JOIN injurytype i
                ON g.iid = i.iid     
                ORDER BY wc DESC
            """
    cursor.prepare(sql3)
    cursor.execute(None)
    row = cursor.fetchall()
    
    datab = []
    for i in row:
        temp = {
            'value': i[0],
            'name': i[3]
        }
        datab.append(temp)    

    # 區域職災人數
    sql_sum = """
                SELECT SUM(num) wc, COUNT(wid), w.agencyname
                FROM workinjury w
                GROUP BY w.agencyname
                ORDER BY SUM(num) DESC
            """    
    cursor.prepare(sql_sum)
    cursor.execute(None)
    row = cursor.fetchall()
    print("sql_sum row", row)
        
    datac = [] 
    nameList = []
    countList = []     
                
    for i in row:
        datac.append(i[0]) # 人數
        countList.append(i[1]) # 件數
        nameList.append(i[2])
    
    return render_template('plot.html', 
                            revenue = revenue, 
                            dataa = dataa, datab = datab,
                            datac = datac, 
                            nameList = nameList, 
                            countList = countList, user = current_user
                           )