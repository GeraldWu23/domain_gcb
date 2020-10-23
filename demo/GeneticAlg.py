import os
import sys
from time import time, sleep
from random import sample, random, shuffle

sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from Sink_domain import parse_domain
from utilities import roulette, get_domain_url
from backward_link import page_backward_link_url as mutate

MAXSIZE = 100  # maximum size of population

# 爬行控制子系统
class CrawlControl:

    def __init__(self, start_urls=[], sel_quota=None, cr_quota=None, mut_quota=None, mut_rate=None, strictHubthres=5):  # make sure they are domain urls

        self.population = []  # processing generation
        self.visited_domain = set()  # visited domain urls
        self.sel_quota = sel_quota  # number of parents chosen in selection
        self.cr_quota = cr_quota  # number of children picked from each parent
        self.mut_quota = mut_quota  # number of mutation picked from each domain
        self.mut_rate = mut_rate  # by which rate a node mutates
        self.strictHubthres = strictHubthres
        self.poolsize = MAXSIZE  # max size of population: __eliminate() will be called when size exceeds this number

        for url in start_urls:
            try:
                if url not in self.visited_domain:
                    domain_node = parse_domain(url, self.strictHubthres)
                    domain_node.get_score()
                    self.population.append(domain_node)
                    self.visited_domain.add(domain_node.url)
            except:
                pass

    def evolve(self):
        if not self.population:
            print('nothing to evolve')
            return False

        # selection
        def __select():
            """
            select some individuals as new parents, popped from population, and the remnants are kept

            :return: new parents
            """
            if len(self.population) <= self.sel_quota:  # quota is large enough for the whole population
                return self.population

            score_list = [node.score for node in self.population]
            i_list = [i for i in range(len(self.population))]

            parents = []  # new parents
            for _ in range(self.sel_quota):
                try:
                    i_to_pop, i_population = roulette(i_list, score_list, return_ind=True)  # return (the ith item in i_list, the ith node in population)
                    i_list.pop(i_to_pop)
                    score_list.pop(i_to_pop)
                    assert len(i_list) == len(score_list)
                    parents.append(self.population.pop(i_to_pop))  # one individual of the population is chosen as new parent and picked out from population
                except:
                    print('illegal situation in selection')
                    break
            return parents

        # crossover
        def __crossover(parents):
            """
            get children from parents according to cr_quota

            :param parents: a list of domain_nodes
            :return: a list of children domain_nodes
            """
            if not parents: # selection failed
                return False
            
            children_domains = []  # children domains
            children_urls = []  # urls of children domains
            for domain in parents:
                children_urls.extend([get_domain_url(url) for url in domain.domain_set if url not in self.visited_domain])

            children_urls = list(set(children_urls))
            if len(children_urls) > self.cr_quota:  # sample urls from domains under parents
                children_urls = sample(children_urls, self.cr_quota)
            else:
                shuffle(children_urls)

            for url in children_urls:  # parse children's urls
                domain = parse_domain(url, self.strictHubthres)
                if not domain:
                    continue
                domain.get_score()
                self.visited_domain.add(get_domain_url(url))
                children_domains.append(domain)  # add child to children list

            return children_domains

        # mutation
        def __mutate(domain_list):
            """
            get mutation from random nodes

            :param: domain_list: a list of domain nodes
            :return: a list of mutation domain nodes
            """

            mutants = []  # mutants
            mutation_pool = []  # mutants' urls
            domain_list = [domain for domain in domain_list if domain]  # get rid of False
            for domain in domain_list:
                if random() > self.mut_rate:  # dont implement mutation for this domain
                    continue

                sleep(0.4)
                print(f'mutating {domain}......')
                try:
                    _, url_list = mutate(domain.url)
                    url_list = [get_domain_url(url) for url in url_list if get_domain_url(url) not in self.visited_domain]
                    if url_list:
                        mutation_pool.extend(url_list)  # add mutation urls to mutation_pool
                except:  # requests in mutate() error
                    pass

            mutation_pool = list(set(mutation_pool))  # remove duplication
            if self.mut_quota < len(mutation_pool):  # control size within set mutation quota
                mutation_pool = sample(mutation_pool, self.mut_quota)
            else:
                shuffle(mutation_pool)

            for url in mutation_pool:  # parse mutants' urls
                domain = parse_domain(url, self.strictHubthres)
                domain.get_score()
                self.visited_domain.add(domain.url)
                mutants.append(domain)  # add mutants to mutant list

            return mutants

        def __eliminate(frac=0.2):
            if len(self.population) <= self.poolsize:
                # eliminate 0.01(false requested domain)
                self.population = [node for node in self.population if node.score == 0.01]
                return True
            self.population = sorted(self.population, key=lambda domain: domain.score, reverse=False)
            self.population = self.population[round(frac * len(self.population)):]
            # eliminate 0.01(false requested domain)
            self.population = [node for node in self.population if node.score == 0.01]  # filter wrong parsed node after elimination

        # main events in an evolution
        mutants = __mutate(self.population)  # mutate before parent domain nodes are picked out
        parents = __select()
        children = __crossover(parents)

        __eliminate(0.2)  # remove the worst 20% of the population if it's too large
        self.population += mutants + children  # population changed

        # make sure they are all domain_urls
        

        return self.population





