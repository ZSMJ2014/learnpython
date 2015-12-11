#!/user/bin/env python3
#-*_ coding:utf-8 -*-

__author__='liuang'
'''
async web application
'''

import logging;logging.basicConfig(level=logging.INFO)
import asyncio,os,json,time
from aiohttp import web
from datetime import datetime
import orm
def index(request):
	return web.Response(body=b'<h1>Awesome</h1>')

@asyncio.coroutine
def init(loop):
	yield from orm.create_pool(loop=loop,host='127.0.0.1',port=3306,user='www-data',password='www-data',db='awesome')
    app=web.Application(loop=loop)
    srv=yield from loop.create_server(app.make_handler(),'127.0.0.1',9000)
    logging.info('server started at http://127.0.0.1:9000...')
    return srv
loop=asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()
