import os
import sys
import redis
import subprocess
import json
from time import time, sleep
import datetime
import numpy as np

sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from pageCollAnali import SubjSim
from spiders.node import Node, Domain, mark_nodes, check_exist
from StrictHub import isStrictHub
from utilities import get_domain_url
from settings import REDIS_PORT, REDIS_HOST


def parse(url_list):
    """
    input url_list output url info lists

    url_list = url list
    """

    parsed_urls = []
    content_list = []
    html_list = []
    offspring_list = []
    parse_time_list = []
    score_time_list = []
    rec_time_list = []

    # request html (or other info) from url
    # TODO: dupefilter implemented by scratch
    # push urls to redis
    print(f'{REDIS_HOST} {REDIS_PORT} in Sink')
    #sleep(5)
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)  # port=6379 in pc, 10031 in server
    r.delete('MySpider:start_urls')  # clean redis
    r.delete("MySpider:items")  # clean redis
    for url in url_list:
        print('-----------------')
        r.lpush('MySpider:start_urls', url)
    print(f'\n\npush end, {len(url_list)}\n\n')

    # info containers
    urls_from_scrapy = []
    html_strs_from_scrapy = []

    # crawl info from urls with scrapy-redis
    # worker = subprocess.Popen("fab crawlMySpider".split())
    worker = subprocess.Popen("scrapy crawl MySpider".split())  # FIXME

    while worker.poll() is None:  # not finished
        while r.llen("MySpider:items") > 0:
            info_dict_from_scrapy = json.loads(r.lpop('MySpider:items'))
            if not info_dict_from_scrapy['html']:
                continue

            urls_from_scrapy.append(info_dict_from_scrapy['url'])
            html_strs_from_scrapy.append(info_dict_from_scrapy['html'])

    while r.llen("MySpider:start_urls") > 0:  # crawler killed by error
        # url = r.lpop("MySpider:start_urls")  # FIXME: should the error url be popped: time it
        print(f'\n\n\n\n\n\n\nencountering an error url: {url}')
        #worker = subprocess.Popen("fab crawlMySpider".split())
        worker = subprocess.Popen("scrapy crawl MySpider".split())  # FIXME

        while worker.poll() is None:  # not finished
            while r.llen("MySpider:items") > 0:
                info_dict_from_scrapy = json.loads(r.lpop('MySpider:items'))
                if not info_dict_from_scrapy['html']:
                    continue

                urls_from_scrapy.append(info_dict_from_scrapy['url'])
                html_strs_from_scrapy.append(info_dict_from_scrapy['html'])

    print('------------------------------------------\n'
          '------------------------------------------\n'
          '---------   scrapy-redis end   -----------\n'
          '------------------------------------------\n'
          '------------------------------------------\n'
          )

    while r.llen("MySpider:items") > 0:
        info_dict_from_scrapy = json.loads(r.lpop('MySpider:items'))
        if not info_dict_from_scrapy['html']:
            continue

        urls_from_scrapy.append(info_dict_from_scrapy['url'])
        html_strs_from_scrapy.append(info_dict_from_scrapy['html'])

    # get other info from html strings
    for url, html_str in zip(urls_from_scrapy, html_strs_from_scrapy):
        # try:
        parse_start = time()
        subjsim = SubjSim()
        page_info_dict = subjsim.get_page_info(url, html_str)
        parse_end = time()

        parsed_urls.append(url)
        html_list.append(html_str)
        content_list.append(page_info_dict['string_content'])
        offspring_list.append(page_info_dict['url_list'])
        parse_time_list.append(parse_end - parse_start)
        rec_time_list.append(str(datetime.datetime.now()).split('.')[0])
        # except:
        #     print("didn't get info")
        #     print(html_str, type(html_str))
        #     continue

    assert np.mean([float(len(li)) for li in [parsed_urls, html_list, content_list,
                                              offspring_list, parse_time_list, rec_time_list]])\
           == float(len(parsed_urls))  # lengths not aligned means getting exceptions

    print(f'successful return urls are {parsed_urls}')
    return parsed_urls, content_list, html_list, offspring_list #, \
           # parse_time_list, score_time_list, rec_time_list


def parse_node(node, forbidden=None):

    # make sure node is a Node
    if type(node) == str:
        # build strictHub Node
        url = [node]  # the node is actually a url
        parsed_urls, content_list, html_list, offspring_list = parse(url)
        node = Node(url=parsed_urls[0], content=content_list[0], html=html_list[0],  # get parent node
                           url_list=list(set(offspring_list[0])))
    else:
        pass

    # filter banned urls
    if forbidden:
        url_list = [url for url in node.url_list if url not in forbidden]
    else:
        url_list = node.url_list

    # all the other offspring nodes are regarded as authority nodes
    parsed_urls, content_list, html_list, offspring_list = parse(url_list)
    offspring_nodes = [Node(url=url, content=content, html=html, url_list=url_list)
                 for url, content, html, url_list in zip(parsed_urls, content_list, html_list, offspring_list)]

    return offspring_nodes


def parse_domain(domain_url):

    generation = 0

    # get domain url
    domain_url = get_domain_url(domain_url)

    # build domain Node
    domain_url = [domain_url]  # to fit parse()
    #try:
    parsed_urls, content_list, html_list, offspring_list = parse(domain_url)
    #except:
    #    print('gen 0 parse error')
    #    return False

    # request domain node error
    if not html_list[0]:
        print('domain parse fail')
        return False
    domain_node = Domain(url=parsed_urls[0], content=content_list[0], html=html_list[0],
                         url_list=list(set(offspring_list[0])), generation=generation)
    domain_node.visited_urls.add(domain_url[0])  # mark as visited url

    # parse domain get dep1
    generation += 1
    dep1_nodes = parse_node(domain_node)
    if isStrictHub(domain_node.html, threshold=5):
        domain_node.Hub.add(domain_node)
        domain_node.type = 'Hub'
        for node in dep1_nodes:
            node.generation = generation
            node.type = 'Authority'
            domain_node.visitied_urls.add(node.url)  # mark depth 1 authority urls as visited
            domain_node.Authority.add(node)  # mark depth 1 authority nodes as authority nodes under this domain node
    else:
        domain_node.type = 'not-related'
        for node in dep1_nodes:
            node.generation = generation
            node.type = 'Authority'
            domain_node.visited_urls.add(node.url)  # mark depth 1 authority urls as visited

    # return domain_node, dep1_nodes

    # sink
    next_parents = dep1_nodes  # parent of next generation
    satisfied = False
    # while(satisfied == False):  # TODO:max depth
    for _ in range(1):
        #print(f'in loop!\nparent is:')
        #print(next_parents)
        #sleep(20)
        generation += 1
        if satisfied:  # there's a Hub page found besides the home page
            break
        parents = next_parents
        next_parents = []
        for node in parents:
            if isStrictHub(node.html, threshold=5):
                satisfied = True
                domain_node.Hub.add(node)
                authority = parse_node(node, domain_node.visited_urls)  # parse nodes if not visited
                for authority_node in authority:
                    node.generation = generation
                    node.type = 'Authority'
                    domain_node.visited_urls.add(authority_node.url)
                    domain_node.Authority.add(authority_node)
            else:
                not_authority_list = parse_node(node, domain_node.visited_urls)
                for not_authority_node in not_authority_list:
                    node.type = 'not_related'
                    node.generation = generation
                    # TODO: if an Authority is exposed under a non-StrictHub page, it will be regards as not-related permanently
                    domain_node.visited_urls.add(not_authority_node.url)
                next_parents.extend(not_authority_list)

        next_parents = [node for node in next_parents if node.url not in domain_node.visited_urls]

    return domain_node

if __name__ == '__main__':

    start = time()
    n = parse_domain("https://cs.xidian.edu.cn/")
    end = time()
    print(f'time used is {end - start}s.')
