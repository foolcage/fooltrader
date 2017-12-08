import logging


def init_log():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # fh = logging.FileHandler('fooltrader.log')
    # fh.setLevel(logging.INFO)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # create formatter and add it to the handlers
    formatter = logging.Formatter("%(levelname) -10s %(asctime)s %(module)s:%(lineno)s %(funcName)s %(message)s")
    # fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # add the handlers to the logger
    # root_logger.addHandler(fh)
    root_logger.addHandler(ch)


init_log()