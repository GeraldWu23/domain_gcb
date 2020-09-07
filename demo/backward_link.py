import time
from bs4 import BeautifulSoup
import requests
from urllib import parse

# 某一页的反向链接
def page_backward_link_url(url, headers):
    backward_link_url = []
    # response = requests.get(url, headers = headers)
    response = requests.get(url)
    res_status_code = response.status_code
    # print('url===',url)
    # print('res_status_code==',res_status_code)
    # with open("csdn.html", "w", encoding="utf-8") as f:
    #   f.write(response.content.decode())
        # html_str = response.content.decode()
    html_str = response.content
    mainSoup = BeautifulSoup(html_str, 'lxml')
    for td_tag in mainSoup.findAll('td', attrs={'class': 'owner title'}):
        for a_tag in td_tag.findAll('a'):
            # print(a_tag.getText())
            link = a_tag.get('href')
            if (link is not None):
                # print(td_tag.getText())
                # print(link)
                backward_link_url.append(link)
    return html_str, backward_link_url

# 所有页的反向链接
def all_page_backward_link(url_input):
    parse_result = parse.urlparse(url=url_input, scheme='http', allow_fragments=True)
    # print(parse_result.netloc)  # 获取域名
    url = "https://link.aizhan.com/" + parse_result.netloc + '/'
    headers = {
        "User_Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36",
        "Cookie": "_csrf=1d25c7af7a636c82663af5dd2a7e7bba837fc9b24871aff26e3bb8c6f35042caa%3A2%3A%7Bi%3A0%3Bs%3A5%3A%22_csrf%22%3Bi%3A1%3Bs%3A32%3A%22sTxVCp-kUc1FDI2lb0HF8izd7vhnNyE9%22%3B%7D; Hm_lvt_b37205f3f69d03924c5447d020c09192=1598233794; allSites=tech.sina.com.cn%7Clink.aizhan.com%2C0; userId=1327143; userName=xiaotianer1986%40sina.cn; userGroup=1; userSecure=bYv1Cid5g2VINbw%2F28NhKuz08%2Bs0n35WSf1zKcc7TECeYptHA0f47at4z%2Fb7Ta48LKtvzQ%3D%3D; Hm_lpvt_b37205f3f69d03924c5447d020c09192=1598234747"
        }
    html_str, backward_link_url = page_backward_link_url(url,headers)  # 获取第一页的html，以及反向链接

    ##### 从html_str 获取 pager这个节点，以便能够获得翻页的结果 ######
    page_2_to_N_url = []   # 存放第二个页面到第N个页面的所有的反向链接url
    mainSoup = BeautifulSoup(html_str, 'lxml')
    for div_tag in mainSoup.findAll('div', attrs={'class': 'pager'}):
        for ul_tag in div_tag.findAll('ul'):
            for a_tag in ul_tag.findAll('a'):
                # print(a_tag.getText())
                link = a_tag.get('href')
                if (link is not None) and link.find("javascript:") == -1:
                    # print(link)
                    page_2_to_N_url.append(link)

    ###############  不想要那么多页的反向链接 #######################
    page_2_to_N_url = page_2_to_N_url[0:2]   # 2的意思是最多取两页,从第2页开始算

    ####  遍历 第2页到第N页，抓取每页里面的url，也就是反链接 #####
    for link in page_2_to_N_url:
        time.sleep(0.4)
        _, backward_chain_url_temp = page_backward_link_url(link, headers)
        # print(link)
        # print(len(backward_chain_url_temp))
        backward_link_url += backward_chain_url_temp
    backward_link_url = list(set(backward_link_url))
    return backward_link_url



if __name__ == "__main__":
    url = 'http://sports.sina.com.cn/'
    res_back_link_list = all_page_backward_link(url)
    print('res_back_link_list===',len(res_back_link_list))