import os
import sys
import redis
import subprocess
import json
from time import time, sleep
import datetime
import numpy as np
from copy import deepcopy
from math import log

sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from pageCollAnali import SubjSim
from spiders.node import Node, Domain, mark_nodes, check_exist
from StrictHub import isStrictHub
from utilities import get_domain_url, filtered_url
from settings import REDIS_PORT, REDIS_HOST



def parse(url_list):
    """
    input url_list output url info lists

    :param url_list:
    :return: website info lists
    """

    # filter urls to ignore
    url_list = list(filter(lambda x: filtered_url(x), url_list))

    # containers of info
    parsed_urls = []
    content_list = []
    html_list = []
    offspring_list = []
    parse_time_list = []
    rec_time_list = []
    urls_from_scrapy = []
    html_strs_from_scrapy = []

    # request html (or other info) from url
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)  # push urls to redis  port=6379 in pc, 10031 in server
    r.delete('MySpider:start_urls')  # clean redis
    r.delete("MySpider:items")  # clean redis
    for url in url_list:
        print('-----------------')
        r.lpush('MySpider:start_urls', url)
    print(f'\n\npush end, {len(url_list)}\n\n')

    # crawl info from urls with scrapy-redis
    worker = subprocess.Popen("fab crawlMySpider".split())
    #worker = subprocess.Popen("scrapy crawl MySpider".split())  # FIXME

    while worker.poll() is None:  # not finished
        while r.llen("MySpider:items") > 0:
            info_dict_from_scrapy = json.loads(r.lpop('MySpider:items'))
            if not info_dict_from_scrapy['html']:
                continue

            urls_from_scrapy.append(info_dict_from_scrapy['url'])
            html_strs_from_scrapy.append(info_dict_from_scrapy['html'])

    while r.llen("MySpider:start_urls") > 0:  # crawler killed by error
        # print(f'\n\n\n\n\n\n\nencountering an error url: {url}')
        worker = subprocess.Popen("fab crawlMySpider".split())
        #worker = subprocess.Popen("scrapy crawl MySpider".split())  # FIXME

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
        try:
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
        except:
            print("didn't get info")
            print(html_str, type(html_str))
            continue

    assert np.mean([float(len(li)) for li in [parsed_urls, html_list, content_list,
                                              offspring_list, parse_time_list, rec_time_list]])\
           == float(len(parsed_urls))  # lengths not aligned means getting exceptions

    print(f'successful return urls are {parsed_urls}')
    return parsed_urls, content_list, html_list, offspring_list #, \
           # parse_time_list, score_time_list, rec_time_list


def parse_node(node, forbidden=None):
    """
    given a node or a string, return a list of node of its 1-gen offsprings

    :param node: a node whose siblings to parse
    :param forbidden: a forbidden list of urls this function ignores
    :return: a list of node
    """

    # make sure node is a Node
    if type(node) == str:
        # build strictHub Node
        url = [node]  # the node is actually a url
        parsed_urls, content_list, html_list, offspring_list = parse(url)
        node = Node(url=parsed_urls[0], content=content_list[0], html=html_list[0],  # get parent node
                           url_list=list(set(offspring_list[0])))


    # filter banned urls
    if forbidden:
        url_list = [url for url in node.url_list if url not in forbidden]

    else:
        url_list = node.url_list

    # all the other offspring nodes are regarded as authority nodes
    parsed_urls, content_list, html_list, offspring_list = parse(url_list)

    offspring_nodes = [Node(url=url, content=content, html=html, url_list=list(set(url_list)))
                       for url, content, html, url_list in zip(parsed_urls, content_list, html_list, offspring_list)]

    return offspring_nodes


def parse_domain(domain_url, threshold=5):
    """
    input a string representing a domain url, return a node containing the information in this domain

    :param domain_url: a string representing a url
    :param threshold: strictHub recognition threhosld
    :return: a node representing this domain with its information
    """
    generation = 0

    # get domain url
    domain_url = get_domain_url(domain_url)

    # build domain Node
    domain_url = [domain_url]  # to fit parse()
    try:
        parsed_urls, content_list, html_list, offspring_list = parse(domain_url)
        _ = html_list[0]
    except:
        print('gen 0 parse error: domain_url')
        sleep(10)
        return False

    domain_node = Domain(url=parsed_urls[0], content=content_list[0], html=html_list[0],
                         url_list=list(set(offspring_list[0])), generation=generation)

    # parse domain get nodes with depth 1
    generation += 1
    domain_node.visited_urls.add(domain_node.url)  # mark as visited url and it will not be in dep1_nodes
    dep1_nodes = parse_node(domain_node, domain_node.visited_urls)
    for url in domain_node.url_list:  # in case that url in url_list different from that in parsed_list
        domain_node.visited_urls.add(url)
    if isStrictHub(domain_node.html, threshold=threshold):
        domain_node.Hub.add(domain_node)
        domain_node.type = 'Hub'
        for node in dep1_nodes:
            node.generation = generation
            node.type = 'Authority'
            domain_node.visited_urls.add(node.url)  # mark depth 1 authority urls as visited
            domain_node.Authority.add(node)  # mark depth 1 authority nodes as authority nodes under this domain node
    else:
        domain_node.type = 'not_related'  # not strictHub and domain_node is not considered to be Authority
        for node in dep1_nodes:
            node.generation = generation
            node.type = None  # could be strictHub
            domain_node.visited_urls.add(node.url)  # mark depth 1 authority urls as visited

    # sink
    next_parents = dep1_nodes  # parent of next generation
    satisfied = False
    for _loop in range(2):
        generation += 1
        if satisfied and _loop > 1:  # there's a Hub page found besides the home page
            break
        parents = next_parents  # parent of this generation
        next_parents = []
        ul = [node.url for node in parents]
        for node in parents:
            if not node.type and isStrictHub(node.html, threshold=threshold):
                satisfied = True
                domain_node.Hub.add(node)
                node.type = 'Hub'
                authority = parse_node(node, domain_node.visited_urls)  # parse offspring nodes if not visited, not affecting parent node
                for url in node.url_list:  # in case that url in url_list different from that in parsed_list
                    domain_node.visited_urls.add(url)
                for authority_node in authority:
                    authority_node.type = 'Authority'
                    authority_node.generation = generation
                    domain_node.visited_urls.add(authority_node.url)
                    domain_node.Authority.add(authority_node)
            else:  # parent nodes from second loop or after start here
                node.type = 'not_related'  # not Authority and not strictHub
                not_authority_list = parse_node(node, domain_node.visited_urls)  # get offsprings of this not-strictHub
                for url in node.url_list:  # in case that url in url_list different from that in parsed_list
                    domain_node.visited_urls.add(url)
                for not_authority_node in not_authority_list:
                    # TODO: if an Authority is exposed under a non-StrictHub page, it will be regards as not-related permanently
                    not_authority_node.generation = generation
                    domain_node.visited_urls.add(not_authority_node.url)
                    if isStrictHub(not_authority_node.html, threshold=threshold):  # if this not-authority node is a strictHub
                        domain_node.Hub.add(not_authority_node)
                        not_authority_node.type = 'Hub'
                        authority = parse_node(node, domain_node.visited_urls)  # parse nodes if not visited
                        for url in node.url_list:  # in case that url in url_list different from that in parsed_list
                            domain_node.visited_urls.add(url)
                        for authority_node in authority:
                            authority_node.type = 'Authority'
                            authority_node.generation = generation + 1
                            domain_node.visited_urls.add(authority_node.url)
                            domain_node.Authority.add(authority_node)
                    else:  # if this not authority node is not strictHub either, push it to next parent
                        not_authority_node.type = 'not_related'
                        next_parents.append(not_authority_node)
        next_parents = [node for node in next_parents if node.url not in domain_node.visited_urls]


    # potential Hub in Authority
    for _ in range(1):
        generation = generation + 1
        for node in deepcopy(domain_node.Authority):
            if isStrictHub(node.html, threshold):  # this Authority node is also a Hub node
                domain_node.Hub.add(node)
                node.type = 'strictHub and Authority'
                authority_list = parse_node(node, domain_node.visited_urls)  # parse nodes if not visited
                for url in node.url_list:  # in case that url in url_list different from that in parsed_list
                    domain_node.visited_urls.add(url)
                for authority_node in authority_list:
                    authority_node.generation = generation
                    authority_node.type = 'Authority'
                    domain_node.visited_urls.add(authority_node.url)
                    domain_node.Authority.add(authority_node)

    # add outter domains under this domain
    for url in domain_node.visited_urls:
        domain_node.domain_set.add(get_domain_url(url))

    # get domain score
    domain_node.get_score()

    return domain_node


if __name__ == '__main__':

    start = time()
    HUT = parse_domain("https://chemeng.hebut.edu.cn/")
    end = time()
    print(f'time used is {end - start}s.')

    start = time()
    CUG = parse_domain("http://chxy.cug.edu.cn/index.htm")
    end = time()
    print(f'time used is {end - start}s.')

    start = time()
    XDU = parse_domain("https://cs.xidian.edu.cn/")
    end = time()
    print(f'time used is {end - start}s.')
