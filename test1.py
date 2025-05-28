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

load_dotenv()


#db pool 생성
pool = PooledDB(
    creator = pymysql,
    maxconnections = 3,     
    mincached = 1 ,         
    blocking = True,
    host = "sql5.freesqldatabase.com",
    user = "sql5777334",
    password = os.getenv('DB_password'),
    port = 3306, 
    database = "sql5777334"
)

# query = "select * from users"
# cursor.execute(query)
# row = cursor.fetchall()
# print(row)

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
    user = get_logged_user()
    query = ["select * from laws where views > 200 order by good / (good + bad) desc limit 1;",
             "select * from laws where views > 200 order by bad / (good + bad) desc limit 1;",
             "select * from laws order by views desc limit 1;",
             "select * from laws where views > 50 order by views asc limit 1;"]
    dataset = get_datas(query)
    max_good = dataset[0]
    max_bad = dataset[1]
    max_view = dataset[2]
    max_valuable = dataset[3]
    new_list = get_data("select * from laws order by PROPOSE_DT desc limit 10 ;")
    print("-" * 50)
    # print(new_list[0])
    print(request.cookies)
    print(user)
    # print(max_good['id'])
    # print(max_bad)
    # print(max_view)
    # print(max_valuable)
    if user : 
        return render_template('main_test2.html', user = user, max_good = max_good, max_bad = max_bad, max_view = max_view, max_valuable = max_valuable, new_list = new_list)
    else :
        return render_template('main_test2.html', user = None, max_good = max_good, max_bad = max_bad, max_view = max_view, max_valuable = max_valuable, new_list = new_list)
    # return render_template('main_test2.html', max_good = max_good, max_bad = max_bad, max_view = max_view, max_valuable = max_valuable, new_list = new_list)
    




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
        cursor.execute("insert into users values(%s ,%s,%s ,%s)", (pid, pname, page, pword) )
        conn.commit()
        conn.close()
        return "success to add the user"
    except Exception as e :
        return "error" 

@app.route("/login", methods = ['GET'])
def login() : 
    return render_template("login_pro.html")

@app.route("/index/<username>", methods = ['GET'])
def index1(username) : 
    return "Hello " + username

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
    print(ls)
    if len(ls) > 0 :
        if ls[0][3] == pword :
            payload = {
                "id" : pid,
                "exp" : datetime.utcnow() + timedelta(hours= 1),
                "name" : ls[0][1]
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

def crawling(BILL_NO) :
    url = f'https://open.assembly.go.kr/portal/openapi/nzmimeepazxkubdpn?AGE=22&KEY=bab1a106f834406d84066a97a809b643&Type=json&BILL_NO={BILL_NO}'
    res_url = requests.get(url)
    data = res_url.json()
    crawl_url = data['nzmimeepazxkubdpn'][1]['row'][0]['DETAIL_LINK']
    print(crawl_url)
    res = requests.get(crawl_url)
    soup = BeautifulSoup(res.text, 'html.parser')
    summary = soup.find('div', {'id' : 'summaryContentDiv'})
    for i in summary.find_all('br') :
        i.replace_with("\n")
    
    summ = summary.get_text().strip()
    datas = summ.split('\n')[4:]
    datas = [i for i in datas if i != '']
    for i in range(len(datas)) :
        datas[i] = datas[i].lstrip()

    summ = "\n".join(datas)
    # print("---" * 50)
    summ = summ.split('주요내용')
    summ = " ".join(summ)
    summ = summ.split('참고사항')
    summ = " ".join(summ)
    # print(summ)
    return summ, data['nzmimeepazxkubdpn'][1]['row'][0]

def make_data(data) :
    if data[4] + data[5] == 0 :
            good_rate = 0
            bad_rate = 0
    else :
        good_rate = int(( data[4] / (data[4] + data[5])) * 100)
        bad_rate = 100 - good_rate
    result = {
        

        'id' : data[0],
        'name' : data[1],
        'proposer' : data[2],
        'date' : data[3],
        'good' : data[4],
        'bad' : data[5],
        'views' : data[6],
        'good_rate' : good_rate,
        'bad_rate' : bad_rate
    }
    return result


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
        conn.close()
        result = []
        result.extend([data['BILL_NO'], data['BILL_NAME'], data['PROPOSER'], data['PROPOSE_DT'],0 ,0, 1])
    else :
        print("Existing rows")
        cursor.execute("update laws set views = views+1 where BILL_NO = %s ;", (BILL_NO, ))
        conn.commit()
        conn.close()
        result = list(result[0])


    result = make_data(result)  
    result['views']+=1
    print(result)
    
    
    #해당 laws 테이블에서의 데이터, 요약
    return render_template("sdf.html", summary = summ, data = result, user= user, vote_config = vote_config)


@app.route("/contents/<BILL_NO>", methods = ['POST'])
def vote(BILL_NO) :
    res = request.form.get('vote')
    print("votes :", res)
    user = get_logged_user()
    print(user)
    if not user :
        #경고창 생성해야함
        return redirect('/login')
    conn = pool.connection()
    cursor = conn.cursor()
    
    if res == "agree" :
        cursor.execute("insert into vote() values(%s, %s, %s, True) on duplicate key update vote = True", (user['id'], BILL_NO, user['name'], ))
        cursor.execute("update laws set good = good+1 where BILL_NO = %s ;", (BILL_NO, ))
        
    elif res == "disagree" :
        cursor.execute("insert into vote() values(%s, %s, %s, False) on duplicate key update vote = False", (user['id'], BILL_NO, user['name'], ))
        cursor.execute("update laws set bad = bad+1 where BILL_NO = %s ;", (BILL_NO, ))
    conn.commit()
    
    conn.close()
    return redirect(url_for('contents', BILL_NO = BILL_NO))


@app.route("/contents/delete/<BILL_NO>", methods = ['POST'])
def vote_delete(BILL_NO) :
    user = get_logged_user()
    vote_config = request.form.get('revote')
    vote_config = int(vote_config)
    print("vote config in delete : " , vote_config, type(vote_config))
    conn = pool.connection()
    cursor = conn.cursor()
    cursor.execute("delete from vote where id = %s and BILL_NO = %s", (user['id'], BILL_NO))
    if vote_config == 1 :
        cursor.execute("update laws set good = good - 1 where BILL_NO = %s", (BILL_NO,))
    elif vote_config == 0 :
        cursor.execute("update laws set bad = bad - 1 where BILL_NO = %s", (BILL_NO,))
    else :
        print("Delete Error")
    conn.commit()
    conn.close()
    return redirect(url_for('contents', BILL_NO = BILL_NO))





@app.route("/getdata", methods = ['POST'])
def shows():
    inp = request.form['data']
    return inp

if __name__ == "__main__" :
    app.run('0.0.0.0', port = 3000, debug = True)
