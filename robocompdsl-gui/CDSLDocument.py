from PySide2.QtCore import *


class CDSLDocument(QObject):
    languageChange = Signal(str)


    def __init__(self):
        super(CDSLDocument, self).__init__()
        self.doc = []
        self._component_name = ""
        self._communications = {"implements": [], "requires": [], "subscribesTo": [], "publishes": []}
        self._imports = []
        self._requires = []
        self._language = ""
        self._gui = False
        self._current_indentation = 0

    def _t(self):
        doc_str = '\t' * self._current_indentation
        return doc_str

    def open_sec(self):
        doc_str = self._t() + "{"
        self._current_indentation += 1
        return doc_str

    def close_sec(self):
        self._current_indentation -= 1
        doc_str = self._t() + "}"
        return doc_str

    def generate_imports(self):
        doc_str = ""
        for imp in self._imports:
            doc_str += self._t() + "import \"" + imp + "\"\n"
        return doc_str

    def _generate_generic_comunication(self, com_type):
        doc_str = ""
        if com_type in self._communications:
            if len(self._communications[com_type]) > 0:
                doc_str = self._t() + "%s " % (com_type)
                for pos, element in enumerate(self._communications[com_type]):
                    doc_str += element
                    if pos < len(self._communications[com_type]) - 1:
                        doc_str += ", "
                    else:
                        doc_str += ";\n"
        else:
            print("CDSLDocument._generate_generic_comunication: invalid communication type: %s" % com_type)
        return doc_str

    def generate_implements(self):
        return self._generate_generic_comunication("implements")

    def generate_requires(self):
        return self._generate_generic_comunication("requires")

    def generate_publish(self):
        return self._generate_generic_comunication("publishes")

    def generate_subscribes(self):
        return self._generate_generic_comunication("subscribesTo")

    def generate_comunications(self):
        doc_str = self._t() + "Communications\n"
        doc_str += self.open_sec() + "\n"
        doc_str += self.generate_implements()
        doc_str += self.generate_requires()
        doc_str += self.generate_publish()
        doc_str += self.generate_subscribes()
        doc_str += self.close_sec() + ";\n"
        return doc_str

    def generate_language(self):
        doc_str = self._t() + "language " + self._language + ";\n";
        return doc_str

    def generate_ui(self):
        doc_str = ""
        if self._gui:
            doc_str = self._t() + "gui Qt(QWidget);\n"
        return doc_str

    def generate_component(self):
        doc_str = "\nComponent " + self._component_name
        doc_str += "\n" + self.open_sec() + "\n"
        doc_str += self.generate_comunications()
        doc_str += self.generate_language()
        doc_str += self.generate_ui()
        doc_str += self.close_sec() + ";"
        return doc_str

    def generate_doc(self):
        doc_str = ""
        doc_str += self.generate_imports()
        doc_str += self.generate_component()
        return doc_str

    def clear_imports(self):
        self._imports = []

    def add_import(self, import_file):
        self._imports.append(import_file)

    def add_require(self, require_name):
        self._communications["requires"].append(require_name)

    def add_publish(self, publish_name):
        self._communications["publishes"].append(publish_name)

    def add_subscribe(self, subscribe_name):
        self._communications["subscribesTo"].append(subscribe_name)

    def add_implement(self, implement_name):
        self._communications["implements"].append(implement_name)

    def add_comunication(self, com_type, com_name):
        if com_type in self._communications:
            self._communications[com_type].append(com_name)
        else:
            print("CDSLDocument.add_comunication: invalid communication type: %s" % com_type)

    def clear_comunication(self, com_type):
        if com_type in self._communications:
            self._communications[com_type] = []
        else:
            print("CDSLDocument.add_comunication: invalid communication type: %s" % com_type)

    def set_name(self, name):
        self._component_name = name

    def set_qui(self, gui):
        self._gui = gui



    # TESTING
    def clear(self):
        self.doc = []
        self._component_name = ""
        self._communications = {"implements": [], "requires": [], "subscribesTo": [], "publishes": []}
        self._imports = []
        self._requires = []
        self._language = ""
        self._gui = False


    def analize_language(self, s, loc, toks):
        lang = toks.language[0]
        print("analyze language: ", lang)
        if self._language != lang:
            self.set_language(lang)
            self.languageChange.emit(self.get_language())

    def set_language(self, language):
        self._language = language

    def get_language(self):
        return self._language