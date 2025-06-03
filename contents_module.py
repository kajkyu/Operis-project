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

def get_comments(comments) :
    comments_list = []
    for i in comments :
        comments_list.append({
            'rid' : i[0],
            'id' : i[1],
            'BILL_NO' : i[2],
            'name' : i[3],
            'vote' : i[4],
            'contents' : i[5],
            'date' : i[6]
        })
    return comments_list

def get_age(age) :
    if age < 20 :
        return 'age10'
    elif age < 30 :
        return 'age20'
    elif age < 40 :
        return 'age30'
    elif age < 50 :
        return 'age40'
    elif age < 60 :
        return 'age50'
    else :
        return 'age60'