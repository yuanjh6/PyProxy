# -*- coding:utf-8 -*-
#
import re
import urllib
from multiprocessing.dummy import Pool
from multiprocessing import cpu_count

import requests


class Proxy(object):
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67 Safari/537.36'
    headers = {
        'User-Agent': user_agent
    }

    # 提取网页内代理的正则表达式
    proxyPattern01 = "<td[^>]*>((\d+)\.(\d+).(\d+).(\d+))</td>[\w\W]*?<td[^>]*>(\d+)</td>"
    proxyUrls = ['https://www.xicidaili.com/nn',
                 'https://www.xicidaili.com/nt',
                 'https://www.xicidaili.com/wn',
                 'https://www.xicidaili.com/wt',
                 'http://www.xiladaili.com/gaoni/']

    def __init__(self):
        pass

    # 采集代理服务器配置，并验证各个服务器是否好使
    def init_proxy(self):
        self.crawler_proxy()
        self.valid_proxy()

    # 采集服务器
    def crawler_proxy(self):
        # 创建一个工作者进程池
        pool = Pool(min(1, cpu_count() - 1))
        # 在各个进程中打开url，并返回结果
        results = pool.map(self.get_page_proxy, self.proxyUrls)
        # 关闭进程池，等待工作结束
        pool.close()
        pool.join()
        results = [y for x in results for y in x]
        return results

    # 网页采集的[(ip,port),,,]列表信息
    def get_page_proxy(self, url):
        group = list()
        if not url:
            return list()
        try:
            response = requests.get(url, headers=self.headers, timeout=(3, 7))
            if not response.ok:
                return list()
            html = response.content.decode('utf-8')
            group01 = re.findall(re.compile(self.proxyPattern01), html)
            group.extend(group01)
            group02 = re.findall(re.compile(self.proxyPattern02), html)
            group.extend(group02)
        except Exception as e:
            print(e.args)
        print('url:' + url + str(group))
        return [(x[0], x[-1]) for x in group]

    # 验证服务器
    def valid_proxy(self):
        pass


proxy = Proxy()
# proxy.get_page_proxy('https://www.kuaidaili.com/free/intr/')
proxy.crawler_proxy()
