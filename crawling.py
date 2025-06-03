from bs4 import BeautifulSoup
import requests, urllib.request



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
