from loguru import logger
import sys

logger.remove()
logger.add(sys.stdout, format="{time} {level} {message}", level="INFO", enqueue=True)
def logging(log:any):
    logger.info(log)
    sys.stdout.flush()