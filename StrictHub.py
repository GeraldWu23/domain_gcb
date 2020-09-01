import re

import requests

from utilities import isname, findChinese


def isStrictHub(html, threshold=5):
    """
    tell if a html string belongs to a strict hub page

    :param html: html string
    :param threshold: more than how many names untill the webpage considered a hub page
    :return: True if it's considered a strict hub page
    """

    html_clean = ' '.join(html.split())
    astring = re.findall(r'<a.*?>.*?</a>', html_clean)
    names = set()

    for ahref in astring:  # for all <a></a>
        textlist = [findChinese(string) for string in re.findall(r'>.+?<', ahref) if string != '> <']  # content list in this <a></a>
        if textlist:
            textonlink = textlist[-1].strip('> <')  # name might appear more than one time
            if isname(textonlink):  # the content is a Chinese name
                names.add(textonlink)
                print(textonlink)
            else:
                print(f'not link: {textonlink}')

    return len(names) > threshold  # page is considered a strict hub page when number of unique names is larger than threshold


if __name__ == '__main__':
    html = str(requests.get('https://mse.ustc.edu.cn/3334/list.htm').content, encoding='utf-8')
    print(isStrictHub(html))
