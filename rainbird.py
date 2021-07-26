#!/usr/bin/env python3
import sys

from rainbird import Controller
from logging import DEBUG, getLogger, Formatter, StreamHandler, basicConfig
from os import environ

basicConfig(level=DEBUG)

logger = getLogger(__name__)

logger.setLevel(DEBUG)
ch = StreamHandler()
ch.setLevel(DEBUG)
formatter = Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)

getLogger().setLevel(DEBUG)
requests_log = getLogger("http.client")
requests_log.setLevel(DEBUG)
requests_log.propagate = True
requests_log.addHandler(ch)

controller = Controller(environ["RAINBIRD_SERVER"], environ["RAINBIRD_PASSWORD"])
print(f"{controller.command(*sys.argv[1:])}\n")
