#!/usr/bin/python3
# -*- coding: UTF-8 -*-

# TIME ： 2022-07-28
import datetime
import contextvars
import json

from loguru import logger


class CurrentFormatter:
    """"""

    uip = contextvars.ContextVar("Uip", default="")
    trace_id = contextvars.ContextVar("TraceId", default="")

    def __init__(self, uip: str, trace_id: str):
        """"""
        self.uip.set(uip)
        self.trace_id.set(trace_id)

    @classmethod
    def dict(cls):
        return dict(uip=cls.uip.get(), trace_id=cls.trace_id.get())


class JsonLogger:
    """"""

    def __new__(cls, source: str = None, source_type: str = None, service_id: str = None, *args, **kwargs):
        """"""
        if source is None:
            source = ""

        if source_type is None:
            source_type = ""

        if service_id is None:
            service_id = ""

        return logger.bind(json=True, source=source, source_type=source_type, service_id=service_id)


def structure(data: dict):
    """"""
    fields = [
        "alias", "level", "message", "fileline", "datetime", "state", "source", "source_type", "service_id", "uip",
        "trace_id"
    ]
    result = dict(extra=dict())
    for key, value in data.items():
        if key in fields:
            result[key] = str(value)
        else:
            result["extra"][key] = str(value)

    difference = set(fields).difference(set(result.keys()))
    for key in difference:
        if key == "state":
            result["state"] = False
            continue
        result[key] = ""
    return result


def formatter_for_json(record: dict):
    """"""
    record["extra"].pop("json", "")
    record["extra"].pop("serialized", "")
    record["extra"]["message"] = record.get("message", "")
    record["extra"]["level"] = record.get("level", dict()).name
    record["extra"]["fileline"] = ":".join([record["name"], record["function"], str(record["line"])])
    record["extra"]["datetime"] = record.get("time", datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S.%f")
    record["extra"]["serialized"] = json.dumps(structure(data=record["extra"]))
    return "{extra[serialized]}\n"


def formatter_fot_stderr(format: str = None, json_format: str = None):
    """"""
    if format is None:
        format = "{time:YYYY-MM-DD HH:mm:ss.SSS} - {level} | {name}:{function}:{line} - {message}\n"

    if json_format is None:
        json_format = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} - {message} - " \
                      "{extra[serialized]}\n"

    def formatter(record: dict):
        """"""
        return format
    return formatter


if __name__ == '__main__':
    logger.add("./app.log", format=formatter_fot_stderr(), level="DEBUG")
    logger.add("./json.log", format=formatter_for_json, level="DEBUG",
               filter=lambda record: record["extra"].get("json", False) is True)



    CurrentFormatter(uip="1.1.1.1", trace_id="1_1_1_1")
    json_logger = JsonLogger()
    json_logger.bind(**CurrentFormatter.dict()).debug("456")
    logger.debug("123")
    json_logger.debug("234", json=True)
    json_logger.bind(**dict(CurrentFormatter.dict())).debug("678")
