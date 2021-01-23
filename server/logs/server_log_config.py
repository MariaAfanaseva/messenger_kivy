import logging
import logging.handlers
import sys
import os

path_file_log = os.path.abspath(os.path.join(__file__, '../files_log/server.log'))
# print(path_file_log)

logger = logging.getLogger('server')

formatter_stream = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
formatter_file = logging.Formatter('%(levelname)-5s %(asctime)-25s %(filename)-10s %(message)s')

handler_stream = logging.StreamHandler(sys.stderr)
handler_file = logging.handlers.TimedRotatingFileHandler(path_file_log, encoding='utf-8', interval=1, when='D')

handler_stream.setLevel(logging.INFO)
handler_file.setLevel(logging.DEBUG)

handler_stream.setFormatter(formatter_stream)
handler_file.setFormatter(formatter_file)


logger.addHandler(handler_file)
logger.addHandler(handler_stream)


if __name__ == '__main__':
    logger.addHandler(handler_stream)
    logger.critical('Debug critical server')
    logger.error('Debug error server')
    logger.warning('Debug warning server')
    logger.info('Debug info server')
    logger.debug('Debug info server')
