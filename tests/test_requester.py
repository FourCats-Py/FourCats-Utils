#!/usr/bin/python3
# -*- coding: UTF-8 -*-

# TIME ： 2022-08-11
from fourcats_utils import Requester

requester = Requester()

if __name__ == '__main__':
    # data = requester.request("GET", "https://www.baidu.com")
    data = requester.request("GET", "https://www.baidu.com", with_logger=True)
    print(data.status)
