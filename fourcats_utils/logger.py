#!/usr/bin/python3
# -*- coding: UTF-8 -*-

# TIME ： 2022-08-08
import sys
import copy
import json
import datetime
import contextvars
from typing import Callable, Union

from loguru import logger as _logger
from loguru._logger import Logger as _Logger

__all__ = ("logger",)


class StderrDispose:
    """"""

    def __init__(self, handler: _logger, flag: str = "json"):
        """"""
        handler.remove()
        self.flag = flag
        self.__stderr_callback = None
        handler.add(sink=sys.stderr, colorize=True, format=self.__dispose)

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
        self.handler = _logger.patch(self.__dispose)

    def init(self, sink, level: str = "INFO", encoding: str = "UTF-8", **kwargs) -> None:
        """"""
        if "filter" not in kwargs:
            kwargs["filter"] = lambda x: x["extra"].get(self.flag, False) is True
        self.handler.add(sink=sink, level=level, format="{extra[serialized]}", encoding=encoding, **kwargs)
        return

    def bind(self, **kwargs) -> None:
        """"""
        self.handler = self.handler.bind(**kwargs)
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
        data = copy.copy(record["extra"])
        data.pop(self.flag, "")
        data.update(**dict(
            message=record.get("message", ""),
            level=record.get("level", dict()).name,
            fileline=":".join([record["name"], record["function"], str(record["line"])]),
            datetime=record.get("time", datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S.%f"),
            timestamp=record.get("time", datetime.datetime.now()).timestamp()
        ))
        record["extra"]["serialized"] = json.dumps(data, ensure_ascii=False)
        return


class AppDispose:
    """"""

    def __init__(self, flag: str = "json"):
        """"""
        self.flag = flag
        self.__app_callback = None

    def init(self, handler: _logger, sink, level: str = "INFO", **kwargs) -> None:
        """"""
        handler.add(sink=sink, level=level, format=self.__dispose, **kwargs)
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

    def __init__(self):
        """"""
        self.__flag = "json"
        self.__rename_callback = None
        self.app = AppDispose(flag=self.__flag)
        self.json = JsonDispose(flag=self.__flag)
        self.stderr = StderrDispose(handler=self.json.handler, flag=self.__flag)

    def __getattr__(self, item) -> _logger:
        """"""
        return getattr(self.handler, item)

    @property
    def handler(self) -> _logger:
        context_bind = self._context_bind.get() or None
        if context_bind is not None:
            return self.json.handler.bind(**json.loads(context_bind))
        return self.json.handler

    def init_app(self, sink, level: str = "INFO", **kwargs):
        """"""
        self.app.init(handler=self.json.handler, sink=sink, level=level, **kwargs)
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

    @property
    def flag(self):
        """"""
        return self.__flag

    def setter_flag(self, flag: str):
        """"""
        self.__flag = flag
        return flag


logger: Union[Logger, _Logger] = Logger()
