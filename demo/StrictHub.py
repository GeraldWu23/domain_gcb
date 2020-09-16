import re
import requests
from utilities import isname, findChinese
from time import time

FORBIDDENNAMES = {'宋体', '博士后', '英才'}

def isStrictHub(html, threshold=5):
    """
    tell if a html string belongs to a strict hub page

    page is considered a strict hub page when：
    1. number of unique names is larger than threshold
    2. number of links smaller than 300 or the ratio of number of names
       against number of links is larger than 0.05
    3. number of elements in Chinese text is not more than 3

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
    astring = re.findall(r'<a.*?>.*?</a>', html_clean)

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
        if isname(textonlink) and textonlink not in FORBIDDENNAMES:  # the content is a Chinese name
            names.add(textonlink)
        #     print(textonlink)
        # else:
        #     print(f'not name:  {textonlink}')

    return len(names) >= threshold and \
           ((len(astring) < 300) or float(len(names))/len(astring) > 0.05)




if __name__ == '__main__':
    starttime = time()
    html = str(requests.get('https://chemeng.hebut.edu.cn/szdw/jzyg/78446.htm').content, encoding='utf-8')
    print(isStrictHub(html))

    endtime = time()
    print(f'used time is {endtime - starttime}')



