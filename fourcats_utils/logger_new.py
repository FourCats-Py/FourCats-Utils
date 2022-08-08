#!/usr/bin/python3
# -*- coding: UTF-8 -*-

# TIME ： 2022-08-01
import json
import sys

from loguru import logger


class Logger:
    """"""

    @classmethod
    def app_logger(cls):
        """"""
        logger.add(
            sink="./app.log",
            level="DEBUG",
            rotation="00:00",
            retention=6,
            encoding="UTF-8"
        )

    @classmethod
    def json_logger(cls):
        """"""
        logger.add(
            sink="./json.log",
            level="DEBUG",
            serialize=True,
            # format=cls.__formatter_for_json,
            filter=lambda record: record["extra"].get("json", False) is True
        )

    @classmethod
    def stderr_logger(cls):
        """"""
        logger.remove()
        logger.add(
            sink=sys.stderr,
            colorize=True,
            level="DEBUG",
            format=cls.__formatter_for_stderr()
        )

    @classmethod
    def __formatter_for_stderr(
            cls,
            stderr_formatter: str = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                                    "<level>{level: <8}</level> | "
                                    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                                    "<level>{message}</level>"
    ):
        """"""

        def formatter(record: dict):
            """"""
            return cls.__select_formatter(record=record, stderr_formatter=stderr_formatter)

        return formatter

    @classmethod
    def __formatter_for_json(cls, record: dict):
        """"""
        record["extra"]["serialized"] = json.dumps(record["extra"])
        return "{extra[serialized]}\n"

    @classmethod
    def __select_formatter(cls, record: dict, stderr_formatter: str):
        """"""
        if record["extra"].get("json", False) is True:
            stderr_formatter += " - <level>{extra[serialized]}</level>"
        stderr_formatter += "\n"

        if "serialized" not in record["extra"]:
            record["extra"]["serialized"] = json.dumps(dict())
        return stderr_formatter


if __name__ == '__main__':
    Logger.stderr_logger()
    Logger.json_logger()
    logger.debug("1")
    logger.info("2", json=True)
    logger.warning('3', json=True)
    logger.error("4", json=True)
