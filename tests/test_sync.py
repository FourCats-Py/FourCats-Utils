#!/usr/bin/python3
# -*- coding: UTF-8 -*-

# TIME ： 2022-08-11
import asyncio

from fourcats_utils import logger


def init():
    logger.init_app(sink="./app.log")
    logger.global_bind(a=1, b=2)
    logger.init_json(sink="./json.log")


async def second(num):
    """"""
    await asyncio.sleep(1)
    logger.info(f"协程 - {num} 输出内容 - 第二次", json=True, alias=num, state="success")


async def first():

    for i in range(100):
        logger.context_bind(c=i, d=i ** 2, thread_name=i)
        logger.info(f"协程 - {i} 输出内容", json=True, aaa=i, alias=i)
        asyncio.create_task(second(i))
    await asyncio.sleep(10)


if __name__ == '__main__':
    init()
    asyncio.run(first())
