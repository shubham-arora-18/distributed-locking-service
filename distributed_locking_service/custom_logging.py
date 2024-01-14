import logging
import socket
import sys

# from ddtrace import patch
from pythonjsonlogger import jsonlogger

# patch(logging=True)


def configure_logging():
    formatter = jsonlogger.JsonFormatter(
        fmt=(
            f"[%(asctime)s.%(msecs)03d] "
            f"[%(process)s] [{socket.gethostname()}] [%(pathname)s L%(lineno)d] "
            "[dd.service=%(dd.service)s dd.env=%(dd.env)s dd.version=%(dd.version)s "
            "dd.trace_id=%(dd.trace_id)s dd.span_id=%(dd.span_id)s] [%(levelname)s] %(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(logging.INFO)
