import os
import sys
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from tld import get_fld
from bs4 import BeautifulSoup, Comment
from urllib.parse import urljoin, urlparse, urlunparse
from posixpath import normpath
import re
from utilities import text_clean, tag_clean




# 页面信息与页面相似度模块
class SubjSim:

    def __init__(self):
        pass

    # 拼接锚文本
    def myjoin(self, base, url):

        """
        : param base : 当前页面 url
        : param url : 子链接的 url(不完整)
        : return : 完整的 url 路径
        """

        url1 = urljoin(base, url)
        arr = urlparse(url1)
        path = normpath(arr[2])

        return urlunparse((arr.scheme, arr.netloc, path, arr.params, arr.query, arr.fragment))

    def get_page_info(self, url, html_str):  # 输入的是网页的html
        """
        : param url : 当前页面 url
        : param html_str : 当前页面 html
        : return : 返回 page_info_dic，里面包含当前网页的基本信息。
        该模块实现功能：
        返回：1. 当前页面URL； 2. 域名； 3. 当前页面标题； 4. meta_list； 5. 子链接队列； 6.子链接数量； 7.其他内容; 8. 锚文本队列； 9. H页还是A页
        """

        page_info_dict = {'html_str': html_str, 'domain': None, 'url': url}  # 返回网页的信息汇总

        # 提取域名
        parseresult = urlparse(url)
        domain_url = parseresult[0] + '://' + parseresult[1]
        page_info_dict['domain'] = domain_url

        # 提取 url_list
        soup = BeautifulSoup(html_str, "lxml")  # 解析正文块
        tags = soup.select("a")

        url_list = []  # 储存子 url
        url_text_list = []  # 锚文本队列
        count = 0  # 调试控制
        for tag in tags:
            #count += 1
            #if count > 5:
            #    break
            try:
                url_text_list.append(tag.text)
                html_str = re.sub(tag.text, '', html_str)
                try:
                    child_url = self.myjoin(url, tag['href'])
                    url_list.append(child_url)
                except:
                    child_url = tag["href"]
                    url_list.append(child_url)
            except:
                continue

        string_content = soup.text
        page_info_dict['string_content'] = text_clean(string_content)
        page_info_dict['url_list'] = url_list  # 子url_list
        page_info_dict['url_text_list'] = url_text_list
        page_info_dict['url_number'] = len(tags)  # 子 url 数量

        return page_info_dict


# 测试模块
if __name__=="__main__":
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36'}
    pass
