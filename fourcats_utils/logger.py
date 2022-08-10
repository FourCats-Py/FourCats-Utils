#!/usr/bin/python3
# -*- coding: UTF-8 -*-

# TIME ： 2022-08-08
import sys
import copy
import json
import contextvars
from typing import Callable

from loguru import logger as _logger


class StderrDispose:
    """"""

    def __init__(self, logger: _logger, flag: str = "json"):
        """"""
        logger.remove()
        self.flag = flag
        self.__stderr_callback = None
        logger.add(sink=sys.stderr, colorize=True, level="DEBUG", format=self.__dispose)

    def dispose(self, func: Callable) -> Callable:
        self.__stderr_callback = func
        return func

    def __dispose(self, record: dict) -> str:
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


class JsonDispose:
    """"""

    def __init__(self, flag: str = "json"):
        """"""
        self.flag = flag
        self.__json_callback = None
        self.logger = _logger.patch(self.__dispose)

    def init(self, sink, level: str = "INFO", encoding: str = "UTF-8", **kwargs) -> None:
        """"""
        if "filter" not in kwargs:
            kwargs["filter"] = lambda x: x["extra"].get(self.flag, False) is True
        self.logger.add(sink=sink, level=level, format="{extra[serialized]}", encoding=encoding, **kwargs)
        return

    def bind(self, **kwargs) -> None:
        """"""
        self.logger = self.logger.bind(**kwargs)
        return

    def dispose(self, func) -> Callable:
        """"""
        self.__json_callback = func
        return func

    def __dispose(self, record: dict) -> None:
        """"""
        if self.__json_callback is not None:
            return self.__json_callback(record=record)
        return self.__json_dispose(record=record)

    def __json_dispose(self, record: dict) -> None:
        """"""
        data = copy.deepcopy(record["extra"])
        data.pop(self.flag, "")
        record["extra"]["serialized"] = json.dumps(data)
        return


class AppDispose:
    """"""

    def __init__(self, flag: str = "json"):
        """"""
        self.flag = flag
        self.__app_callback = None

    def init(self, logger: _logger, sink, level: str = "INFO", **kwargs) -> None:
        """"""
        logger.add(sink=sink, level=level, format=self.__dispose, **kwargs)
        return

    def dispose(self, func) -> Callable:
        """"""
        self.__app_callback = func
        return func

    def __dispose(self, record: dict) -> str:
        """"""
        if self.__app_callback is not None:
            return self.__app_callback(record=record)
        return self.__app_dispose(record=record)

    def __app_dispose(self, record: dict) -> str:
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
    _context_bind = contextvars.ContextVar("context_bind", default="")

    def __init__(self, flag: str = "json"):
        """"""
        self.app = AppDispose(flag=flag)
        self.json = JsonDispose(flag=flag)
        self.stderr = StderrDispose(logger=self.logger, flag=flag)

    @property
    def logger(self):
        # TODO 该部分需要考虑, 逻辑不够严谨, 可能存在问题
        context_bind = self._context_bind.get() or None
        if context_bind is not None:
            return self.json.logger.bind(**json.loads(context_bind))
        return self.json.logger

    # @property
    # def context_logger(self):
    #     return self.json.logger.bind(**json.loads(self._context_bind.get()))

    def init_app(self, sink, level: str = "INFO", **kwargs):
        """"""
        self.app.init(logger=self.logger, sink=sink, level=level, **kwargs)
        return

    def init_json(self, sink, level: str = "INFO", encoding: str = "UTF-8", **kwargs) -> None:
        """"""
        self.json.init(sink=sink, level=level, encoding=encoding, **kwargs)
        return

    def global_bind(self, **kwargs) -> None:
        """"""
        self.json.bind(**kwargs)
        return

    def context_bind(self, **kwargs) -> None:
        """"""
        self._context_bind.set(json.dumps(kwargs))
        return


if __name__ == '__main__':
    obj = Logger()
    obj.context_bind(c=3, d=4)
    obj.init_app(sink="./app.log")
    obj.init_json(sink="./json.log")
    obj.global_bind(a=1, b=2)
    obj.logger.debug("1")
    obj.logger.info("2", json=True)
    obj.logger.warning("3", json=True)
    obj.logger.error("4", json=True)
