import os
import sys
from time import time, localtime

sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from GeneticAlg import CrawlControl
from utilities import get_local_timestamp, format_time_period, record2mongo, get_domain_url

if __name__ == '__main__':
    starttime = time()
    ecosys = CrawlControl(start_urls=['http://mse.hit.edu.cn/',
                                      'http://fhss.dlut.edu.cn/',
                                      'https://forestry.nefu.edu.cn/',
                                      'https://gl.jlu.edu.cn/',
                                      'http://www.hrbmush.edu.cn/',
                                      'http://www.changchun.gov.cn/',
                                      'https://www.hlj.gov.cn/'],
                          # TODO: for sel_quota and cr_quota, should it
                          # TODO: be tuned according to the immediate size of population
                          sel_quota=5,
                          cr_quota=20,
                          mut_quota=2,
                          mut_rate=0.1
                          )

    recorded = set()  # recorded url
    nmongo = 0  # id in mongo, no duplication in both dataset

    with open('logger.txt', 'w') as flog:
        flog.write('')  # clean logger
        flog.write('---------configure---------\n')
        flog.write(f'sel_quota: {ecosys.sel_quota}\n')
        flog.write(f'cr_quota: {ecosys.cr_quota}\n')
        flog.write(f'mut_quota: {ecosys.mut_quota}\n')
        flog.write(f'mut_rate: {ecosys.mut_rate}\n\n')


        flog.write('start urls:\n')
        for domain_node in ecosys.population:
            flog.write(domain_node.url + '  ' + str(domain_node.score) + '\n')  # start domain nodes
            for node in domain_node.Hub:  # upload to MongoDB
                record2mongo('NortheastChina_H_04112020', str({'url': node.url, 'gen':0, 'content': node.content, 'html': node.html}), database='cv_byarea')  # gen is domain gen not evolve gen
                nmongo += 1
                recorded.add(node.url)
            for node in domain_node.Authority:
                record2mongo('NortheastChina_A_04112020', str({'url': node.url, 'gen':0, 'content': node.content, 'html': node.html}), database='cv_byarea')  # gen is domain gen not evolve gen
                nmongo += 1
                recorded.add(node.url)

    with open('strictHub_logger.txt', 'w') as fhub:
        fhub.write('')  # clean stricthub logger


    for gen in range(30):  # this is evolve gen, not domain gen
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
                flog.write(f'{get_domain_url(domain_node.url)}({domain_node.gen}): {domain_node.score}\n')
                count_strictHub += len(domain_node.Hub)
                count_Authority += len(domain_node.Authority)
                count_visited_urls += len(domain_node.visited_urls)

                for node in domain_node.Hub:  # upload to MongoDB
                    if node.url in recorded: continue
                    record_avail = record2mongo('NortheastChina_H_04112020', str({'url': node.url, 'gen':gen, 'content': node.content, 'html': node.html}), database='cv_byarea')
                    nmongo += 1
                    recorded.add(node.url)
                    if not record_avail:
                        flog.write(f'record Hubs failed:  {node.url}\n')

                for node in domain_node.Authority:
                    if node.url in recorded: continue
                    record_avail = record2mongo('NortheastChina_A_04112020', str({'url': node.url, 'gen':gen, 'content': node.content, 'html': node.html}), database='cv_byarea') 
                    nmongo += 1
                    recorded.add(node.url)
                    if not record_avail:
                        flog.write(f'record Authorities failed:  {node.url}\n')

            flog.write(f'\n\nstrictHub count is : {count_strictHub}\n')
            flog.write(f'Authority count is : {count_Authority}\n')
            flog.write(f'visited urls are : {count_visited_urls}\n')
            flog.write(f'duration : {format_time_period(starttime, endtime)}\n')
            flog.write(f'speed : {float(count_visited_urls)/float(float(endtime-starttime)/3600)} url(s)/h\n')
            flog.write(f'total visited num: {len(ecosys.visited_domain)}')
        with open('strictHub_logger.txt', 'a') as fhub:
            for domain_node in ecosys.population:
                fhub.write(f'\n\n------------{domain_node.url}-------------\n')
                for node in domain_node.Hub:
                    fhub.write(f'{node.url}\n')

    print(ecosys.visited_domain)
    endtime = time()
    print(f'\n\n{(endtime-starttime)/60} min')
