#!/usr/bin/env python
# -*- coding: utf-8 -*-

#--------- 通用的配模块，包含常用函数和方法的实现 ---------------#
import MySQLdb
import cStringIO
import pycurl
import simplejson as json
import logging
import redis
import traceback
import os 
import sys
import pprint

#--------- 程序运行环境: test | production ---------------#
ENVIRONMENT = "test"

if ENVIRONMENT == "test":
    #----------------- Base 目录--------------------#
    BASE_FILE       = "/data/xxx/"
    LOG_PATH        = "log/log"
  
    #-----------------本地 Redis 配置 -------------------#
    REDISHOST        = "localhost"
    REDISPORT        = 6375
    TIMEOUT          = 5 
    REDIS_DB         = 0
    
    #-----------------数据库配置--------------------#
    MYSQLHOST         = "127.0.0.1"
    MYSQLUSER         = "root"
    MYSQLPASS         = "123456"
    MYSQLDB           = "my_db"
    

elif ENVIRONMENT == "production":
    #----------------- Base 目录--------------------#
    BASE_FILE       = "/data/xxx/"
    LOG_PATH        = "log/log"
  
    #-----------------本地 Redis 配置 -------------------#
    REDISHOST        = "localhost"
    REDISPORT        = 6375
    TIMEOUT          = 5 
    REDIS_DB         = 0
    
    #-----------------数据库配置--------------------#
    MYSQLHOST         = "127.0.0.1"
    MYSQLUSER         = "root"
    MYSQLPASS         = "123456"
    MYSQLDB           = "my_db"

#-----------------Mysql函数-----------------#
def get_mysql_connection():
    try: 
        db = MySQLdb.connect(host=MYSQLHOST, user=MYSQLUSER, passwd=MYSQLPASS, db=MYSQLDB, charset='utf8')
    except Exception, error:
        print "Mysql connect error!"+str(error)
        write_log("Mysql connect error!"+str(error))
    return db

def close_mysql_connection(db):
	db.close()
	
#查询
def mysql_query(sql):
    db  = get_mysql_connection()
    cur = db.cursor()

    cur.execute(sql)
    index = cur.description
    all = cur.fetchall()
    
    idx = 0
    result = {}  
    for line in all:
        ret = {}
        for i in range(len(index)):
            ret[index[i][0]] = line[i]
        if ret.has_key('id'):
            result[ret['id']] = ret
        else:
            result[idx] = ret
        idx = idx+1
    cur.close()
    close_mysql_connection(db)
    
    return result

#执行
def mysql_execute(sql):
    db  = get_mysql_connection()
    cur = db.cursor()

    cur.execute(sql)
    db.commit()
    cur.close()
    close_mysql_connection(db)

#-----------------Http接口函数-----------------#
def post_curl(url, argu1, argu2):
    result = "" 
    buf = cStringIO.StringIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.WRITEFUNCTION, buf.write)
    c.setopt(c.CONNECTTIMEOUT, 20)
    c.setopt(c.TIMEOUT, 60)
    #c.setopt(c.COOKIEFILE, '')
    c.setopt(c.FAILONERROR, True)
    #c.setopt(c.HTTPHEADER, ['Accept: text/html', 'Accept-Charset: UTF-8'])

    try:
        c.setopt(c.POSTFIELDS, 'argu1='+str(argu1)+'&argu2='+str(argu2))
        c.perform()
        result = buf.getvalue()
        buf.close()
    except pycurl.error, error:
        (errno, errstr) = error
        print 'Curl error: ', errstr
        write_log('Curl error: ' + errstr, "exception")
        buf.close() 
    return result
    
#---------------JSON处理------------------#
def json_decode(str):
    result = {}
    try:
        result = json.loads(str)
    except Exception, error:
        write_log("json decode detail exception: %s json values: %s" % (traceback.format_exc(),str), "exception")

    return result

def json_encode(arr):
    result = {}
    try:
        result = json.dumps(arr)
    except Exception, error:
        print 'error array values : ', arr
        write_log("json encode detail exception: %s array values in stdout.log" % traceback.format_exc(), "exception")

    return result    

#-----------------Redis 函数--------------------#	
def get_redis(redis_db):
    try:
        my_redis = redis.Redis(host = REDISHOST, port = REDISPORT, db = redis_db, socket_timeout=3)
    except Exception, error:
        write_log("Connect Redis error! "+str(error), "exception")
    
    return my_redis

def close_redis(my_redis):
    del my_redis

#----------------log 操作函数-----------------------# 
def write_log(content, role=None):
    if role:
        log_path = LOG_PATH+"."+str(role)+".log"
    else:
        log_path = LOG_PATH+".log"
    #生成一个日志对象
    logger = logging.getLogger()
    #生成log句柄
    hdlr = logging.FileHandler(BASE_FILE+log_path)
    #日志格式三项：时间，信息级别，日志信息 
    formatter = logging.Formatter('[%(asctime)s %(levelname)s] %(message)s') 
    #将格式器设置到处理器上
    hdlr.setFormatter(formatter)
    #将处理器加到日志对象上 
    logger.addHandler(hdlr)
    #要设置日志等级,NOTSET（值为0），输出所有信息 
    logger.setLevel(logging.NOTSET)
    #写入  
    content = "["+str(os.getpid())+"] "+content
    logger.info(content) 
    logger.removeHandler( hdlr )
    hdlr.close()#关闭句柄，否则会造成fd泄露
    del logger


#----获取异常所在的行数和执行函数名----------#
def get_cur_func_info(): 
    try: 
        raise 
    except Exception, err: 
        f = sys.exc_info()[2].tb_frame.f_back 
        return (f.f_code.co_name, f.f_lineno)      
        
if __name__ == '__main__':
    
    '''
    #测试json
    str = '{"name":"Mike","sex":"male","age":"29"}'
    print(json_decode(str))
    '''
    
    '''
    #mysql 测试
    result = mysql_query("select * from test1")
    #print result
    #print type(result)
    for k,v in result.items():
        print k,v
        print v['id'], v['name']
    '''
    
    '''
    #测试日志写入
    write_log("test test test", "test")
    '''
    
    '''
    #测试redis
    local_redis = get_redis('minute')
    result = local_redis.keys('*')
    pprint.pprint(result)
    '''
    
    #测试xxx