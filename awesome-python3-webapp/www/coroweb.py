#!/usr/bin/env python3
#-*- coding:utf-8 -*-
__author__='liuang'

import asyncio,os,inspect,logging,functools
from urllib import parse
from aiohttp import web
from apis import APIError

#get 和post为修饰方法，主要是为对象上加上'__method__'和'__route__'属性
#为了把我们定义的url实际处理方法，以get请求或post请求区分
def get(path):
    '''
    Define decorator @get('/path)
    '''
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args,**kw):
            return func(*args,**kw)
        wrapper.__method__='GET'
        wrapper.__route__=path
        return wrapper
    return decorator

def post(path):
    '''
    Define decorator @post('/path')
    '''
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args,**kw):
            return func(*args,**kw)
        wrapper.__method__='POST'
        wrapper.__route__=path
        return wrapper
    return decorator
#关于inspect.Parameter的kind类型有5种：
#POSITIONAL_ONLY   只能是位置参数
#POSITINAL_OR_KEYWORD 可以是位置参数也可以是可变参数（list,tuple）
#VAR_POSITIONAL  相当于是*args
#KEYWORD_ONLY   关键字参数且提供了key，相当于是*，key
#VAR_KEYWORD   相当于是**kw
#
#如果url处理函数需要传入关键字参数，且默认是空的话，获取这个key
def get_required_kw_args(fn):
    args=[]
    params=inspect.signature(fn).parameters
    for name,param in params.items():
        if param.kind==inspect.Parameter.KEYWORD_ONLY and param.default==inspect.Parameter.empty:
            args.append(name)
    return tuple(args)
#如果url处理函数需要传入关键字参数，获取这个key
def get_named_kw_args(fn):
    args=[]
    params=inspect.signature(fn).parameters
    for name,param in params.items():
        if param.kind==inspect.Parameter.KEYWORD_ONLY:
            args.append(name)
    return tuple(args)
#如果url处理函数需要传入关键字参数，返回True
def has_name_kw_args(fn):
    params=inspect.signature(fn).parameters
    for name,param in params.items():
        if param.kind==inspect.Parameter.KEYWORD_ONLY:
            return True
#如果url处理函数的参数是**kw，返回True
def has_var_kw_arg(fn):
    params=inspect.signature(fn).parameters
    for name,param in params.items():
        if param.kind==inspect.Parameter.VAR_KEYWORD:
            return True
#如果url处理函数的最后一个参数是request，返回True
def has_request_arg(fn):
    sig=inspect.signature(fn)
    params=sig.parameters
    found=False
    for name,param in params.items():
        if name=='request':
            found=True
            continue
        if found and (param.kind!=inspect.Parameter.VAR_POSITIONAL and param.kind!=inspect.Parameter.KEYWORD_ONLY and param.kind!=inspect.Parameter.VAR_KEYWORD):
            raise ValueError('request parameter must be the last named parameter in function:%s%s'%(fn.__name__,str(sig)))
    return found
#RequestHandler目的就是从URL函数中分析其需要接受的参数，从request中获取必要的参数，调用URL函数
class RequestHandler(object):
    def __init__(self,app,fn):
        self._app=app
        self._func=fn
        self._has_request_arg=has_request_arg(fn)
        self._has_var_kw_arg=has_var_kw_arg(fn)
        self._has_named_kw_args=has_name_kw_args(fn)
        self._named_kw_args=get_named_kw_args(fn)
        self._required_kw_args=get_required_kw_args(fn)
    @asyncio.coroutine
    def __call__(self,request):
        kw=None
        #如果处理函数需要传入特定key的参数或者可变参数的话
        if self._has_var_kw_arg or self._has_named_kw_args or self._required_kw_args:
            #如果是post请求，则读请求的body
            if request.method=='POST':
                if not request.conent_type:
                    return web.HTTPBadRequest('Missing Content-Type.')
                ct=request.conent_type.lowwer()
                if ct.startswith('application/json'):
                    #把request的body，按json的方式输出为一个字典
                    params=yield from request.json()
                    if not isinstance(params,dict):
                        return web.HTTPBadRequest('JSON body must be object.')
                    kw=params
                elif ct.startswith('application/x-www-form-urlencoded') or ct.startswith('multipart/form-data'):
                    params=yield from request.post()
                    kw=dict(**params)
                else:
                    return web.HTTPBadRequest('Unsupported Content-Type:%s'%request.conent_type)
            #如果是get请求，则读请求url字符串
            if request.method=='GET':
                qs=request.query_string
                if qs:
                    kw=dict()
                    for k,v in parse.parse_qs(qs,True).items:
                        kw[k]=v[0]
        #如果kw为空的话，kw设置为request.match_info
        if kw is None:
            kw=dict(**request.match_info)
        else:
            #如果kw有值的话
            #如果处理方法需要传入**kw，且需要传入关键字参数
            if not self._has_var_kw_arg and self._named_kw_args:
                #remove all unamed kw:
                copy=dict()
                #从kw中筛选出url处理方法需要传入的参数
                for name in self._named_kw_args:
                    if name in kw:
                        copy[name]=kw[name]
                kw=copy
            #check named arg:
            for k,v in request.match_info.items():
                if k in kw:
                    logging.warning('Duplicate arg name in named arg and kw args:%s'%k)
                kw[k]=v
        if self._has_request_arg:
            kw['request']=request
        #check required kw:
        if self._required_kw_args:
            for name in self._required_kw_args:
                if not name in kw:
                    return web.HTTPBadRequest('Missing argument:%s'%name)
        logging.info('call with args:%s' % str(kw))
        try:
            r=yield from self._func(**kw)
            return r
        except APIError as e:
            return dict(error=e.error,data=e.data,message=e.message)
#添加静态页面的路径
def add_static(app):
    path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'static')
    app.router.add_static('/static/',path)
    logging.info('add static %s=>%s' % ('/sstatic/',path))

def add_route(app,fn):
    #获取'__method__'和'__route__'属性，如果有空则抛出异常
    method=getattr(fn,'__method__',None)
    path=getattr(fn,'__route__',None)
    if path is None or method is None:
        raise ValueError('@get or @post not defined in %s.' % str(fn))
    if not asyncio.iscoroutinefunction(fn) and not inspect.isgeneratorfunction(fn):
        fn=asyncio.coroutine(fn)
    logging.info('add route %s %s => %s(%s)' % (method,path,fn.__name__,','.join(inspect.signature(fn).parameters.keys())))
    app.router.add_route(method,path,RequestHandler(app,fn))
#自动搜索传入的module_name的module的处理函数
def add_routes(app,module_name):
    n=module_name.rfind('.')
    if n==(-1):
        mod=__import__(module_name,globals(),locals())
    else:
        name=module_name[n+1:]
        mod=getattr(__import__(module_name[:n],globals(),locals(),[name]),name)
    for attr in dir(mod):
        if attr.startswith('_'):
            continue
        fn=getattr(mod,attr)
        if callable(fn):
            method=getattr(fn,'__method__',None)
            path=getattr(fn,'__route__',None)
            if method and path:
                add_route(app,fn)
