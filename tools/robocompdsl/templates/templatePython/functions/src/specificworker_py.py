import datetime
from string import Template

from dsl_parsers.parsing_utils import communication_is_ice, get_name_number



COMPUTE_METHOD_STR = """
@QtCore.Slot()
def compute(self):
    print('SpecificWorker.compute...')
    # computeCODE
    # try:
    #   self.differentialrobot_proxy.setSpeedBase(100, 0)
    # except Ice.Exception as e:
    #   traceback.print_exc()
    #   print(e)

    # The API of python-innermodel is not exactly the same as the C++ version
    # self.innermodel.updateTransformValues('head_rot_tilt_pose', 0, 0, 0, 1.3, 0, 0)
    # z = librobocomp_qmat.QVec(3,0)
    # r = self.innermodel.transform('rgbd', z, 'laser')
    # r.printvector('d')
    # print(r[0], r[1], r[2])

    return True
"""


STATEMACHINE_INITIALIZE_METHOD_STR = """
#
# sm_${state_method}
#
@QtCore.Slot()
def sm_${state_method}(self):
    print("Entered state ${state_method}")
    self.t_initialize_to_compute.emit()
    pass
    
"""

STATEMACHINE_COMPUTE_METHOD_STR = """
#
# sm_${state_method}
#
@QtCore.Slot()
def sm_${state_method}(self):
    print("Entered state ${state_method}")
    self.compute()
    pass

"""

STATEMACHINE_METHOD_STR = """
#
# sm_${state_method}
#
@QtCore.Slot()
def sm_${state_method}(self):
    print("Entered state ${state_method}")
    pass
"""

INTERFACE_TYPES_COMMENT_STR = """\
######################
# From the ${module_name} you can use this types:
${types}
"""

PROXY_METHODS_COMMENT_STR = """\
######################
# From the ${module_name} you can ${action} this methods:
${methods}
"""

class TemplateDict(dict):
    def __init__(self, component):
        super(TemplateDict, self).__init__()
        self.component = component
        self['year'] = str(datetime.date.today().year)
        self['timeout_compute_connect'] = self.timeout_compute_connect()
        self['statemachine_start_and_destroy'] = self.statemachine_start_and_destroy()
        self['compute_creation'] = self.compute_creation()
        self['statemachine_slots'] = self.statemachine_slots()
        self['subscription_methods'] = self.subscription_methods()
        self['implements_methods'] = self.implements_methods()
        self['interface_specific_comment'] = self.interface_specific_comment()

    @staticmethod
    def replace_type_cpp_to_python(t):
        t = t.replace('::', '.')
        t = t.replace('string', 'str')
        return t

    def compute_creation(self):
        result = ""
        statemachine = self.component.statemachine
        if (statemachine is not None and statemachine['machine']['default'] is True) or self.component.statemachine_path is None:
            result += COMPUTE_METHOD_STR
        return result

    # TODO: Refactor main states and substates
    def statemachine_slots(self):
        result = ""
        statemachine = self.component.statemachine
        if statemachine is not None:
            cod_virtuals = ""

            # Generate code for the methods of the StateMachine.
            if statemachine['machine']['contents']['initialstate'] is not None:

                # TODO: code to add comments with the transitions
                # if sm['machine']['contents']['transitions'] is not None:
                #     for transi in sm['machine']['contents']['transitions']:
                #             if sm['machine']['contents']['initialstate'] == trasi["src"]
                #                 codsignals += "<TABHERE>#<TABHERE>%s >>> %s" % ( transi['src'], sm['machine']['contents']['initialstate'])
                # if sm['machine']['contents']['transitions'] is not None:
                #     for transi in sm['machine']['contents']['transitions']:
                #         for dest in transi['dests']:
                #             if  sm['machine']['contents']['initialstate'] == dest
                #                 codsignals += "<TABHERE>#<TABHERE>%s <<< %s"%(sm['machine']['contents']['initialstate'], transi['src'])

                if statemachine['machine']['default']:
                    cod_virtuals += Template(STATEMACHINE_INITIALIZE_METHOD_STR).substitute(state_method=statemachine['machine']['contents']['initialstate'])
                else:
                    cod_virtuals += Template(STATEMACHINE_METHOD_STR).substitute(state_method=statemachine['machine']['contents']['initialstate'])

            if statemachine['machine']['contents']['states'] is not None:
                for state in sorted(statemachine['machine']['contents']['states']):
                    if statemachine['machine']['default']:
                        if state == 'compute':
                            cod_virtuals += Template(STATEMACHINE_COMPUTE_METHOD_STR).substitute(state_method=state)
                    else:
                        cod_virtuals += Template(STATEMACHINE_METHOD_STR).substitute(state_method=state)

            if statemachine['machine']['contents']['finalstate'] is not None:
                cod_virtuals += Template(STATEMACHINE_METHOD_STR).substitute(state_method=statemachine['machine']['contents']['finalstate'])

            # Generate code for the methods of the StateMachine transitions for substates.
            if statemachine['substates'] is not None:
                for substates in statemachine['substates']:
                    # TODO: Add commented header with the parent of this methods.
                    if substates['contents']['initialstate'] is not None:
                        cod_virtuals += Template(STATEMACHINE_METHOD_STR).substitute(state_method=substates['contents']['initialstate'])
                    if substates['contents']['states'] is not None:
                        for state in sorted(substates['contents']['states']):
                            cod_virtuals += Template(STATEMACHINE_METHOD_STR).substitute(state_method=state)
                    if substates['contents']['finalstate'] is not None:
                        cod_virtuals += Template(STATEMACHINE_METHOD_STR).substitute(state_method=substates['contents']['finalstate'])

            result += "# =============== Slots methods for State Machine ===================\n"
            result += "# ===================================================================\n"
            result += cod_virtuals+'\n'
            result += "# =================================================================\n"
            result += "# =================================================================\n"
        return result

    # TODO: Refactor to extract code snippets
    # TODO: isinstance
    # TODO: extract similar code from implements_methods
    def subscription_methods(self):
        pool = self.component.idsl_pool
        result = ""
        for interface in self.component.subscribesTo:
            module = pool.module_providing_interface(interface.name)
            for module_interface in module['interfaces']:
                if module_interface['name'] == interface.name:
                    for mname in module_interface['methods']:
                        method = module_interface['methods'][mname]
                        out_values = []
                        if method['return'] != 'void':
                            out_values.append([method['return'], 'ret'])
                        param_str_a = ''
                        for p in method['params']:
                            if p['decorator'] == 'out':
                                out_values.append([p['type'], p['name']])
                            else:
                                param_str_a += ', ' + p['name']
                        result += '\n'
                        result += '#\n'
                        result += '# ' + 'SUBSCRIPTION to ' + method['name'] + ' method from ' + module_interface['name'] + ' interface\n'
                        result += '#\n'
                        if not communication_is_ice(interface):
                            result += 'def ROS' + module_interface['name'] + "_" + method['name'] + '(self' + param_str_a + "):\n"
                        else:
                            result += 'def ' + module_interface['name'] + "_" + method['name'] + '(self' + param_str_a + "):\n"
                        if method['return'] != 'void': result += "    ret = " + method['return'] + '()\n'
                        result += "    #\n"
                        result += "    #subscribesToCODE\n"
                        result += "    #\n"
                        if len(out_values) == 0:
                            result += "    pass\n\n"
                        elif len(out_values) == 1:
                            if method['return'] != 'void':
                                result += "    return ret\n\n"
                            else:
                                result += "    " + out_values[0][1] + " = " + self.replace_type_cpp_to_python(out_values[0][0]) + "()\n"
                                result += "    return " + out_values[0][1] + "\n\n"
                        else:
                            for v in out_values:
                                if v[1] != 'ret':
                                    result += "    " + v[1] + " = " + self.replace_type_cpp_to_python(v[0]) + "()\n"
                            first = True
                            result += "    return ["
                            for v in out_values:
                                if not first: result += ', '
                                result += v[1]
                                if first:
                                    first = False
                            result += "]\n\n"
        return result

    # TODO: Refactor to extract code snippets
    # TODO: isinstance
    def implements_methods(self):
        pool = self.component.idsl_pool
        result = ""
        if self.component.implements:
            result += "# =============== Methods for Component Implements ==================\n"
            result += "# ===================================================================\n"
            for imp in sorted(self.component.implements):
                if type(imp) == str:
                    im = imp
                else:
                    im = imp[0]
                if not communication_is_ice(imp):
                    module = pool.module_providing_interface(im)
                    for interface in module['interfaces']:
                        if interface['name'] == im:
                            for mname in interface['methods']:
                                method = interface['methods'][mname]
                                result += 'def ROS' + interface['name'] + "_" + method['name'] + "(self, req):\n"
                                result += "    #\n"
                                result += "    # implementCODE\n"
                                result += "    # Example ret = req.a + req.b\n"
                                result += "    #\n"
                                result += "    return " + method['name'] + "Response(ret)\n"
                else:
                    module = pool.module_providing_interface(im)
                    for interface in module['interfaces']:
                        if interface['name'] == im:
                            for mname in interface['methods']:
                                method = interface['methods'][mname]
                                out_values = []
                                if method['return'] != 'void':
                                    out_values.append([method['return'], 'ret'])
                                param_str_a = ''
                                for p in method['params']:
                                    if p['decorator'] == 'out':
                                        out_values.append([p['type'], p['name']])
                                    else:
                                        param_str_a += ', ' + p['name']
                                result += '\n'
                                result += '#\n'
                                result += '# ' + method['name']+'\n'
                                result += '#\n'
                                result += 'def ' + interface['name'] + "_" + method['name'] + '(self' + param_str_a + "):\n"
                                if method['return'] != 'void': result += '    ret = ' + method['return'] + '()\n'
                                result += "    #\n"
                                result += "    # implementCODE\n"
                                result += "    #\n"
                                if len(out_values) == 0:
                                    result += "    pass\n\n"
                                elif len(out_values) == 1:
                                    if method['return'] != 'void':
                                        result += "    return ret\n\n"
                                    else:
                                        result += "    " + out_values[0][1] + " = " + self.replace_type_cpp_to_python(out_values[0][0]) + "()\n"
                                        result += "    return " + out_values[0][1] + "\n\n"
                                else:
                                    for v in out_values:
                                        if v[1] != 'ret':
                                            result += "    " + v[1] + " = " + self.replace_type_cpp_to_python(v[0]) + "()\n"
                                    first = True
                                    result += "    return ["
                                    for v in out_values:
                                        if not first: result += ', '
                                        result += v[1]
                                        if first:
                                            first = False
                                    result += "]\n\n"
            result += "# ===================================================================\n"
            result += "# ===================================================================\n\n"
        return result

    def timeout_compute_connect(self):
        result = ""
        if self.component.statemachine is None:
            result += "self.timer.timeout.connect(self.compute)\n"
        return result

    def statemachine_start_and_destroy(self):
        result = ""
        statemachine = self.component.statemachine
        if statemachine is not None:
            result += "self." + statemachine['machine']['name'] + ".start()\n"
            if statemachine['machine']['default']:
                result += "self.destroyed.connect(self.t_compute_to_finalize)\n"
        return result

    def interface_specific_comment(self):
        result = ""
        interfaces_by_type = {
            "requires": self.component.requires,
            "publishes":  self.component.publishes,
            "implements": self.component.implements,
            "subscribesTo": self.component.subscribesTo
        }
        for interface_type, interfaces in interfaces_by_type.items():
            for interface, num in get_name_number(interfaces):
                if communication_is_ice(interface):
                    proxy_methods_calls = ""
                    module = self.component.idsl_pool.module_providing_interface(interface.name)
                    if interface_type in ["publishes", "requires"]:
                        proxy_reference = "self." + interface.name.lower() + num + "_proxy."
                        if interface_type == 'publishes':
                            action = "publish calling"
                        else:
                            action = "call"
                        for method in module['interfaces'][0]['methods']:
                            proxy_methods_calls += f"# {proxy_reference}{method}(...)\n"
                        if proxy_methods_calls:
                            result += Template(PROXY_METHODS_COMMENT_STR).substitute(module_name=module['name'],
                                                                                     methods=proxy_methods_calls,
                                                                                     action=action)
                    structs_str = ""
                    for struct in module['structs']:
                        structs_str += f"# {struct['name'].replace('/', '.')}\n"
                    if structs_str:
                        result += Template(INTERFACE_TYPES_COMMENT_STR).substitute(module_name=module['name'],
                                                                                   types=structs_str)
        return result