import logging
import logging.config
import threading
from typing import Dict, Optional, Any

from pythonjsonlogger import jsonlogger


class _LogExtraData:
    _data: Dict[str, Any] = {}
    _thread_data: threading.local = threading.local()

    def __init__(self):
        self._thread_data.data = {}

    def add_data(self, data: dict, data_id: int, thread: bool = False):
        if thread is True:
            self._thread_data.data[data_id] = data
        else:
            self._data[data_id] = data

    def remove_data(self, data_id: int):
        if data_id in self._data:
            del self._data[data_id]
        if data_id in self._thread_data.data:
            del self._thread_data.data[data_id]

    def get_all_data(self) -> Dict[str, Any]:
        data_items = [*list(self._data.items()), *list(self._thread_data.data.items())]
        sorted_items = sorted(data_items, key=lambda x: x[0])
        combined = {}
        for _, v in sorted_items:
            combined = {**combined, **v}
        return combined


class ContextLogger(jsonlogger.JsonFormatter):
    def __init__(self, context_data: _LogExtraData, *args, **kwargs):
        super(ContextLogger, self).__init__(*args, **kwargs)
        self.context_data = context_data

    def add_fields(
        self,
        log_record: Dict[str, Any],
        record: logging.LogRecord,
        message_dict: Dict[str, Any],
    ) -> None:
        super(ContextLogger, self).add_fields(log_record, record, message_dict)

        contextual_data = self.context_data.get_all_data()
        log_record.update(contextual_data)


class LogContext:
    # To be filled out when we enact the logging thing
    _global_data: Optional[_LogExtraData] = None

    def __init__(self, data: Dict[str, Any], thread: bool = False):
        self.data = data
        self.thread = thread

    def __enter__(self):
        self._global_data.add_data(self.data, id(self), self.thread)

    def __exit__(self, *args):
        self._global_data.remove_data(id(self))


def initialize_logger():
    print("Initialize")
    context_data = _LogExtraData()
    LogContext._global_data = context_data
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": True,
            "formatters": {
                "json": {
                    "()": f"{ContextLogger.__module__}.ContextLogger",
                    "format": "%(asctime)s %(levelname)s %(filename)s %(lineno)s %(message)s",
                    "timestamp": True,
                    "context_data": context_data,
                }
            },
            "handlers": {
                "json": {"class": "logging.StreamHandler", "formatter": "json"}
            },
            "loggers": {"": {"handlers": ["json"], "level": 20}},
        }
    )
