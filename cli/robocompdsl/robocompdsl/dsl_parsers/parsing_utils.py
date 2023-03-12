import os
from pathlib import Path

import pyparsing
from collections import Counter, OrderedDict
from rich.console import Console
from robocompdsl.logger import logger

console = Console()

def communication_is_ice(sb):
    is_ice = True
    if isinstance(sb, str):
        is_ice = True
    elif isinstance(sb, (list, tuple)):
        if len(sb) == 2:
            if sb[1] == 'ros'.lower():
                is_ice = False
            elif sb[1] != 'ice'.lower():
                console.log('Only ICE and ROS are supported', style='yellow')
                raise ValueError("Communication not ros and not ice, but %s" % sb[1])
    else:
        raise ValueError("Parameter %s of invalid type %s" % (str(sb), str(type(sb))))
    return is_ice


def is_valid_pubsub_idsl(idsl):
    for interface in idsl.interfaces:
        if len(interface["methods"]) != 1:
            return False
        for method in interface["methods"].values():
            if method.ret != "void":
                return False
            for param in method.params:
                if param["decorator"] == "out":
                    return False
    return True


def is_valid_rpc_idsl(idsl):
    for interface in idsl.interfaces:
        if len(interface["methods"]) > 0:
            return True
    return False


def is_agm_agent(component):
    assert isinstance(component, (dict, OrderedDict)), \
        "Component parameter is expected to be a dict or OrderedDict but %s" % str(type(component))
    options = component.options
    return 'agmagent' in [x.lower() for x in options]





def get_name_number(names_list):
    """
    Used to add a number in case of multiple equal names
    :param names_list: list of names
    :return:
    """
    assert isinstance(names_list, list), "names_list must be a 'list' of interfaces (list) not %s" % str(type(names_list))
    for index, name in enumerate(names_list):
        assert isinstance(name, (list, tuple)), "names_list elements be a 'list' or tuple not %s" % str(type(names_list))

    ret = []
    c = Counter(names_list)
    keys = sorted(c)

    for k in keys:
        for cont in range(c[k]):
            if cont > 0:
                ret.append([k, str(cont)])
            else:
                ret.append([k, ''])
    return ret


def decorator_and_type_to_const_ampersand(decorator, vtype, module_pool, cpp11=False):
    ampersand = ' & '
    const = ' '
    if vtype in ['float', 'int', 'short', 'long', 'double']:  # MAIN BASIC TYPES
        if decorator in ['out']:  # out
            ampersand = ' &'
            const = ' '
        else:                      # read-only
            ampersand = ' '
            const = 'const '
    elif vtype in ['bool']:        # BOOL SEEM TO BE SPECIAL
        const = ' '
        if decorator in ['out']:  # out
            ampersand = ' &'
        else:                      # read-only
            ampersand = ' '
    elif vtype in ['string']:      # STRINGS
        if decorator in ['out']:  # out
            const = ' '
            ampersand = ' &'
        else:                      # read-only
            const = 'const '
            ampersand = ' &'
    else:                            # GENERIC, USED FOR USER-DEFINED DATA TYPES
        kind = get_kind_from_pool(vtype, module_pool)
        if kind is None:
            get_kind_from_pool(vtype, module_pool, debug=True)
            raise TypeError('error, unknown data structure, map or sequence '+vtype)
        else:
            if kind == 'enum':               # ENUM
                const = ' '
                if decorator in ['out']:  # out
                    ampersand = ' &'
                else:                      # read-only
                    ampersand = ' '
            else:                            # THE REST
                if decorator in ['out']:  # out
                    ampersand = ' &'
                    const = ' '
                else:                      # read-only
                    if not cpp11:
                        ampersand = ' &'
                        const = 'const '
                    else:
                        ampersand = ''
                        const = ''

    return const, ampersand


def get_kind_from_pool(vtype, module_pool, debug=False):
    logger.debug(vtype)
    split = vtype.split("::")
    logger.debug(split)
    if len(split) > 1:
        vtype = split[1]
        mname = split[0]
        logger.debug('SPLIT (' + vtype+'), (' + mname + ')')
        if mname in module_pool:
            logger.debug('dentro SPLIT (' + vtype+'), (' + mname + ')')
            r = get_type_from_module(vtype, module_pool[mname])
            if r is not None: return r
        if mname.startswith("RoboComp"):
            if mname[8:] in module_pool:
                r = get_type_from_module(vtype, module_pool[mname[8:]])
                if r is not None: return r
    else:
        logger.debug('no split')
        for module in module_pool:
            logger.debug('  '+str(module))
            r = get_type_from_module(vtype, module_pool[module])
            if r is not None: return r


def get_type_from_module(vtype, module):
    for t in module['types']:
        if t['name'] == vtype:
            return t['type']
    return None

