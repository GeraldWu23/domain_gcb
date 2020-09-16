'''
A container of url information
'''

import os
import sys
from time import sleep
from math import log

sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from dupefilter import request_fingerprint
from utilities import get_domain_url

# hyperparametres

Pc = 1  # 交叉概率
Pm = 0.5  # 突变概率  # FIXME：too large
S  = 0  # 主题相关度阈值
Pn = None  # niche 末位淘汰比例/或个数
Nh = 0  # Hub页判定阈值 TBFIX:17


class Node:
    """
    to store the information of a url.

    """
    def __init__(self, url, content=None, html=None, url_list=None, parse_time=None, score_time=None,
                 generation=None):
        """
        url : url of the webpage
        content : content without html code
        html : html code
        subj_similar : score indicating the relationship between the webpage and a subject
        url_number : number of url in its content
        url_list : a list of url in its content
        type : Hub, Authority, or irrelavant
        title
        meta_list

        parse_time_cost : time costing by parse()
        score_time_cost : time costing getting score
        rec_time : parse timestamp
        generation : the ith generation

        """
        self.url = url
        self.content = content
        self.html = html
        self.type = None  # not-related, hub, authority
        self.url_list = url_list
        self.parse_time_cost = parse_time
        self.score_time_cost = score_time
        self.generation = generation


class Domain(Node):
    def __init__(self, url, content=None, html=None, url_list=None, parse_time=None, score_time=None,
                 generation=None):
        super(Domain, self).__init__(url, content, html, url_list, parse_time, score_time, generation)
        self.visited_urls = set()  # all urls under this Domain Node
        self.Authority = set()  # all Authority pages(Node) under this Domain Node
        self.Hub = set()  # all Hub pages(Node) under this Domain Node
        self.domain_set = {get_domain_url(url)}  # all domain urls under this domain
        self.Domain_score = None
        self.score = None

    def get_score(self):
        """
        input a domain node, return the score of the node
        the larger the score, the more likely the node is related to our target

        :return: float
        """

        nA = float(len(set([n.url for n in self.Authority])))  # number of Authority nodes with unique url
        nV = float(len(self.visited_urls))  # number of visited urls

        # error sink behaviour of domain node
        if nA >= nV or nA < 0:
            return False
        try:
            self.score = log(nA) * (nA / nV) ** 0.06
        except:
            self.score = 0.01  # set a minimum score which is not 0
        return self.score  # TODO: make a smoother curve when x > 0.05


def mark_nodes(node, visited_dict):
    """
    mark a node as visited

    update the VISITED_DICT

    node : a node representing a url

    return : None
    """

    fingerprint = request_fingerprint(node)
    try:
        visited_dict[fingerprint] += 1

    except:
        visited_dict[fingerprint] = 1

    return visited_dict


def check_exist(node, visited_dict):
    """
    check if a node has been visited

    node : a node representing a url

    return : True if visited else False
    """

    fingerprint = request_fingerprint(node)
    try:
        count = visited_dict[fingerprint]
        return True
    except:
        return False
