
from dbutils.pooled_db import PooledDB
import pymysql
import jwt
import requests
from bs4 import BeautifulSoup
import requests, urllib.request

response = requests.get("https://open.assembly.go.kr/portal/openapi/nzmimeepazxkubdpn?AGE=22&KEY=bab1a106f834406d84066a97a809b643&pSize=5&Type=json")
data1 = response.json()
print(data1['nzmimeepazxkubdpn'][1]['row'])
for i in data1['nzmimeepazxkubdpn'][1]['row'] :
    print(i['BILL_NAME'])
print(data1['nzmimeepazxkubdpn'][1]['row'][0]['DETAIL_LINK'])
url = data1['nzmimeepazxkubdpn'][1]['row'][0]['DETAIL_LINK']
url = "http://likms.assembly.go.kr/bill/billDetail.do?billId=PRC_S2A5B0Z4A1Y7X1X7F3F3E5F0D9D2C8"
res = requests.get(url)
soup = BeautifulSoup(res.text, 'html.parser')
summary = soup.find('div', {'id' : 'summaryContentDiv'})
for i in summary.find_all('br') :
    i.replace_with("\n")
summ = summary.text.strip()
d = summ.split('\n')[4:]
# for i in d[0] : print(i) #2칸 공백
for i in d :
    sdf = " ".join(d)
print(sdf)
summ = summary.get_text().strip()
datas = summ.split('\n')[4:]
datas = [i for i in datas if i != '']
for i in range(len(datas)) :
    datas[i] = datas[i].lstrip()

print(datas)
summ = "\n".join(datas)
print(summ)
