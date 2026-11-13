from __future__ import annotations

import logging
import re

_IPV4 = re.compile(r"\b(\d{1,3}\.\d{1,3}\.\d{1,3})\.\d{1,3}\b")
_IPV6 = re.compile(r"\b(?:[0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}\b")


def truncate_ip(value: str) -> str:
    value = _IPV4.sub(r"\1.0", value)

    def _v6(match: re.Match[str]) -> str:
        parts = match.group(0).split(":")
        keep = parts[:3]
        return ":".join(keep) + "::"

    return _IPV6.sub(_v6, value)


class RedactIpFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = truncate_ip(record.msg)
        if isinstance(record.args, tuple):
            record.args = tuple(truncate_ip(item) if isinstance(item, str) else item for item in record.args)
        return True


def configure_logging(level: str) -> None:
    root = logging.getLogger()
    root.setLevel(level.upper())
    if not root.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
        handler.addFilter(RedactIpFilter())
        root.addHandler(handler)
    else:
        for handler in root.handlers:
            handler.addFilter(RedactIpFilter())
