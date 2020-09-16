import sys

from blaise_instrument_checker import app
from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '{"timestamp": "%(asctime)s", "service": "blaise_instrument_checker",  "severity": "%(levelname)s", "module": "%(module)s" "message": "%(message)s"}'
        # 'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': sys.stdout,
        'formatter': 'default'
    }},
    'root': {
        'level': 'NOTSET',
        'handlers': ['wsgi']
    }
})

if __name__ == "__main__":
    app.run()
