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
    proxyPattern01 = "<td[^>]*>((\d+)\.(\d+).(\d+).(\d+))</td>[\w\W]*?<td[^>]*>(\d+)</td>[\w\W]*?<td[^>]*>(HTTPS?)</td>"
    proxyPattern02 = "<td>((\d+)\.(\d+).(\d+).(\d+)):(\d+)</td>[\w\W]*?<td>(HTTPS?).*?</td>"
    proxyUrls = ['https://www.xicidaili.com/nn',
                 'https://www.xicidaili.com/nt',
                 'https://www.xicidaili.com/wn',
                 'https://www.xicidaili.com/wt',
                 'https://proxy.mimvp.com/freeopen.php',
                 'http://www.nimadaili.com/https/',
                 'https://www.kuaidaili.com/free/intr/',
                 'http://www.nimadaili.com/http/',
                 'http://www.xiladaili.com/http/',
                 'http://www.superfastip.com/welcome/freeIP',
                 'http://www.xiladaili.com/gaoni/',
                 'http://www.qydaili.com/free/',
                 'https://www.kuaidaili.com/free/inha/',
                 'http://www.nimadaili.com/gaoni/',
                 'http://www.kxdaili.com/dailiip.html',
                 'https://www.kuaidaili.com/ops/',
                 'http://www.xiladaili.com/putong/',
                 'http://www.xiladaili.com/https/']
    # 验证代理有效性，此网页返回请求ip
    validProxyUrl = 'http://icanhazip.com/'

    def __init__(self):
        proxys = list()
        self.localIp = ''

    # 采集代理服务器配置，并验证各个服务器是否好使
    def init_proxy(self):
        try:
            res1 = requests.get(self.validProxyUrl, timeout=6, headers=self.headers)
            if res1.ok:
                self.localIp = res1.text
        except Exception as e:
            print(e.args)

        self.crawler_proxy()
        self.valid_proxys()

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
        results = self.unique(results)
        self.proxys = results
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
            html = response.text
            group01 = re.findall(re.compile(self.proxyPattern01), html)
            group.extend(group01)
            group02 = re.findall(re.compile(self.proxyPattern02), html)
            group.extend(group02)
        except Exception as e:
            print(e.args)
        print('url:' + url + str(group))
        return [(x[-1], x[0], x[-2]) for x in group]

    # 去重
    def unique(self, proxyUrlList):
        # TODO
        return proxyUrlList

    # 验证服务器
    def valid_proxys(self):
        pool = Pool(min(1, cpu_count() - 1))
        # 在各个进程中打开url，并返回结果

        results = pool.map(self.good_proxy, self.proxys)
        # 关闭进程池，等待工作结束
        pool.close()
        pool.join()
        results = [x for x in results if x]
        self.proxys = results
        return results

    # 验证服务器,代理有效，返回代理配置，无效，返回None
    def good_proxy(self, proxy):

        try:
            res1 = requests.get(self.validProxyUrl, proxies={
                proxy[0].lower(): proxy[0].lower() + "://" + proxy[1] + ":" + proxy[2]},
                                timeout=6, headers=self.headers)
            print(res1.text)
            if res1.ok and (
                    res1.text.find(proxy[1]) > -1 or self.localIp != res1.text):
                print('good proxy:' + str(proxy))
                return proxy
        except Exception as e:
            print(e.args)
        return None


proxy = Proxy()
# proxy.get_page_proxy('https://www.kuaidaili.com/free/intr/')
# proxy.crawler_proxy()
# proxy.valid_proxy(('HTTP', '124.205.155.153', '124'))
proxy.init_proxy()
print(proxy.proxys)
