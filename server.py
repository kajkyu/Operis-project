from flask import Flask , render_template ,request, jsonify, redirect, url_for, make_response
# from mysql.connector import pooling
from dbutils.pooled_db import PooledDB
import pymysql
import jwt
import os, requests
from bs4 import BeautifulSoup
import requests, urllib.request
from datetime import datetime, timedelta
from dotenv import load_dotenv
import time
from modules.contents_module import make_data, get_comments, get_age
from modules.crawling import crawling
from urllib.parse import urlencode

load_dotenv()


#db pool 생성
pool = PooledDB(
    creator = pymysql,
    maxconnections = 5,     
    mincached = 3,         
    blocking = True,
    host = "sql5.freesqldatabase.com",
    user = "sql5777334",
    password = os.getenv('DB_password'),
    port = 3306, 
    database = "sql5777334",
    charset = "utf8mb4"
)







app = Flask(__name__)

def get_logged_user() :
    token = request.cookies.get('token')
    if not token :
        return None 
    try : 
        decode = jwt.decode(token, os.getenv('JWT_SECRET_KEY'), algorithms=["HS256"]) #json 형식 
        return decode
    except jwt.ExpiredSignatureError : 
        return None
    except jwt.InvalidTokenError :
        return None

    

def get_data(query) :
    try : 
        conn = pool.connection()
        cursor = conn.cursor()
        cursor.execute(query)
        ls = cursor.fetchall()
        conn.close()
        res = []
        print(ls)
        for i in ls :
            data = list(i)
            if(data[4] + data[5] == 0) :
                good_rate = 0
                bad_rate = 0
            else : 
                good_rate = int((data[4] / (data[4] + data[5])) * 100)
                bad_rate = 100 - good_rate
            data.append(good_rate)
            data.append(bad_rate)
            result = {
                "id" : data[0],
                "name" : data[1],
                "proposer" : data[2],
                "date" : data[3],
                "good" : data[4],
                "bad" : data[5],
                "views" : data[6],
                "good_rate" : data[7],
                "bad_rate" : data[8]
            }
            res.append(result)
        return res
    except Exception as e :
        print("Error:", e)  
        return "error: " + str(e)
    
def get_datas(query) :
    try : 
        conn = pool.connection()
        cursor = conn.cursor()
        res = []
        for i in query : 
            cursor.execute(i)
            ls = cursor.fetchone()
            data = list(ls)
            good_rate = int((data[4] / (data[4] + data[5])) * 100)
            bad_rate = 100 - good_rate
            data.append(good_rate)
            data.append(bad_rate)
            result = {
                "id" : data[0],
                "name" : data[1],
                "proposer" : data[2],
                "date" : data[3],
                "good" : data[4],
                "bad" : data[5],
                "views" : data[6],
                "good_rate" : data[7],
                "bad_rate" : data[8]
            }
            res.append(result)

        conn.close()
        return res
    except Exception as e :
        print("Error:", e)  
        return "error: " + str(e)


#index page (Main page로 운영할 계획)
@app.route("/")
def index():
    #로그인된 유저 정보 가져옴, 없으면 None
    user = get_logged_user()
    query = ["select * from laws where views > 200 order by good / (good + bad) desc limit 1;",
             "select * from laws where views > 200 order by bad / (good + bad) desc limit 1;",
             "select * from laws order by views desc limit 1;",
             "select * from laws where views > 50 order by views asc limit 1;"] # 주목할 법안 division with zero 조심 
    #select * from laws where views > 50 order by PROPOSE_DT desc limit 1 ;
    #select * from laws where views > 50 order by views asc limit 1;
    dataset = get_datas(query)
    max_good = dataset[0]
    max_bad = dataset[1]
    max_view = dataset[2]
    max_valuable = dataset[3]
    new_list = get_data("select * from laws order by PROPOSE_DT desc limit 10 ;")
    print("-" * 50)
    
    
    print(user) # {'id': 'Kice', 'exp': 1748976296, 'name': 'sally', 'age': 21}
    
    #로그인/비로그인 구분해서 render
    if user : 
        return render_template('main_test2.html', user = user, max_good = max_good, max_bad = max_bad, max_view = max_view, max_valuable = max_valuable, new_list = new_list)
    else :
        return render_template('main_test2.html', user = None, max_good = max_good, max_bad = max_bad, max_view = max_view, max_valuable = max_valuable, new_list = new_list)
    
    




#회원가입 페이지 로드
@app.route("/signup" , methods = ['GET'])
def signup():
    return render_template('signup1.html')

#회원가입 페이지에서 사용자 추가 요청처리
@app.route("/process/adduser" , methods = ['POST'])
def signups():
    try : 
        conn = pool.connection()   
        cursor = conn.cursor()    

        pid = request.form['id']    
        pword = request.form['pword']   
        pname = request.form['name']   
        page = request.form['age']     
        print(pid + " " + pword + " " + page + " " + pname) 
        cursor.execute("insert into users values(%s ,%s,%s ,%s)", (pid, pname, page, pword,) )
        conn.commit()
        conn.close()
        return redirect('/login')
    except Exception as e :
        return "error" 

#로그인 페이지 로드 
@app.route("/login", methods = ['GET'])
def login() : 
    return render_template("login_pro.html")

#로그인 페이지에서 로그인 처리 
@app.route("/process/login", methods = ['POST'])
def logins() : 
    pid = request.form['id']
    pword = request.form['password']
    conn = pool.connection()
    cursor = conn.cursor()
    print(pid + " " + pword)
    cursor.execute("select * from users where id = %s", (pid, ))
    ls = cursor.fetchall()
    conn.close()
    print(ls) # ((sdf, 12, sdfa, sdf),)
    if len(ls) > 0 :
        if ls[0][3] == pword :
            payload = {
                "id" : pid,
                "exp" : datetime.utcnow() + timedelta(hours= 1),
                "name" : ls[0][1],
                "age" : ls[0][2]
            }
            token = jwt.encode(payload, os.getenv('JWT_SECRET_KEY'), algorithm="HS256")
            res = make_response(redirect('/'))
            res.set_cookie('token', token)
            return res
            # return redirect(url_for('index1', username = pid))
        else :
            return "Wrong Password"
    else :
        return "there is no data"
        
#아이디 중복 요청 처리 
@app.route("/getdb", methods = ['POST'])
def getdb():
    data = request.get_json()
    check_id = data['id']
    print(check_id)
    reply = {
        'chk' : "none"
    }
    conn = pool.connection()
    cursor = conn.cursor()
    cursor.execute("select * from users where id = %s", (check_id, ))
    result = cursor.fetchall()
    conn.close()
    print(result)
    if len(result) > 0 :
        reply['chk'] = "Duplicate"
    elif len(result) == 0 :
        reply['chk'] = "ok"
    else :
        reply['chk'] = "err"
    return jsonify(reply)

@app.route("/logout", methods = ['GET'])
def logout() :
    res = make_response(redirect('/'))
    res.set_cookie('token', '', expires=0)
    return res


@app.route("/contents/<BILL_NO>")
def contents(BILL_NO):
    print("enter the contents")

    summ, data = crawling(BILL_NO)
    user = get_logged_user()
    conn = pool.connection()
    cursor = conn.cursor()
    
    #기존 db에 있는 법안인지 확인
    cursor.execute("select * from laws where BILL_NO = %s", (BILL_NO, ))
    result = cursor.fetchall()

    #투표 여부 확인
    vote_config = None
    if user :
        cursor.execute("select * from vote where BILL_NO = %s and id = %s", (BILL_NO, user['id']))
        vote = cursor.fetchone()
        
        print("vote : ", vote)
        
        if vote != None and len(vote) > 0 : 
            vote_config = vote[3]
        

    # len(reuslt) == 0 기존에 없던 법안
    if len(result) == 0 :
        print("create the rows")
        cursor.execute("insert into laws values(%s, %s, %s, %s, %s, %s, %s)", 
                       (data['BILL_NO'], data['BILL_NAME'], data['PROPOSER'], data['PROPOSE_DT'],0 ,0, 1,) )
        conn.commit()
        # conn.close()
        result = []
        result.extend([data['BILL_NO'], data['BILL_NAME'], data['PROPOSER'], data['PROPOSE_DT'],0 ,0, 1])
    else :
        print("Existing rows")
        cursor.execute("update laws set views = views+1 where BILL_NO = %s ;", (BILL_NO, ))
        conn.commit()
        # conn.close()
        result = list(result[0])

    result = make_data(result)  
    result['views']+=1
    print("result : ", result)

    #댓글 가져오기 
    cursor.execute("select * from comments where BILL_NO = %s order by reg_date desc;", (BILL_NO,))
    Comments_List = cursor.fetchall()
    #나이대별 가져오기 
    cursor.execute("select * from vote_age where BILL_NO = %s", (BILL_NO,))
    age_list = cursor.fetchone()
    if age_list :
        sum = 0
        age_list = list(age_list[1:])
        for age in age_list :
            sum+=age
        if sum == 0 :
            age_list = None

    print(age_list)
    conn.close()
    Comments_List = get_comments(Comments_List)
    print(Comments_List)
    # print(Comments_List)

    return render_template("contents.html", summary = summ, data = result, user= user, vote_config = vote_config, Comments_List = Comments_List, age_list = age_list)


@app.route("/contents/<BILL_NO>", methods = ['POST'])
def vote(BILL_NO) :
    res = request.form.get('vote') # agree or disagree
    print("votes :", res)
    user = get_logged_user()
    print(user)
    if not user :
        #경고창 생성해야함
        return redirect('/login')
    conn = pool.connection()
    cursor = conn.cursor()
    
    if res == "agree" :
        cursor.execute("insert into vote values(%s, %s, %s, 'agree')", (user['id'], BILL_NO, user['name'], ))
        cursor.execute("update laws set good = good+1 where BILL_NO = %s ;", (BILL_NO, ))
        
    elif res == "disagree" :
        cursor.execute("insert into vote values(%s, %s, %s, 'disagree') ", (user['id'], BILL_NO, user['name'], ))
        cursor.execute("update laws set bad = bad+1 where BILL_NO = %s ;", (BILL_NO, ))
    
    
    if user :
        age = get_age(user['age'])
        sql = f"insert into vote_age(BILL_NO, {age}) values(%s, 1) on duplicate key update {age} = {age} + 1"
        cursor.execute(sql, (BILL_NO,))

    conn.commit()
    conn.close()

    return redirect(url_for('contents', BILL_NO = BILL_NO))


@app.route("/contents/delete/<BILL_NO>", methods = ['POST'])
def vote_delete(BILL_NO) :
    user = get_logged_user()
    vote_config = request.form.get('revote')
    
    print("vote config in delete : " , vote_config, type(vote_config))
    conn = pool.connection()
    cursor = conn.cursor()
    cursor.execute("delete from vote where id = %s and BILL_NO = %s", (user['id'], BILL_NO))
    if vote_config == "agree" :
        cursor.execute("update laws set good = good - 1 where BILL_NO = %s", (BILL_NO,))
    elif vote_config == "disagree" :
        cursor.execute("update laws set bad = bad - 1 where BILL_NO = %s", (BILL_NO,))
    else :
        print("Delete Error")
    age = get_age(user['age'])
    sql = f"update vote_age set {age} = {age} - 1 where BILL_NO = %s"
    cursor.execute(sql, (BILL_NO,))
    conn.commit()
    conn.close()
    return redirect(url_for('contents', BILL_NO = BILL_NO))

@app.route("/comments", methods = ['POST'])
def comments() :
    data = request.get_json()
    userid = data['id']
    BILL_NO = data['BILL_NO']
    contents = data['content']
    username = data['username']
    vote_config = data['vote_config']
    print(userid, BILL_NO, contents)
    print(time.strftime('%Y.%m.%d %H:%M'))
    date = time.strftime('%Y-%m-%d %H:%M')
    conn = pool.connection()
    cursor = conn.cursor()
   

    cursor.execute("insert into comments(id, BILL_NO, name, vote, contents, reg_date ) values(%s, %s, %s, %s, %s, %s);", (userid, BILL_NO, username, vote_config, contents, date ))
    conn.commit()
    conn.close()
    return data

@app.route("/contents/delete/comments/<BILL_NO>", methods = ['POST'])
def delte_comments(BILL_NO):
    comment = request.form.get('comment')
    conn = pool.connection()
    cursor = conn.cursor()
    cursor.execute("delete from comments where rid = %s", (comment,))
    conn.commit()
    conn.close()
    return redirect(url_for('contents', BILL_NO = BILL_NO))

@app.route("/getdata", methods = ['POST'])
def shows():
    inp = request.form['data']
    return inp

@app.route("/search")
def search():
    
    return render_template('search.html')

@app.route("/search", methods = ['POST'])
def search1():
    form_type = request.form.get('action_type')
    if form_type == 'searching' :
        search = request.form['search-target']
        pindex = 1
    elif form_type == 'page' :
        search = request.form.get('search-target')
        pindex = request.form.get('pindex')
        status = request.form.get('page_button')
        total_page = request.form.get('total_page')
        print(pindex)
        print(status)
        print(total_page)
        pindex = int(pindex)
        if status == 'prev' and pindex != 1 :
           pindex = pindex - 1
        elif status == 'next'  and pindex < int(total_page):  
            pindex = pindex + 1
        
    url = "https://open.assembly.go.kr/portal/openapi/nzmimeepazxkubdpn"
    
    params = {
        'AGE' : 22,
        'KEY' : 'bab1a106f834406d84066a97a809b643',
        'BILL_NAME' : search,
        'Type' : 'json',
        'pSize' : 10,
        'pIndex' : pindex

    }
    search_url = url + '?' + urlencode(params)
    crawl_data = requests.get(search_url)
    print(search_url)
    result = crawl_data.json()
    res = []
    try : 
        total = result['nzmimeepazxkubdpn'][0]['head'][0]['list_total_count']
        search_list = result['nzmimeepazxkubdpn'][1]['row']
        page = ((total-1) // 10) + 1
        for result in search_list :
            res.append({
                'id' : result['BILL_NO'],
                'name' : result['BILL_NAME'],
                'proposer' : result['PROPOSER'],
                'date' : result['PROPOSE_DT'],
                'committee' : result['COMMITTEE'] if result['COMMITTEE'] != None else "해당없음"
            })
    except :
        total = 0
        search_list = None
        page = 1
    
    # print(res)
    # print(total)
    # print(search_list)
    return render_template('search.html', search_result = res, search = search, total = total, page = page, pindex = pindex)



    

if __name__ == "__main__" :
    app.run('0.0.0.0', port = 3000, debug = True)
