from time import sleep
from fabric.api import cd, run, env, parallel, execute
from fabric.context_managers import settings as fsettings, hide as fhide
import subprocess
import socket
CONTEXTPATH = '~/domain_gcb/'

env.hosts = ['hjj@172.16.7.20',
             'hjj@172.16.7.22',
             'hjj@172.16.7.23',
             'hjj@172.16.7.24',
             'hjj@172.16.7.25',
             'hjj@172.16.7.26']
env.password = 'EF317F870B@**'
env.parallel = True



@parallel
def crawlMySpider():
    #with fsettings(
    #    fhide('warnings', 'running', 'stdout', 'stderr'),
    #    warn_only=True
    #):
    with cd(CONTEXTPATH):
        #with fsettings(
        #    fhide('stdout', 'stderr'),
        #    # warn_only=True
        #):

        worker0 = subprocess.Popen("scrapy crawl MySpider".split())
        worker1 = subprocess.Popen("scrapy crawl MySpider".split())
        worker2 = subprocess.Popen("scrapy crawl MySpider".split())

        worker0.wait()
        worker1.wait()
        worker2.wait()
        #run('python run.py')


  

