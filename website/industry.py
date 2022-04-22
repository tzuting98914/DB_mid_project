from flask import Blueprint, render_template, request, flash, redirect, url_for
import cx_Oracle
import random, string
from datetime import datetime
from website import connectDB
from flask_login import current_user,login_required
from website.tool import checkLength

connection = connectDB()
cursor = connection.cursor()

industry = Blueprint("industry",__name__)

## Oracle 連線
# cx_Oracle.init_oracle_client(lib_dir="C:/oracle/instantclient_21_3") # init Oracle instant client 位置
# connection = cx_Oracle.connect('Group15', 'group15group15', cx_Oracle.makedsn('140.117.69.58', 1521, 'orcl')) # 連線資訊
# cursor = connection.cursor()


# industry
@industry.route('/industry', methods=['GET', 'POST'])
def Industry():
    data_category = In_category()

    # 資料POST
    if request.method=='POST':
        # 搜尋
        if 'search' in request.values:
            inid_search = request.values.get("inid_search")
            category_search = request.values.get("category_search")
            inName_search = request.values.get("inName_search")

            inid_search = ('%' + inid_search+ '%') if inid_search != None else "%%"
            category_search = ('%' + category_search+ '%') if category_search != None else "%%"
            inName_search = ('%' + inName_search+ '%') if inName_search != None else "%%"

            sql = """
                    SELECT * 
                    FROM INDUSTRY
                    WHERE 
                        INID LIKE : inid_search AND
                        CATEGORY LIKE : category_search AND
                        INDUSTRYNAME LIKE : inName_search
                    ORDER BY INID ASC
                    """

            # cursor.prepare(sql)
            # cursor.execute(None,{'inid_search':inid_search,
            #                     'category_search':category_search,
            #                     'inName_search':inName_search,})
            cursor.execute(sql,{'inid_search':inid_search,
                                'category_search':category_search,
                                'inName_search':inName_search,})

            industry_row = cursor.fetchall()
            industry_data = []
            for i in industry_row:
                industry = {
                    'inId': i[0],
                    'category': i[1],
                    'industryName': i[2],
                    'industryDesc': i[3]
                }
                industry_data.append(industry)

            
            return render_template('industry.html', industry_data=industry_data,
                                                    data_category=data_category, 
                                                    user=current_user)
        # 刪除資料
        if 'delete' in request.values:            
            inid = request.values.get('delete')
            print("delete", inid)
            
            if('I' in inid):
                cursor.prepare('DELETE FROM INDUSTRY WHERE INID = :inid ')
                cursor.execute(None, {'inid': inid})
                connection.commit() # 把這個刪掉
                return redirect(url_for('industry.Industry'))

            else:
                flash('正式的行業別資料，沒辦法刪除喔', category='error')
                return redirect(url_for('industry.Industry'))

        # 修改資料
        if 'edit' in request.values:
            inId = request.values.get('edit')                        
            return redirect(url_for('industry.viewIndustry',inId=inId))
    

    # 列出全部
    else:
        sql = 'SELECT * FROM INDUSTRY ORDER BY INID ASC'
        cursor.execute(sql)
        industry_row = cursor.fetchall()
        industry_data = []
        for i in industry_row:
            industry = {
                'inId': i[0],
                'category': i[1],
                'industryName': i[2],
                'industryDesc': i[3]
            }
            industry_data.append(industry)

        
        return render_template('industry.html', industry_data=industry_data,
                                                data_category=data_category, 
                                                user=current_user)



# 新增industry基本資訊
@industry.route('/viewIndustry', methods=['GET', 'POST'])
@login_required
def viewIndustry():
    data_category = In_category()
    data_industryName = In_industryName()

    # 新增industry資料
    if request.method == 'POST':
        category = request.values.get('category')
        industryName = request.values.get('industryName')
        industryDesc = request.values.get('industryDesc')

        # 新增職災資訊
        if request.form['submitBtn'] == "add":
            # 確認資料庫中id不重複
            cursor.prepare('SELECT * FROM INDUSTRY WHERE INID = :inId')
            data = ""
            while ( data != None): 
                number = str(random.randrange( 100000000, 999999999))
                inId = "I" + number             
                cursor.execute(None, {'inId':inId})
                data = cursor.fetchone()


            # 使用者輸入判斷
            if (len(category) < 1):
                print("no eid",category)
                flash('請選擇行業類別', category='error')
            elif (len(industryName) < 1 or checkLength(industryName,100)):
                print("no industryName",industryName)     
                flash('行業名稱未輸入或內容過長!', category='error')
                return redirect(url_for('industry.viewIndustry'))
            elif (checkLength(industryDesc,1500)):
                print("no industryDesc",industryDesc)    
                flash('行業敘述內容過長!', category='error')
                return redirect(url_for('industry.viewIndustry'))   
            else:
                sql = """
                        INSERT INTO INDUSTRY 
                            (INID, CATEGORY, INDUSTRYNAME, INDUSTRYDESC)
                        VALUES
                            (:inId, :category, :industryName, :industryDesc)
                    """

                cursor.execute(sql, {
                    'inId': inId, 'category':category,
                    'industryName':industryName, 'industryDesc':industryDesc           
                    })
                connection.commit()
                print("新增資料成功")
                flash('新增資料成功！', category='success')

                info = show_industry(inId)
                
                # todo: 剛新增完抓不到資料
                if info != None:
                    # return redirect(url_for('industry.viewIndustry', data=info))
                    return redirect(url_for('industry.Industry'))
                else:               
                    return redirect(url_for('industry.Industry'))


        # 編輯
        else:
            # inId = request.values.get('inId')
            inId = request.args['inId']

            if (len(category) < 1):
                print("no eid",category)
                flash('請選擇行業類別', category='error')
            elif (len(industryName) < 1 or checkLength(industryName,100)):
                print("no industryName",industryName)     
                flash('行業名稱未輸入或內容過長!', category='error')
                return redirect(url_for('industry.Industry'))
            elif (checkLength(industryDesc,1500)):
                print("no industryDesc",industryDesc)    
                flash('行業敘述內容過長!', category='error')
                return redirect(url_for('industry.Industry'))   
            else:
                sql ="""
                        UPDATE INDUSTRY
                        SET
                            CATEGORY = :category,
                            INDUSTRYNAME = :industryName,
                            INDUSTRYDESC = :industryDesc
                        WHERE INID = :inId
                """
                cursor.execute(sql, {
                    'inId':inId, 'category': category, 
                    'industryName':industryName, 'industryDesc':industryDesc})

                connection.commit()
                flash('更新資料成功！', category='success')
                info = show_industry(inId)
                print("info__after update",info)
                
                return redirect(url_for('industry.Industry'))
    else:
        # 編輯頁面
        if 'inId' in request.args:        
            inId = request.args['inId']
            info = show_industry(inId)
            print("進入編輯頁面")
            return render_template("viewIndustry.html", data=info,
                                            data_category=data_category,
                                            data_industryName=data_industryName, 
                                            user=current_user,
                                            type='edit')
        else:
            # 進入新增頁面    
            return render_template("viewIndustry.html",    
                                            data_category=data_category,
                                            data_industryName=data_industryName, 
                                            user=current_user,
                                            type='add')




# 行業類別
def In_category():
    sql = " SELECT CATEGORY FROM INDUSTRY "
    cursor.execute(sql)
    info_row = cursor.fetchall()
    s = list(set([i[0] for i in info_row]))
    info_data = [{'id':i,'CATEGORY':k} for i,k in enumerate(sorted(s))]

    return info_data

# 行業名稱
def In_industryName():
    sql = " SELECT INDUSTRYNAME FROM INDUSTRY "
    cursor.execute(sql)
    info_row = cursor.fetchall()
    s = list(set([i[0] for i in info_row]))
    info_data = [{'id':i,'industryName':k} for i,k in enumerate(sorted(s))]

    return info_data


# 根據編號找資料
def show_industry(inid):
    sql = """
            SELECT * 
            FROM INDUSTRY
            WHERE INID = :inid
        """
    cursor.execute(sql, {'inid': inid})
    data = cursor.fetchone() 
    if data != None:
        data = [i.strip() if isinstance(i, str) else i for i in data]
        info = {
                'inId': data[0],
                'category': data[1],
                'industryName': data[2],
                'industryDesc': data[3]
            }
        return info
    else:
        return None

def Industry():
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
        }
        info_data.append(info)
    return info_data