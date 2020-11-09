import re
import requests
from utilities import isname, findChinese, get_domain_url, legalurl
from time import time

with open('./forbiddenword.txt', 'r', encoding='utf-8') as f:
    FORBIDDENNAMES = set([word.strip() for word in f.readlines()])


def isStrictHub(html, threshold=5):
    """
    tell if a html string belongs to a strict hub page

    page is considered a strict hub page when：
    1. number of unique names is larger than threshold
    2. number of links smaller than 300 or the ratio of number of names
       against number of links is larger than 0.05
    3. number of elements in Chinese text is not more than 3 and less than 2

    :param html: html string
    :param threshold: more than how many names untill the webpage considered a hub page
    :return: True if it's considered a strict hub page
    """

    # no input string
    if not html:
        print('NO HTML FOUND')
        return False

    # format html string and find all 'a' string
    html = html.lower()
    html_clean = ' '.join(html.split())
    astring = re.findall(r'<a href=.*?>.*?</a>', html_clean)

    # def containers
    names = set()
    textlist = []

    # extract all Chinese elements
    for ahref in astring:  # for all <a></a>
        for string in re.findall(r'>.+?<', ahref):  # between start tag and end tag
            Chineseintext = findChinese(string)
            if Chineseintext:
                if len(Chineseintext) <= 3:  # e.g. 葛昌纯1968年， 院士-张清杰，院士-张-联盟
                    textlist.extend(Chineseintext)

    # find all Chinese names from those elements
    textlist = list(set([i for i in textlist if i]))
    for textonlink in textlist:
        # the content is a Chinese name
        if isname(textonlink) and textonlink not in FORBIDDENNAMES and len(textonlink) > 1:
            names.add(textonlink)
            print(textonlink)  # FIXME
        # else:
        #     print(f'not name:  {textonlink}')

    return len(names) >= threshold and \
           ((len(astring) < 300) or float(len(names))/len(astring) > 0.05)


def get_name_urls(url, html):
    """
    get name urls from a strictHub page

    :param url: url of this page
    :param html: html string
    :return: a list of name urls
    """

    head = get_domain_url(url)

    # format html string and find all 'a' string
    html_clean = ' '.join(html.split())
    astring = re.findall(r'<a href=.*?>.*?</a>', html_clean)  # a href block
    print(astring)
    # def containers
    url_list = []

    for ahref in astring:
        textlist = re.findall(r'>.+?<', ahref)
        text = ''.join(textlist)
        Chinese_list = findChinese(text)
        if Chinese_list and sum([isname(chinese) for chinese in Chinese_list]) > 0:
            try:
                url_text = re.findall(r'<a href=.+?>', ahref)[0].split()[1][6:-1]
                name_url = legalurl(url_text, head)
                print(name_url)
                url_list.append(name_url)
            except:
                pass


if __name__ == '__main__':
    starttime = time()
    url = 'http://www.ccerdao.gov.cn/wzdt/'
    html = str(requests.get(url).content, encoding='utf-8')
    # get_name_urls(url, html)
    print(isStrictHub(html))
    endtime = time()
    print(f'used time is {endtime - starttime}')



