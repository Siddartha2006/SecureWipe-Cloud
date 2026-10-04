import time
from .worker import cleanup_expired

if __name__ == "__main__":
    while True:
        cleanup_expired()
        time.sleep(60)
