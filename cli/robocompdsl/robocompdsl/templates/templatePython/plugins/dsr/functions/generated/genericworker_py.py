import datetime

from robocompdsl.dsl_parsers.parsing_utils import communication_is_ice, get_name_number
from robocompdsl.templates.common.templatedict import TemplateDict


DSR_INIT_STR = """\
self.agent_id = configData["Agent"]["id"]
self.g = DSRGraph(0, configData["Agent"]["name"], self.agent_id, configData["Agent"]["configFile"])
"""


class src_genericworker_py(TemplateDict):
    def __init__(self, component):
        super(src_genericworker_py, self).__init__()
        self.component = component
        self['year'] = str(datetime.date.today().year)
        self['requires_proxies'] = self.requires_proxies()
        self['publishes_proxies'] = self.publishes_proxies()
        self['insert_dsr'] = self.insert_dsr()
        self['import_dsr'] = self.import_dsr()



    def import_dsr(self):
        if self.component.dsr:
            return "from pydsr import DSRGraph"
        else:
            return ""

    def insert_dsr(self):
        if self.component.dsr:
            return DSR_INIT_STR
        else:
            return ""

    # TODO: Refactor this and publishes with a zip?
    def requires_proxies(self):
        result = ""
        for req, num in get_name_number(self.component.requires):
            if isinstance(req, str):
                rq = req
            else:
                rq = req[0]
            if communication_is_ice(req):
                result += "self." + rq.lower() + num + "_proxy = mprx[\"" + rq  + num + "\"]\n"
            else:
                result += "self." + rq.lower() + "_proxy = ServiceClient" + rq + "()\n"
        return result

    def publishes_proxies(self):
        result = ""
        for pb, num in get_name_number(self.component.publishes):
            if isinstance(pb, str):
                pub = pb
            else:
                pub = pb[0]
            if communication_is_ice(pb):
                result += "self." + pub.lower() + num + "_proxy = mprx[\"" + pub + num + "\"]\n"
            else:
                result += "self." + pub.lower() + "_proxy = Publisher" + pub + "()\n"
        return result
