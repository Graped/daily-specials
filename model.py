import os, random, sys, time

from ware import WareItem
from js import JsExecutor
from source import SeckillInfo
from history import HhHistoryParser
from network import saveHttpData

class WareManager:

    def __init__(self, isLocal=False):
        self.isLocal = isLocal
        self.wareList = []

        try:
            os.mkdir('data')
        except OSError:
            pass

    def initWareList(self):

        # Update from Jd
        self.updateJdWareList()

    def updateJdWareList(self):

        start = 26
        size = 5
        gids = [x for x in range(start, start + size)]

        for gid in gids:
            path = 'data/%d.json' % gid

            if not self.isLocal:
                ret = saveHttpData(path, 'http://coupon.m.jd.com/seckill/seckillList.json?gid=%d' % gid)
                if ret < 0: continue

            seckillInfo = SeckillInfo(path)

            for item in seckillInfo.itemList:

                wItem = WareItem()
                wItem.setSeckillItem(item)

                self.wareList.append(wItem)

            # os.remove(path)

    def updatePriceHistories(self):

        def execute(executor, title, url):
            value = 'requestPriceInfo("{}", "{}")'.format(title, url)

            return executor.execute(value)

        executor = JsExecutor('js/huihui.js')

        for ware in self.wareList:

            # Get URL for price history
            url = execute(executor, ware.name, ware.url)

            # Get price histories
            path = 'data/{}.js'.format(ware.wid)

            # Update from servers
            if not self.isLocal:
                ret = saveHttpData(path, url)
                if ret < 0: continue

            # Parse
            parser = HhHistoryParser()

            if parser.parse(path):
                historyData = parser.getHistoryData()
                if historyData:
                    ware.setHistories(historyData.histories)

            ware.update()

            # os.remove(path)

            # Sleep for a while
            if not self.isLocal:
                time.sleep(random.random())

        self.wareList.sort()

        for ware in self.wareList:
            print ware
