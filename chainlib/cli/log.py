# standard imports
import logging

logging.basicConfig(level=logging.WARNING, format='%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s')


def process_log(args, logger):
    if args.vv:
        logger.setLevel(logging.DEBUG)
    elif args.v:
        logger.setLevel(logging.INFO)

    return logger
