#!/usr/bin/python3
# -*- coding: UTF-8 -*-

# TIME ： 2022-08-08
import json
import sys
from typing import Callable

from loguru import logger as _logger
from loguru._logger import Logger as _Logger


class JsonDispose:
    """"""

    def __init__(self):
        """"""
        self.__json_callback = None
        self.logger = _logger.patch(self.__dispose)
        self.logger.add(
            sink="./json.log", level="DEBUG", format="{extra[serialized]}",
            filter=lambda record: record["extra"].get("json", False) is True
        )

    def dispose(self, func):
        """"""
        self.__json_callback = func
        return func

    def __dispose(self, record: dict) -> None:
        """"""
        if self.__json_callback is not None:
            return self.__json_callback(record=record)
        return self.__json_dispose(record=record)

    def __json_dispose(self, record: dict):
        """"""
        record["extra"]["serialized"] = json.dumps(record["extra"])
        return


class StderrDispose:
    """"""

    def __init__(self, logger=_logger, flag: str = "json"):
        """"""
        assert isinstance(logger, (_Logger, JsonDispose)), "The log controller type is incorrect."

        if isinstance(logger, JsonDispose):
            logger = logger.logger

        logger.remove()
        self.flag = flag
        self.__stderr_callback = None
        logger.add(sink=sys.stderr, colorize=True, level="DEBUG", format=self.__dispose)

    def dispose(self, func: Callable):
        self.__stderr_callback = func
        return func

    def __dispose(self, record: dict):
        """"""
        if self.__stderr_callback is not None:
            return self.__stderr_callback(record)
        return self.__stderr_dispose(record=record)

    def __stderr_dispose(self, record: dict) -> str:
        """"""
        stderr_formatter = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | " \
                           "<level>{level: <8}</level> | " \
                           "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - " \
                           "<level>{message}</level>"

        if record["extra"].get(self.flag, False) is True:
            stderr_formatter += " - <level>{extra[serialized]}</level>"

        if "serialized" not in record["extra"]:
            record["extra"]["serialized"] = json.dumps(dict())

        stderr_formatter += "\n"
        return stderr_formatter


class Logger:
    """"""

    def __init__(self):
        """"""
        self.json = None
        self.stderr = StderrDispose(logger=self.json or _logger)

    @property
    def logger(self):
        if self.json is None:
            return _logger
        return self.json.logger

    def init_app(self):
        """"""
        self.logger.add("./app.log", format=formatter_fot_stderr(), level="DEBUG")

    def init_json(self):
        """"""
        self.json = JsonDispose()
        return self.json.logger


if __name__ == '__main__':
    obj = Logger()
    obj.init_json()
    obj.logger.debug("1")
    obj.logger.info("2", json=True)
    obj.logger.warning("3", json=True)
    obj.logger.error("4", json=True)
