# -*- coding:utf-8 -*-
#
import re
from multiprocessing.dummy import Pool
from multiprocessing import cpu_count
import random
import requests


class Proxy(object):
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67 Safari/537.36'
    headers = {
        'User-Agent': user_agent
    }

    # 提取网页内代理的正则表达式
    proxyPattern01 = "<td[^>]*>((\d+)\.(\d+).(\d+).(\d+))</td>[\w\W]*?<td[^>]*>(\d+)</td>[\w\W]*?<td[^>]*>(HTTPS?)</td>"
    proxyPattern02 = "<td>((\d+)\.(\d+).(\d+).(\d+)):(\d+)</td>[\w\W]*?<td>(HTTPS?).*?</td>"
    proxySeedUrls = ['https://www.xicidaili.com/nn',
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
        self.proxyUrls = list()
        # 当前使用代理id，使用一个+1，滚动使用
        self.proxy_id = 0

    # 采集代理服务器配置，并验证各个服务器是否好使
    def init_proxy(self):
        self.crawler_proxy()
        self.valid_proxys()

    # 采集服务器
    def crawler_proxy(self):
        # 创建一个工作者进程池
        pool = Pool(max(1, cpu_count() - 1))
        # 在各个进程中打开url，并返回结果
        results = pool.map(self.get_page_proxy, self.proxySeedUrls)
        # 关闭进程池，等待工作结束
        pool.close()
        pool.join()
        results = [y for x in results for y in x]
        results = self.unique(results)
        self.proxyUrls = results
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
        return [(x[-1] + '://' + x[0] + ":" + x[-2]) for x in group]

    # 去重
    def unique(self, proxyUrlList):
        return list(set(proxyUrlList))

    # 验证服务器
    def valid_proxys(self):
        pool = Pool(max(1, cpu_count() - 1))
        # 在各个进程中打开url，并返回结果

        results = pool.map(self.good_proxy, self.proxyUrls)
        # 关闭进程池，等待工作结束
        pool.close()
        pool.join()
        results = [x for x in results if x]
        self.proxyUrls = results
        return results

    # 验证服务器,代理有效，返回代理配置，无效，返回None
    def good_proxy(self, proxyUrl):
        protocol = proxyUrl[:proxyUrl.find(":")].lower()
        try:
            res1 = requests.get(self.validProxyUrl, proxies={
                protocol: proxyUrl}, timeout=6, headers=self.headers)
            if res1.ok:
                return proxyUrl
        except Exception as e:
            print(e.args)
        return None

    def bad_proxy(self, proxyUrl):
        if proxyUrl in self.proxyUrls:
            self.proxyUrls.remove(proxyUrl)

    def get_proxy(self):
        self.proxy_id = (self.proxy_id + 1) % len(self.proxyUrls)
        return self.proxyUrls[self.proxy_id]

    def random_proxy(self):
        return self.proxyUrls[random.randint(0, len(self.proxyUrls))]


# 使用方法1，打印当前可以使用的代理
# proxy = Proxy()
# proxy.init_proxy()
# print(proxy.proxyUrls)

# 使用方法2，程序中使用
proxy = Proxy()
proxy.init_proxy()  # 抓取代理服务器，验证各代理服务器
print(proxy.proxyUrls)  # 打印输出当前获取的有效服务器
proxy.get_proxy()  # 循环获取代理，避免只使用一个
proxy.random_proxy()  # 随机获取代理，避免只使用一个
proxy.bad_proxy('1.1.1.1:8080')  # 标记失效代理，从代理列表中移除
