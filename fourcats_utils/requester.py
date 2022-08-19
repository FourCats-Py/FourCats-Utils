#!/usr/bin/python3
# -*- coding: UTF-8 -*-

# TIME ： 2022-07-28
import json
import certifi
from urllib.parse import urlencode

from loguru import logger
from urllib3 import PoolManager, HTTPResponse, HTTPConnectionPool

from .logger import logger

__all__ = ("Requester",)


class Response(HTTPResponse):
    """"""

    def json_decode(self):
        """"""
        return json.loads(self.data)

    def check_http_code(self, value: int):
        """"""
        if self.status != value:
            raise ValueError(f"The target status is {value}, but the actual request status is {self.status}.")
        return self

    def check_json_state(self, field, value):
        """"""
        result = json.loads(self.data)
        if result[field] != value:
            raise ValueError(
                f"The target status is {value}, but the actual request status is {result.get(field, '')}."
            )
        return result


class Requester(PoolManager):
    """"""

    def __init__(self, num_pools=10, headers=None, with_logger=False, **connection_pool_kw):
        """"""

        HTTPConnectionPool.ResponseCls = Response

        if "cert_reqs" not in connection_pool_kw:
            connection_pool_kw["cert_reqs"] = "CERT_REQUIRED"

        if "ca_certs" not in connection_pool_kw:
            connection_pool_kw["ca_certs"] = certifi.where()

        self.with_logger = with_logger
        super(Requester, self).__init__(num_pools=num_pools, headers=headers, **connection_pool_kw)

    def request(self, method, url, fields=None, headers=None, with_logger=False, **urlopen_kw):
        """"""
        with_logger = self.with_logger or with_logger
        if with_logger is True:
            return self._with_logger(method=method, url=url, fields=fields, headers=headers, **urlopen_kw)
        return self._request(method=method, url=url, fields=fields, headers=headers, **urlopen_kw)

    def json_request(self, method, url, fields=None, headers=None, with_logger=False, **urlopen_kw):
        """"""
        if headers is None:
            headers = {"Content-Type": "application/json; charset=utf-8"}

        if "Content-Type" not in headers:
            headers["Content-Type"] = "application/json; charset=utf-8"

        if "body" not in urlopen_kw:
            raise TypeError(
                "JSON type request, parameters can only be placed in the request body."
            )

        urlopen_kw["body"] = json.dumps(urlopen_kw["body"])

        if fields:
            url += "?" + urlencode(fields)

        with_logger = self.with_logger or with_logger
        if with_logger is True:
            return self._with_logger(method=method, url=url, headers=headers, **urlopen_kw)
        return self._request(method=method, url=url, headers=headers, **urlopen_kw)

    def _request(self, method, url, fields=None, headers=None, **urlopen_kw):
        """
        Make a request using :meth:`urlopen` with the appropriate encoding of
        ``fields`` based on the ``method`` used.

        This is a convenience method that requires the least amount of manual
        effort. It can be used in most situations, while still having the
        option to drop down to more specific methods when necessary, such as
        :meth:`request_encode_url`, :meth:`request_encode_body`,
        or even the lowest level :meth:`urlopen`.
        """
        method = method.upper()

        urlopen_kw["request_url"] = url

        if method in self._encode_url_methods:
            return self.request_encode_url(
                method, url, fields=fields, headers=headers, **urlopen_kw
            )
        else:
            return self.request_encode_body(
                method, url, fields=fields, headers=headers, **urlopen_kw
            )

    def _with_logger(self, method, url, fields=None, headers=None, **urlopen_kw):
        """"""
        fields = fields or dict()
        headers = headers or dict()
        body = urlopen_kw.get("body", dict()) or dict()

        _fields = {
            key: value if isinstance(value, (str, list, int, dict, tuple)) else str(value)
            for key, value in fields.items()
        }

        logger.debug("".join(["*" * 30, " " * 5, "REQUEST START", " " * 5, "*" * 30]))
        logger.debug(f"METHOD: {method}")
        logger.debug(f"URL: {url}")
        logger.debug(f"HEADERS: {json.dumps(headers, ensure_ascii=False)}")
        logger.debug(f"FIELDS: {json.dumps(_fields, ensure_ascii=False)}")
        logger.debug(f"BODY: {body if isinstance(body, str) else json.dumps(body, ensure_ascii=False)}")
        response = self._request(method=method, url=url, fields=fields, headers=headers, **urlopen_kw)
        logger.debug("".join(["*" * 30, " " * 5, "REQUEST END  ", " " * 5, "*" * 30]))
        logger.debug("".join(["*" * 30, " " * 5, "RESPONSE START", " " * 4, "*" * 30]))
        try:
            logger.debug(f"RESPONSE: {json.loads(response.data)}")
        except (UnicodeDecodeError, TypeError, json.JSONDecodeError):
            if isinstance(response.data, bytes):
                _response = response.data if len(response.data) < 30 else \
                    response.data[:15] + b'.....' + response.data[-15:]
            else:
                _response = response.data if len(response.data) < 30 else \
                    response.data[:15] + '......' + response.data[-15:]
            logger.debug(f"RESPONSE: {_response}")
        except Exception as e:
            logger.warning(
                f"JSON deserialization found location error, unable to print the request result log, "
                f"but does not affect the program operation. - {e}"
            )
            logger.debug("RESPONSE: Unknown error occurred in JSON parsing, please use the response result normally.")
        logger.debug("".join(["*" * 30, " " * 5, "RESPONSE END ", " " * 5, "*" * 30]))
        return response
