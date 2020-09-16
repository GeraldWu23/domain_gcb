import os
import sys
from time import time

sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from GeneticAlg import CrawlControl


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

    with open('logger.txt', 'w') as f:
        f.write()  # clean logger

    for _ in range(3):
        ecosys.evolve()
        with open('logger.txt', 'a') as f:
            for domain_node in ecosys.population:
                f.write('\n\n\n')
                for node in domain_node.Hub:
                    f.write(f'{node.url}\n')
    print(ecosys.visited_domain)
    endtime = time()
    print(f'\n\n{(endtime-starttime)/60} min')
