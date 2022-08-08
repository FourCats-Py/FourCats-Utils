#!/usr/bin/python3
# -*- coding: UTF-8 -*-

# TIME ： 2022-08-08
import json
import sys
from typing import Callable

from loguru import logger as _logger


class Stderr:
    """"""

    def __init__(self, logger: _logger):
        """"""
        self.stderr_callback = None
        logger.remove()
        logger.add(sink=sys.stderr, colorize=True, level="DEBUG", format=self.__stderr_formatter)

    def set_stderr_callback(self, func: Callable):
        self.stderr_callback = func
        return func

    def __stderr_formatter(self, record: dict):
        """"""
        if self.stderr_callback is not None:
            return self.stderr_callback(record)
        return self.__stderr_callback(record=record)

    @staticmethod
    def __stderr_callback(record: dict) -> str:
        """"""
        stderr_formatter = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | " \
                           "<level>{level: <8}</level> | " \
                           "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - " \
                           "<level>{message}</level>"

        if record["extra"].get("json", False) is True:
            stderr_formatter += " - <level>{extra[serialized]}</level>"
        stderr_formatter += "\n"
        return stderr_formatter


class Patch:
    """"""

    def __init__(self):
        """"""
        self.patch_callback = None
        self.logger = _logger.patch(self.__patch)

    def set_patch(self, func):
        """"""
        self.patch_callback = func
        return func

    def __patch(self, record: dict) -> None:
        """"""
        if self.patch_callback is not None:
            return self.patch_callback(record=record)
        return self.__patch_dispose(record=record)


    def __patch_dispose(self, record: dict):
        """"""
        record["extra"]["serialized"] = json.dumps(record["extra"])
        return


class Logger:
    """"""

    def __init__(self):
        """"""
        self.logger = _logger.patch(self.patching)
        self.stderr = Stderr(logger=self.logger)


if __name__ == '__main__':
    obj = Logger()
    obj.logger.debug("1")
    obj.logger.info("2", json=True)
    obj.logger.warning("3", json=True)
    obj.logger.error("4", json=True)
