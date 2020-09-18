import os
import sys
from time import time, localtime

sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from GeneticAlg import CrawlControl
from utilities import get_local_timestamp, format_time_period, record2mongo

if __name__ == '__main__':
    starttime = time()
    ecosys = CrawlControl(start_urls=['https://chemeng.hebut.edu.cn/',
                                      'http://chxy.cug.edu.cn/index.htm',
                                      'https://cs.xidian.edu.cn/'],
                          sel_quota=6,
                          cr_quota=5,
                          mut_quota=2,
                          mut_rate=0.2
                          )

    with open('logger.txt', 'w') as flog:
        flog.write('')  # clean logger
    with open('strictHub_logger.txt', 'w') as fhub:
        fhub.write('')  # clean stricthub logger

    for gen in range(3):
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
                flog.write(f'{domain_node.url}\n')
                count_strictHub += len(domain_node.Hub)
                count_Authority += len(domain_node.Authority)
                count_visited_urls += len(domain_node.visited_urls)

                for node in domain_node.Hub:  # upload to MongoDB
                    record2mongo('domain_gcb_Hub', node.url, node.html)
                for node in domain_node.Authority:
                    record2mongo('domain_gcb_Hub', node.url, node.html)

            flog.write(f'\n\nstrictHub count is : {count_strictHub}\n')
            flog.write(f'Authority count is : {count_Authority}\n')
            flog.write(f'visited urls are : {count_visited_urls}\n')
            flog.write(f'duration : {format_time_period(starttime, endtime)}\n')
            flog.write(f'speed : {float(count_visited_urls)/int((endtime-starttime)/3600)} url(s)/h\n')
        with open('strictHub_logger.txt', 'a') as fhub:
            for domain_node in ecosys.population:
                fhub.write(f'\n\n------------{domain_node.url}-------------\n')
                for node in domain_node.Hub:
                    fhub.write(f'{node.url}\n')

    print(ecosys.visited_domain)
    endtime = time()
    print(f'\n\n{(endtime-starttime)/60} min')
