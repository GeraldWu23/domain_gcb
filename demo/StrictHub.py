import re
import requests
from utilities import isname, findChinese
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
            #print(textonlink)  # FIXME
        #else:
            #print(f'not name:  {textonlink}')

    return len(names) >= threshold and \
           ((len(astring) < 300) or float(len(names))/len(astring) > 0.05)




if __name__ == '__main__':
    starttime = time()
    html = str(requests.get('https://nxy.scau.edu.cn/484/list.htm').content, encoding='utf-8')
    print(isStrictHub(html))

    endtime = time()
    print(f'used time is {endtime - starttime}')



