#!/usr/bin/python3
# -*- coding: UTF-8 -*-

# TIME ： 2022-08-11
import time
import threading
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED

from fourcats_utils.logger import logger


def init():
    logger.init_app(sink="./app.log")
    logger.global_bind(a=1, b=2)
    logger.init_json(sink="./json.log")


def second():
    """"""
    thread_name = threading.currentThread().getName()
    logger.info(f"线程 - {thread_name} 输出内容 - 第二次", json=True, alias=thread_name, state="success")


def first(num):
    thread_name = threading.currentThread().getName()
    logger.context_bind(c=num, d=num ** 2, thread_name=thread_name)
    logger.info(f"线程 - {thread_name} 输出内容", json=True, aaa=thread_name, alias=thread_name)
    time.sleep(1)
    second()


if __name__ == '__main__':
    init()
    executor = ThreadPoolExecutor(max_workers=10)
    tasks = [executor.submit(first, i) for i in range(100)]
    wait(tasks, return_when=ALL_COMPLETED)
