import logging
import sys
import os

path_file_log = os.path.abspath(os.path.join(__file__, '../files_log/client.log'))
# print(path_file_log)


log = logging.getLogger('client')

handler_stream = logging.StreamHandler(sys.stderr)
handler_stream.setLevel(logging.ERROR)
handler_file = logging.FileHandler(path_file_log, encoding='utf-8')
handler_file.setLevel(logging.DEBUG)

formatter_stream = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
formatter_file = logging.Formatter('%(asctime)-25s %(levelname)-10s %(filename)-10s %(message)s')
handler_stream.setFormatter(formatter_stream)
handler_file.setFormatter(formatter_file)

log.addHandler(handler_file)
log.addHandler(handler_stream)

log.setLevel(logging.DEBUG)


if __name__ == '__main__':
    log.addHandler(handler_stream)
    log.critical('Debug critical client')
    log.error('Debug error client')
    log.warning('Debug warning client')
    log.info('Debug info client')
    log.debug('Debug debug client')
