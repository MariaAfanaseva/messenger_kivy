import logging
from ipaddress import ip_address
logger = logging.getLogger('server')


class CheckPort:
    """Port validation descriptor."""
    def __set_name__(self, owner, name):
        self.name = name  # name = port

    def __set__(self, instance, value):
        if not isinstance(value, int) or not 1024 < value < 65535:
            logger.critical('Неверные значения port (-p)')
            exit(1)
        # If the port passed the test, add it to the list of instance attributes.
        instance.__dict__[self.name] = value
        logger.info(f'Полученны данные port, который слушает сервер - {value}')


class CheckIP:
    """Address validation descriptor."""
    def __set_name__(self, owner, name):
        self.name = name  # name = IP

    def __set__(self, instance, value):
        if value:
            try:
                ip_addr = str(ip_address(value))
            except ValueError:
                logger.critical('Неверные значения ip (-a)')
                exit(1)
            else:
                instance.__dict__[self.name] = ip_addr
                logger.info(f'Полученны данные address, который слушает сервер - {ip_addr}')
        else:
            instance.__dict__[self.name] = value
            logger.info(f'Сервер слушает все адреса')


class CheckName:
    """Username validation descriptor."""
    def __set_name__(self, owner, name):
        self.name = name

    def __set__(self, instance, name):
        if isinstance(name, str) and len(name) < 25:
            instance.__dict__[self.name] = name
        else:
            logger.critical('Имя должно быть словом не длиннее 25')
            exit(1)
