import os
import sys
from time import time, localtime

sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from GeneticAlg import CrawlControl
from utilities import get_local_timestamp, format_time_period, record2mongo, get_domain_url

if __name__ == '__main__':
    starttime = time()
    ecosys = CrawlControl(start_urls=['https://chemeng.hebut.edu.cn/',
                                      'http://chxy.cug.edu.cn/index.htm',
                                      'https://cs.xidian.edu.cn/',
                                      'http://dmse.jlu.edu.cn/index.htm',
                                      'https://cmse.szu.edu.cn/index.htm',
                                      'https://nxy.scau.edu.cn/'],
                          # TODO: for sel_quota and cr_quota, should it
                          # TODO: be tuned according to the immediate size of population
                          sel_quota=2,
                          cr_quota=5,
                          mut_quota=1,
                          mut_rate=0.2
                          )

    recorded = set()  # recorded url
    nmongo = 0  # id in mongo, no duplication in both dataset

    with open('logger.txt', 'w') as flog:
        flog.write('')  # clean logger
        flog.write('start urls:\n')
        for domain_node in ecosys.population:
            flog.write(domain_node.url + '\n')  # start domain nodes
            for node in domain_node.Hub:  # upload to MongoDB
                record2mongo('domain_gcb_Hub', str(nmongo), str({'url': node.url, 'html': node.html, 'gen': -1}))
                nmongo += 1
                recorded.add(node.url)
            for node in domain_node.Authority:
                record2mongo('domain_gcb_Authority', str(nmongo), str({'url': node.url, 'html': node.html, 'gen': -1}))
                nmongo += 1
                recorded.add(node.url)

    with open('strictHub_logger.txt', 'w') as fhub:
        fhub.write('')  # clean stricthub logger

    for gen in range(5):
        with open('logger.txt', 'a') as flog:
            flog.write(f'\n\n\n\n\n------------ generation {gen} ------------\n')
            flog.write(f'\nstart time : {get_local_timestamp()}\n')

        starttime = time()
        ecosys.evolve()  # evolve
        endtime = time()

        with open('logger.txt', 'a') as flog:
            flog.write(f'end time : {get_local_timestamp()}\n\n\n')
            flog.write('population:\n\n')
            count_strictHub = 0
            count_Authority = 0
            count_visited_urls = 0
            for domain_node in ecosys.population:
                flog.write(f'{domain_node.url}({get_domain_url(domain_node.url)}): {domain_node.score}\n')
                count_strictHub += len(domain_node.Hub)
                count_Authority += len(domain_node.Authority)
                count_visited_urls += len(domain_node.visited_urls)

                for node in domain_node.Hub:  # upload to MongoDB
                    if node.url in recorded: continue
                    record2mongo('domain_gcb_Hub', str(nmongo), str({'url':node.url, 'html':node.html, 'gen':gen}))
                    nmongo += 1
                    recorded.add(node.url)

                for node in domain_node.Authority:
                    if node.url in recorded: continue
                    record2mongo('domain_gcb_Authority', str(nmongo), str({'url':node.url, 'html':node.html, 'gen':gen}))
                    nmongo += 1
                    recorded.add(node.url)

            flog.write(f'\n\nstrictHub count is : {count_strictHub}\n')
            flog.write(f'Authority count is : {count_Authority}\n')
            flog.write(f'visited urls are : {count_visited_urls}\n')
            flog.write(f'duration : {format_time_period(starttime, endtime)}\n')
            flog.write(f'speed : {float(count_visited_urls)/max(float((endtime-starttime)/3600), 1)} url(s)/h\n')
        with open('strictHub_logger.txt', 'a') as fhub:
            for domain_node in ecosys.population:
                fhub.write(f'\n\n------------{domain_node.url}-------------\n')
                for node in domain_node.Hub:
                    fhub.write(f'{node.url}\n')

    print(ecosys.visited_domain)
    endtime = time()
    print(f'\n\n{(endtime-starttime)/60} min')
