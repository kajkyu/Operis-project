from bs4 import BeautifulSoup
import requests, urllib.request



url = "http://likms.assembly.go.kr/bill/billDetail.do?billId=PRC_Z2X5V0W5E0F8D1D5C4A3B1W8X3V7W8"
res = requests.get(url)
soup = BeautifulSoup(res.text, 'html.parser')
data = soup.find('div', {'id' : 'summaryContentDiv'})
for i in data.find_all('br') :
    i.replace_with("\n")
summary = data.get_text().strip()

d = summary.split('\n')[4:]
for i in range(len(d)) :
    d[i] = d[i].lstrip()

print(d)

# sdf = " ".join(d)
# summ = data.text
# print(len(summ.split('\n')))
# for i in summ.split('\n') :
#     print(i)
    



