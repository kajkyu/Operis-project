from db_pool import get_pool
pool = get_pool()

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
