from loguru import logger
import sys

def logging(log:any):
    logger.info(log)
    sys.stdout.flush()