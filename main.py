###--Main--### 

import sys

from daemon_config import DaemonConfig
from daemon import Daemon


if __name__ == '__main__':

    cfg = DaemonConfig(sys.argv[1])
    errors = cfg.load()

    if errors:
        sys.exit(errors)

    try:
        daemon = Daemon(cfg)
        daemon.run()

    except Exception as error:
        sys.exit(error)
