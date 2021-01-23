import dis


class ServerCreator(type):
    def __init__(self, name_class, bases_classes, dict_class):
        # Metaclass to verify server compliance
        # name_class - metaclass instance - Server
        # bases_classes - tuple of base classes - ()
        # dict_class - dictionary of attributes and methods of an instance of a metaclass
        self.methods_class = []
        self.attrs_class = []
        self.name_class = name_class
        self.bases_classes = bases_classes
        self.dict_class = dict_class
        # print(dict_class)
        self.check_class()
        super().__init__(name_class, bases_classes, dict_class)

    def check_class(cls):
        for func in cls.dict_class:
            try:
                instructions = dis.get_instructions(cls.dict_class[func])
            except TypeError:
                pass
            else:
                cls.search_instruction(instructions)
        # print(attrs_class)
        # print(methods_class)
        if 'connect' in cls.methods_class:
            raise TypeError('Использование метода connect недопустимо в серверном классе')
        if not ('SOCK_STREAM' in cls.attrs_class and 'AF_INET' in cls.attrs_class):
            raise TypeError('Некорректная инициализация сокета.')

    def search_instruction(cls, instructions):
        for i in instructions:
            # print(i)
            if i.opname == 'LOAD_GLOBAL':
                if i.argval not in cls.methods_class:
                    cls.methods_class.append(i.argval)
            elif i.opname == 'LOAD_ATTR':
                if i.argval not in cls.attrs_class:
                    cls.attrs_class.append(i.argval)


class ClientCreator(type):
    def __init__(self, name_class, bases_classes, dict_class):
        self.methods = []
        self.attrs = []
        self.name_class = name_class
        self.bases_classes = bases_classes
        self.dict_class = dict_class
        super().__init__(name_class, bases_classes, dict_class)

    def check_class(cls):
        for func in cls.dict_class:
            try:
                instructions = dis.get_instructions(cls.dict_class[func])
            except TypeError:
                pass
            else:
                cls.search_instruction(instructions)
        if not ('SOCK_STREAM' in cls.attrs and 'AF_INET' in cls.attrs):
            raise TypeError('Некорректная инициализация сокета.')
        for command in ('accept', 'listen'):
            if command in cls.methods:
                # print(cls.methods)
                raise TypeError(f'В классе обнаружено использование запрещённого метода {command}')
        if 'get_msg' in cls.methods or 'send_msg' in cls.methods:
            pass
        else:
            raise TypeError('Отсутствуют вызовы функций, работающих с сокетами.')

    def search_instruction(cls, instructions):
        for i in instructions:
            if i.opname == 'LOAD_GLOBAL':
                if i.argval not in cls.methods:
                    cls.methods.append(i.argval)
            elif i.opname == 'LOAD_ATTR':
                if i.argval not in cls.attrs:
                    cls.attrs.append(i.argval)
