import re
import jieba.posseg as pseg
from bs4 import BeautifulSoup
from urllib.parse import urlparse


def isname(text):
    '''
    define if a text is a Chinese name if it's within 3 characters(there are names have 4 char but more linkly to include non-name str)

    :param text: text to define(if it's a name)
    :return: bool
    '''
    def __name_in(text):
        '''

        :param text: text to recognise if there is a least one name in
        :return: bool
        '''
        words = pseg.cut(text)
        contain_pers_bool = False
        for w in words:
            if w.flag == 'nr':
                contain_pers_bool = True
        return contain_pers_bool

    return __name_in(text) and len(text) <= 3


def findChinese(text):
    '''
    find all Chinese characters and join them to a string

    :param text
    :return: a string representing all Chinese
    '''

    chinese_pattern = re.compile(u'[\u4e00-\u9fa5]')
    res =  ''.join(re.findall(chinese_pattern, text))
    if not res:
        return None
    words = pseg.cut(res)
    return [w.word for w in words]


def text_clean(sentence):
    sentence = re.sub(r" ", "", sentence)
    sentence = sentence.replace('\r', '').replace('\n', '').replace('\t', '')
    sentence = re.sub(r"\s+", "", sentence)
    sentence = re.sub(r"\u3000", '', sentence)
    sentence = re.sub(r"\r", '', sentence)
    sentence = re.sub(r"[0-9\s+\.\!\/_,$%^*()?;；:-【-——丨〔：】+\"\']+|[+——！，;:。？、~@#￥%……&*（）]+", " ", sentence)

    return sentence


def tag_clean(html_str):
    html = BeautifulSoup(html_str, 'lxml')
    [s.extract() for s in html.findAll('meta')]
    [s.extract() for s in html.findAll('script')]
    [s.extract() for s in html.findAll('link')]
    [s.extract() for s in html.findAll('noscript')]
    [s.extract() for s in html.findAll('img')]
    [s.extract() for s in html.findAll('style')]
    [s.extract() for s in html.findAll('input')]
    [s.extract() for s in html.findAll('iframe')]
    [s.extract() for s in html.findAll('br')]
    comments = html.findAll(text=lambda text: isinstance(text, Comment))
    [s.extract() for s in comments]

    return str(html)


def get_domain_url(url):
    parseresult = urlparse(url)
    domain_url = parseresult[0] + '://' + parseresult[1]
    return domain_url


if __name__ == '__main__':

    p1 = '帮会建了徽信群 没在群里的加下徽信:[30109552300]，晚上群里有活动通知大家，(抢资源)，争地盘，谢谢配合。i love you '
    p2 = '<a><img>sdfasgdfgf</img><div>sdfsdfsdfasdgf</div><span>徐璋勇</span></a>'

    pre = re.compile(u'[\u4e00-\u9fa5]')
    res = re.findall(pre, p2)
    res1 = ''.join(res)
    print(res1)

