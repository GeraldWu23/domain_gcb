import re
import requests
from utilities import isname, findChinese
from time import time

def isStrictHub(html, threshold=5):
    """
    tell if a html string belongs to a strict hub page

    :param html: html string
    :param threshold: more than how many names untill the webpage considered a hub page
    :return: True if it's considered a strict hub page
    """
    if not html:
        print('NO HTML FOUND')
        return False

    html = html.lower()
    html_clean = ' '.join(html.split())
    astring = re.findall(r'<a.*?>.*?</a>', html_clean)
    names = set()
    textlist = []

    for ahref in astring:  # for all <a></a>
        for string in re.findall(r'>.+?<', ahref):  # between start tag and end tag
            Chineseintext = findChinese(string)
            if Chineseintext:
                if len(Chineseintext) <= 3:  # e.g. 葛昌纯1968年， 院士-张清杰，院士-张-联盟
                    textlist.extend(Chineseintext)

    # textlist = [findChinese(string) for string in re.findall(r'<.+?>.+?</', ahref) if string != '> <' or string != '']
    textlist = list(set([i for i in textlist if i]))
    #print(textlist)
    for textonlink in textlist:
        if isname(textonlink):  # the content is a Chinese name
            names.add(textonlink)
            #print(textonlink)
        else:
            pass
            #print(f'not link: {textonlink}')

    return len(names) >= threshold  # page is considered a strict hub page when number of unique names is larger than threshold


if __name__ == '__main__':
    starttime = time()
    html = str(requests.get('http://www.gutian.gov.cn/').content, encoding='utf-8')
    print(isStrictHub(html))

    endtime = time()
    print(f'used time is {endtime - starttime}')
