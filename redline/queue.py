# -*- coding: utf-8 -*-
#
# Copyright 2011 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
from redis import Redis

# See http://code.google.com/p/redis/issues/detail?id=656

class Redline(object):

    # FIFO Queue
    def __init__(self,queue_name,host='localhost', port=6379,db=0,
                 password=None, socket_timeout=None,
                 connection_pool=None,
                 charset='utf-8', errors='strict', unix_socket_path=None):
        # Initialize Redis
        self.redis = Redis(host=host,port=port,db=db,
                           password=password,socket_timeout=socket_timeout,
                           connection_pool=connection_pool,
                           charset=charset,errors=errors,unix_socket_path=unix_socket_path)
        self.queue_name = queue_name
        self.queue_key = "redline:queue:%s" % self.queue_name
        self.processing_key = "redline:processing:%s" % self.queue_name
        self.pending_key = "redline:pending:%s" % self.queue_name
        self.completed_key = "redline:completed:%s" % self.queue_name
    
    def push(self,element):
        print self.queue_key, element
        push_element = self.redis.lpush(self.queue_key,element)

    def push_unique(self,element):
        seen = self.check_seen(element)
        if not seen:
            Queue.push(self,element)
            self.redis.sadd(self.pending_key,element)

    def pop(self):
        popped_element = self.redis.rpoplpush(self.queue_key,self.processing_key)
        return popped_element

    def bpop(self):
        popped_element = self.redis.brpoplpush(self.queue_key,self.processing_key)
        return popped_element

    def mark_completed(self,element):
        # note, I think the latest version of redis.py has count as the middle arg 
        self.redis.lrem(self.processing_key,element,0)
        self.redis.sadd(self.completed_key,element)
        self.redis.srem(self.pending_key,element)

    def queue_size(self):
        return self.redis.llen(self.queue_key)
     
    def processing_size(self):
        return self.redis.llen(self.processing_key)

    def completed_size(self):
        set_members = self.redis.smembers(self.completed_key)
        return len(set_members)

    def empty(self):
        return (self.queue_size() == 0 and self.processing_size() == 0)

    def check_pending(self,element):
        return self.redis.sismember(self.pending_key,element)

    def check_completed(self,element):
        return self.redis.sismember(self.completed_key,element)

    def check_seen(self,element):
        pending = self.check_pending(element)
        completed = self.check_completed(element)
        return (pending or completed)



