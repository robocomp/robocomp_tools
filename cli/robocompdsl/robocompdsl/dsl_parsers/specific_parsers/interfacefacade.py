from collections import UserList, UserDict

from robocompdsl.logger import logger


# interface_struct.methods[method.name] = {}
# interface_struct.methods[method.name]['name'] = method.name
# try:
#     interface_struct.methods[method.name]['decorator'] = method.decorator
# except KeyError:
#     interface_struct.methods[method.name]['decorator'] = ''
#
# interface_struct.methods[method.name]['return'] = method.ret
#
# params = []
# try:
#     for p in method.params:
#         try:
#             params.append({'decorator': p.decorator, 'type': p.type, 'name': p.name})
#         except KeyError:
#             params.append({'decorator': 'none', 'type': p.type, 'name': p.name})
# except KeyError:
#     pass
# interface_struct.methods[method.name]['params'] = params
#
# try:
#     interface_struct.methods[method.name]['throws'] = method.raise.asList()
# except KeyError:
#     interface_struct.methods[method.name]['throws'] = 'nothing'

{
  "type": "interface",
  "name": "CameraRGBDSimple",
  "methods": [
    {
      "ret": "TImage",
      "name": "getImage",
      "params": [
        {
          "type": "string",
          "name": "camera"
        }
      ],
      "raise": [
        "HardwareFailedException"
      ]
    },
    {
      "ret": "TDepth",
      "name": "getDepth",
      "params": [
        {
          "type": "string",
          "name": "camera"
        }
      ],
      "raise": [
        "HardwareFailedException"
      ]
    },
    {
      "ret": "TPoints",
      "name": "getPoints",
      "params": [
        {
          "type": "string",
          "name": "camera"
        }
      ],
      "raise": [
        "HardwareFailedException"
      ]
    },
    {
      "ret": "TRGBD",
      "name": "getAll",
      "params": [
        {
          "type": "string",
          "name": "camera"
        }
      ],
      "raise": [
        "HardwareFailedException"
      ]
    }
  ]
}

class Struct:
    def __init__(self, input_dict):
        super(Struct, self).__init__()
        self.name = input_dict['name']
        self.type = input_dict['type']
        self.methods = Methods(input_dict['methods'])

class Param:
    def __init__(self, param):
        super(Param, self).__init__()
        self.name = param['name']
        self.type = param['type']
        self.decorator = param['decorator'] if 'decorator' in param else 'none'

    def __hash__(self):
        return self.name.__hash__()

    def __eq__(self, other):
        return self.name == other.name

class Params(UserList):
    def __init__(self, params):
        super(Params, self).__init__()
        self.extend([Param(x) for x in params])

    def append(self, item) -> None:
        super(Params, self).append(Param(item))

    def __hash__(self):
        return tuple(self).__hash__()

    def __eq__(self, other):
        return tuple(self) == tuple(other)


class Method:
    def __init__(self, input_dict):
        super(Method, self).__init__()
        self.name = input_dict['name']
        self.ret = input_dict['ret']
        self.params = Params(input_dict['params']) if 'params' in input_dict else []
        self.throws = input_dict['throws'] if 'throws' in input_dict else []
        self.raise_ = input_dict['raise'] if 'raise' in input_dict else []
        self.decorator = input_dict['decorator'] if 'decorator' in input_dict else ''


    def __hash__(self):
        return self.name.__hash__()

    def __eq__(self, other):
        return self.name == other.name


class Methods(UserDict):
    def __init__(self, params):
        super(Methods, self).__init__()
        self.update({x['name']: Method(x) for x in params})

    def __hash__(self):
        return tuple(self).__hash__()

    def __eq__(self, other):
        return tuple(self) == tuple(other)


class Interface:
    def __init__(self, params):
        super(Interface, self).__init__()
        self.name = params['name']
        self.methods = Methods(params['methods'])

    def __setattr__(self, key, value):
        logger.debug("Setting attribute %s to %s" % (key, value))
        if isinstance(value, (list, tuple, dict)):
            if key in CLASS_TYPE_MAP:
                new_class = CLASS_TYPE_MAP[key]
                value = new_class(value)
        super(Interface, self).__setattr__(key, value)
        logger.debug("New attribute %s is %s" % (key, getattr(self, key)))

class Interfaces(UserList):
    def __init__(self, params):
        super(Interfaces, self).__init__()
        self.extend([Interface(x) for x in params])

    def append(self, item):
        logger.debug("Appending Interface %s" % item)
        super(Interfaces, self).append(Interface(item))

    def __hash__(self):
        return tuple(self).__hash__()

    def __eq__(self, other):
        return tuple(self) == tuple(other)


CLASS_TYPE_MAP = {
    "interfaces": Interfaces,
    "methods": Methods,
    "method": Method
}

class InterfaceFacade:
    def __init__(self, nested_dict=None):
        if nested_dict is not None:
            for key, value in nested_dict.items():
                setattr(self, key, value)

    def __setattr__(self, key, value):
        logger.debug("Setting attribute %s to %s" % (key, value))
        if isinstance(value, (list, tuple, dict)):
            if key in CLASS_TYPE_MAP:
                new_class = CLASS_TYPE_MAP[key]
                value = new_class(value)
        super(InterfaceFacade, self).__setattr__(key, value)
        logger.debug("New attribute %s is %s" % (key, getattr(self, key)))

    def __setitem__(self, key, value):
        """
        For compatibility with the smdsl and idsl object format.
        """
        if key == 'filename':
            setattr(self, key, value)
        else:
            raise TypeError('Invalid access to InterfaceFacade by item %s' % key)


    def __eq__(self, other):
        equal = True
        if not isinstance(other, InterfaceFacade):
            return False
        for attr in self.__dict__:
            if hasattr(other, attr):
                equal = equal and getattr(self, attr) == getattr(other, attr)
            else:
                return False
        return equal

    def __len__(self):
        return len(self.__dict__)