# FourCats-Utils

### Statement
 - A common Python toolkit package based on personal habits.
 - The log module is a secondary processing based on `loguru` that conforms to the usage habits.

### Logger

#### Init

- Provides a fast configuration method for application logs.
- It provides a quick configuration method for `Json` logs.
- It provides a fast configuration method for special log processing.

##### Application

```python
import json
from fourcats_utils import logger

# init Please refer to `loguru.add` method.
logger.init_app(sink="./app.log")


# Special processing (day response style)
@logger.app.dispose
def app_dispose(record: dict) -> str:
    # The following content is only the test content (default content). You can customize the logic for style output.
    stderr_formatter = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"

    if record["extra"].get("json", False) is True:
        stderr_formatter += " - <level>{extra[serialized]}</level>"

    if "serialized" not in record["extra"]:
        record["extra"]["serialized"] = json.dumps(dict())

    stderr_formatter += "\n"
    return stderr_formatter

```

##### `Json`

```Python
import copy
import json
import datetime
from fourcats_utils import logger

# init Please refer to `loguru.add` method.
logger.init_json(sink="./json.log")


# Special processing (day response style)
@logger.json.dispose
def app_dispose(record: dict) -> None:
    # The following content is only the test content (default content). You can customize the logic for style output.
    data = copy.copy(record["extra"])
    data.pop("json", "")
    data.update(**dict(
        message=record.get("message", ""),
        level=record.get("level", dict()).name,
        fileline=":".join([record["name"], record["function"], str(record["line"])]),
        datetime=record.get("time", datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S.%f"),
        timestamp=record.get("time", datetime.datetime.now()).timestamp()
    ))
    record["extra"]["serialized"] = json.dumps(data, ensure_ascii=False)
    return

```

##### Stderr

```python
import json
from fourcats_utils import logger


# Special processing (day response style)
@logger.stderr.dispose
def app_dispose(record: dict) -> str:
    # The following content is only the test content (default content). You can customize the logic for style output.
    stderr_formatter = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"

    if record["extra"].get("json", False) is True:
        stderr_formatter += " - <level>{extra[serialized]}</level>"

    if "serialized" not in record["extra"]:
        record["extra"]["serialized"] = json.dumps(dict())

    stderr_formatter += "\n"
    return stderr_formatter

```

##### Bind

```Python
from fourcats_utils import logger

# Use global binding.
logger.global_bind(a=1, b=2)

# Use context binding.
logger.context_bind(c=3, d=4)

```

#### Thread test

```python
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
```

#### Asyncio test

```python
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
```

### The default configuration is the distinction between the Jason log and the application log

- Setting the flag is mainly to display the JSON content you output in the console output (which does not contain the
  flag identification field). If it is not set, it defaults to ` JSON `
- Flag is the keyword parameter you need in the output log method. Currently, boolean type is supported.

```python
from fourcats_utils import logger

# Default
print(logger.flag)
# json

logger.setter_flag(flag="json_logger")
print(logger.flag)

# Output application log
logger.debug("1")

# And output to the application log and the Json log.
# The default is json, but the configuration above has been changed to JSON_ logger
logger.debug("1", json_logger=True)

```

### About customizing the renaming method of log files after cutting.
 - [https://github.com/Delgan/loguru/issues/529](https://github.com/Delgan/loguru/issues/529)
