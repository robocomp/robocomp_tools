import os
import re
import signal
import sys

from PySide2.QtCore import *
from PySide2 import QtCore
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from ui_gui import Ui_MainWindow
from parseGUI import LoadInterfaces


# DETECT THE ROBOCOMP INSTALLATION TO IMPORT RCPORTCHECKER CLASS
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROBOCOMP = ''
ROBOCOMP_COMP_DIR = os.path.join(os.path.expanduser("~"), "robocomp", "components")
ROBOCOMPDSL_DIR = os.path.join(CURRENT_DIR, "..", "robocompdsl")

try:
    ROBOCOMP = os.environ['ROBOCOMP']
except:
    default_robocomp_path = '/opt/robocomp'
    print('ROBOCOMP environment variable not set! Trying default directory (%s)' % (default_robocomp_path))
    if os.path.exists(default_robocomp_path) and os.path.isdir(default_robocomp_path):
        if not os.listdir(default_robocomp_path):
            print("Default Robocomp directory (%s) exists but it's empty. Exiting!" % (default_robocomp_path))
            sys.exit()
        else:
            ROBOCOMP = default_robocomp_path
    else:
        print("Default Robocomp directory (%s) doesn't exists. Exiting!" % (default_robocomp_path))
        sys.exit()
# sys.path.append(os.path.join(ROBOCOMP, "tools/rcportchecker"))

ROBOCOMP_INTERFACES = os.path.join(ROBOCOMP, "interfaces")
if not os.path.isdir(ROBOCOMP_INTERFACES):
    new_path = os.path.join(os.path.expanduser("~"), "robocomp", "interfaces")
    print('ROBOCOMP INTERFACES not found at %s! Trying HOME directory (%s)' % (ROBOCOMP_INTERFACES, new_path))
    ROBOCOMP_INTERFACES = new_path
    if not os.path.isdir(ROBOCOMP_INTERFACES):
        print("Default Robocomp INTERFACES directory (%s) doesn't exists. Exiting!" % (ROBOCOMP_INTERFACES))
        sys.exit()

class CDSLLanguage:
    CPP = "CPP"
    PYTHON = "Python"

class CDSLGui:
    QWIDGET = "QWidget"
    QDIALOG = "QDialog"
    QMAINWINDOW = "QMainWindow"

class CDSLDocument:
    def __init__(self):
        self.doc = []
        self._component_name = ""
        self._communications = {"implements": [], "requires": [], "subscribesTo": [], "publishes": []}
        self._imports = set()
        self._requires = []
        self._language = CDSLLanguage.PYTHON
        self._gui = False
        self._gui_combo = CDSLGui.QWIDGET
        self._agmagent = False
        self._innerModel = False
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
            doc_str += self._t() + "import \"" + imp + "\";\n"
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
            print ("CDSLDocument._generate_generic_comunication: invalid communication type: %s" % com_type)
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
        doc_str = self._t() + "communications\n"
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
            doc_str = self._t() + "gui Qt(" + self._gui_combo + ");\n"
        return doc_str

    def generate_agmagent(self):
        doc_str = ""
        if self._agmagent:
            doc_str = self._t() + "options agmagent;\n"
        return doc_str

    def generate_innerModel(self):
        doc_str = ""
        if self._innerModel:
            doc_str = self._t() + "options innerModelViewer;\n"
        return doc_str

    def generate_component(self):
        doc_str = "\ncomponent " + self._component_name
        doc_str += "\n" + self.open_sec() + "\n"
        doc_str += self.generate_comunications()
        doc_str += self.generate_language()
        doc_str += self.generate_ui()
        doc_str += self.generate_agmagent()
        doc_str += self.generate_innerModel()
        doc_str += self.close_sec() + ";"
        return doc_str

    def generate_doc(self):
        doc_str = ""
        doc_str += self.generate_imports()
        doc_str += self.generate_component()
        return doc_str

    def clear_imports(self):
        self._imports.clear()

    def add_import(self, import_file):
        self._imports.add(import_file)

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
            print ("CDSLDocument.add_comunication: invalid communication type: %s" % com_type)

    def clear_comunication(self, com_type):
        if com_type in self._communications:
            self._communications[com_type] = []
        else:
            print("CDSLDocument.add_comunication: invalid communication type: %s" % com_type)

    def set_name(self, name):
        self._component_name = name

    def set_language(self, language):
        self._language = language

    def set_qui(self, gui):
        self._gui = gui

    def set_gui_combo(self, gui_combo):
        self._gui_combo = gui_combo

    def set_agmagent(self, agmagent):
        self._agmagent = agmagent

    def set_innerModel(self, innerModel):
        self._innerModel = innerModel

class Highlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(Highlighter, self).__init__(parent)

        keywordFormat = QTextCharFormat()
        keywordFormat.setForeground(Qt.darkBlue)
        keywordFormat.setFontWeight(QFont.Bold)

        keywordPatterns = ["\\bimport\\b", "\\bcomponent\\b", "\\bcommunications\\b",
                "\\bpublishes\\b", "\\bimplements\\b", "\\bsubscribesTo\\b", "\\brequires\\b",
                "\\blanguage\\b", "\\bgui\\b", "\\boptions\\b","\\binnerModelViewer\\b","\\bstateMachine\\b","\\bmodules\\b","\\bagmagent\\b"]

        self.highlightingRules = [(QRegExp(pattern), keywordFormat)
                for pattern in keywordPatterns]

        self.multiLineCommentFormat = QTextCharFormat()
        self.multiLineCommentFormat.setForeground(Qt.red)

        self.commentStartExpression = QRegExp("/\\*")
        self.commentEndExpression = QRegExp("\\*/")

    def highlightBlock(self, text):
        for pattern, format in self.highlightingRules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        startIndex = 0
        if self.previousBlockState() != 1:
            startIndex = self.commentStartExpression.indexIn(text)

        while startIndex >= 0:
            endIndex = self.commentEndExpression.indexIn(text, startIndex)

            if endIndex == -1:
                self.setCurrentBlockState(1)
                commentLength = len(text) - startIndex
            else:
                commentLength = endIndex - startIndex + self.commentEndExpression.matchedLength()

            self.setFormat(startIndex, commentLength,
                    self.multiLineCommentFormat)
            startIndex = self.commentStartExpression.indexIn(text,
                    startIndex + commentLength);


class RoboCompDSLGui(QMainWindow):
    def __init__(self):
        super(RoboCompDSLGui, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self._communications = {"implements": [], "requires": [], "subscribesTo": [], "publishes": []}
        self._interfaces = {}
        self._cdsl_doc = CDSLDocument()
        self._command_process = QProcess()

        #COMPONENT NAME
        self.ui.nameLineEdit.textEdited.connect(self.update_component_name)

        #DIRECTORY SELECTION
        self._dir_completer = QCompleter()
        self._dir_completer_model = QFileSystemModel()
        if os.path.isdir(ROBOCOMP_COMP_DIR):
            self.ui.directoryLineEdit.setText(ROBOCOMP_COMP_DIR)
            self._dir_completer_model.setRootPath(ROBOCOMP_COMP_DIR)
        self._dir_completer.setModel(self._dir_completer_model)
        self.ui.directoryLineEdit.setCompleter(self._dir_completer)
        self.ui.directoryButton.clicked.connect(self.set_output_directory)

        #CUSTOM INTERFACES LIST WIDGET
        self._interface_list = customListWidget(self.ui.centralWidget)
        self.ui.gridLayout.addWidget(self._interface_list, 4, 0, 8, 2)
        self._interface_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self._interface_list.customItemSelection.connect(self.set_comunication)

        #LIST OF CONNECTION TYPES
        self.ui.communicationsComboBox.currentIndexChanged.connect(self.reselect_existing)

        #LANGUAGE
        self.ui.languageComboBox.currentIndexChanged.connect(self.update_language)

        #GUI CHECKBOX
        self.ui.guiCheckBox.stateChanged.connect(self.update_gui)

        #GUI COMBOBOX
        self.ui.guiComboBox.currentIndexChanged.connect(self.update_gui_combo)

        #AGMAGENT CHECKBOX
        self.ui.agmagentCheckBox.stateChanged.connect(self.update_agmagent_selection)

        #INNERMODEL CHECKBOX
        self.ui.innermodelCheckBox.stateChanged.connect(self.update_innerModel_selection)

        #MAIN TEXT EDITOR
        self.ui.mainTextEdit.setHtml("")
        self._document = self.ui.mainTextEdit.document()
        self._component_directory = None
        self.ui.mainTextEdit.setText(self._cdsl_doc.generate_doc())

        #CONSOLE
        self._console = QConsole(self.ui.centralWidget)
        self.ui.gridLayout_2.addWidget(self._console, 1, 0, 3, 1)
        self._command_process.readyReadStandardOutput.connect(self._console.standard_output)
        self._command_process.readyReadStandardError.connect(self._console.error_output)

        #RESET BUTTON
        self.ui.resetButton.clicked.connect(self.reset_cdsl_file)

        #CREATION BUTTON
        self.ui.createButton.clicked.connect(self.write_cdsl_file)

        #GENERATE BUTTON
        self.ui.generateButton.clicked.connect(self.robocompdsl_generate_component)

        self.setupEditor()
        self.load_idsl_files()

    def setupEditor(self):
        self.highlighter = Highlighter(self.ui.mainTextEdit.document())

    def load_idsl_files(self):
        idsls_dir = os.path.join(ROBOCOMP_INTERFACES, "IDSLs")
        self._interfaces = LoadInterfaces.load_all_interfaces(LoadInterfaces, idsls_dir)
        self._interface_list.addItems(list(self._interfaces.keys()))

    def set_comunication(self):
        interfaces_names = self._interface_list.customItemList()
        com_type = str(self.ui.communicationsComboBox.currentText())
        self._communications[com_type] = []
        self._cdsl_doc.clear_comunication(com_type)
        for iface_name_item in interfaces_names:
            iface_name = iface_name_item
            self._communications[com_type].append(iface_name)
            self._cdsl_doc.add_comunication(com_type, iface_name)
        self.update_imports()
        self.update_editor()

    def update_imports(self):
        self._cdsl_doc.clear_imports()
        for com_type in self._communications:
            for iface_name in self._communications[com_type]:
                imports_list = LoadInterfaces.get_files_from_interface(iface_name)
                for imp in imports_list:
                    idsl_full_filename = imp
                    self._cdsl_doc.add_import(idsl_full_filename)

    def update_language(self):
        language = self.ui.languageComboBox.currentText()
        self._cdsl_doc.set_language(str(language))
        self.update_editor()

    def update_gui(self):
        checked = self.ui.guiCheckBox.isChecked()
        if checked:
            self._cdsl_doc.set_qui(True)
            self.ui.guiComboBox.setEnabled(True)
        else:
            self._cdsl_doc.set_qui(False)
            self.ui.guiComboBox.setEnabled(False)
        self.update_editor()

    def update_gui_combo(self):
        gui_combo = self.ui.guiComboBox.currentText()
        self._cdsl_doc.set_gui_combo(str(gui_combo))
        self.update_editor()

    def update_agmagent_selection(self):
        checked = self.ui.agmagentCheckBox.isChecked()
        if checked:
            self._cdsl_doc.set_agmagent(True)
        else:
            self._cdsl_doc.set_agmagent(False)
        self.update_editor()

    def update_innerModel_selection(self):
        checked = self.ui.innermodelCheckBox.isChecked()
        if checked:
            self._cdsl_doc.set_innerModel(True)
        else:
            self._cdsl_doc.set_innerModel(False)
        self.update_editor()

    def update_component_name(self, name):
        self._cdsl_doc.set_name(name)
        self.update_editor()

    def update_editor(self):
        self.ui.mainTextEdit.setText(self._cdsl_doc.generate_doc())

    def set_output_directory(self):
        dir_set = False
        while not dir_set:
            dir = QFileDialog.getExistingDirectory(self, "Select Directory",
                                                   ROBOCOMP_COMP_DIR,
                                                   QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
            if self.check_dir_is_empty(str(dir)):
                self.ui.directoryLineEdit.setText(dir)
                dir_set = True

    def reset_cdsl_file(self):
        self._communications = {"implements": [], "requires": [], "subscribesTo": [], "publishes": []}
        self._interfaces = {}
        self._cdsl_doc = CDSLDocument()
        self._command_process = QProcess()
        self.update_editor()

    def write_cdsl_file(self):
        component_dir = str(self.ui.directoryLineEdit.text())
        text = self._cdsl_doc.generate_doc()
        if not self.ui.nameLineEdit.text():
            component_name, ok = QInputDialog.getText(self, 'No component name set', 'Enter component name:')
            if ok:
                self.update_component_name(component_name)
                self.ui.nameLineEdit.setText(component_name)
            else:
                return False

        if not os.path.exists(component_dir):
            if QMessageBox.Yes == QMessageBox.question(self,
                                                       "Directory doesn't exist.",
                                                       "Do you want create the directory %s?" % component_dir,
                                                       QMessageBox.Yes | QMessageBox.No):
                os.makedirs(component_dir)
            else:
                QMessageBox.question(self,
                                     "Directory not exist",
                                     "Can't create a component witout a valid directory")
                return False

        file_path = os.path.join(component_dir, str(self.ui.nameLineEdit.text()) + ".cdsl")
        if os.path.exists(file_path):
            if QMessageBox.No == QMessageBox.question(self,
                                                      "File already exists",
                                                      "Do you want to overwrite?",
                                                      QMessageBox.Yes | QMessageBox.No):
                return False

        with open(file_path, 'w') as the_file:
            #check if file is written correctly
            the_file.write(text)
        #self.execute_robocomp_cdsl()
        return True

    def robocompdsl_generate_component(self):
        self.write_cdsl_file()
        self.execute_robocomp_cdsl()

    def execute_robocomp_cdsl(self):
        cdsl_file_path = os.path.join(str(self.ui.directoryLineEdit.text()), str(self.ui.nameLineEdit.text()) + ".cdsl")
        command = "python -u %s/robocompdsl.py %s %s" % (
            ROBOCOMPDSL_DIR, cdsl_file_path, os.path.join(str(self.ui.directoryLineEdit.text())))
        self._console.append_custom_text("%s\n" % command)
        self._command_process.start(command, QProcess.Unbuffered | QProcess.ReadWrite)

    def reselect_existing(self):
        com_type = self.ui.communicationsComboBox.currentText()
        selected = self._communications[com_type]
        #self.ui.interfacesListWidget.clearSelection()
        self._interface_list.clearItems()

        for iface in selected:
            items = self._interface_list.findItems(iface, Qt.MatchFlag.MatchExactly)
            if len(items) > 0:
                item = items[0]
                item.setSelected(True)

    def check_dir_is_empty(self, dir_path):
        if len(os.listdir(dir_path)) > 0:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("Directory not empty")
            msgBox.setText("The selected directory is not empty.\n"
                           "For a new Component you usually want a new directory.\n"
                           "Do you want to use this directory anyway?")
            msgBox.setStandardButtons(QMessageBox.Yes)
            msgBox.addButton(QMessageBox.No)
            msgBox.setDefaultButton(QMessageBox.No)
            if msgBox.exec_() == QMessageBox.Yes:
                return True
            else:
                return False
        else:
            return True

class QConsole(QTextEdit):
    def __init__(self, parent=None):
        super(QConsole, self).__init__(parent)
        font = QFont("Monospace",9)
        font.setStyleHint(QFont.TypeWriter)
        self.setFont(font)
        # self.setFontWeight(QFont.Light)
        # self.setFontPointSize(9)
        self.setTextColor(QColor("LightGreen"))
        p = self.palette()
        #p.setColor(QPalette.Base, QColor(4, 11, 50))
        self.setMinimumSize(QtCore.QSize(0, 130))
        self.setStyleSheet("background-color: rgb(4, 11, 50);")
        #self.setObjectName("console")
        self.setPalette(p)
        self.setText(">\n")

    def append_custom_text(self, text):
        self.setTextColor(QColor("white"))
        self.append(text)

    def standard_output(self):
        self.setTextColor(QColor("LightGreen"))
        process = self.sender()
        text = process.readAllStandardOutput()
        self.append(str(text))

    def error_output(self):
        self.setTextColor(QColor("red"))
        process = self.sender()
        text = process.readAllStandardError()
        self.append(str(text))

class customListWidget(QListWidget):
    itemList = []
    customItemSelection = Signal()

    def __init__(self, parent=None):
        super(customListWidget, self).__init__(parent)
        self.itemList = []
        self.setMinimumSize(QtCore.QSize(160, 0))
        self.setMaximumSize(QtCore.QSize(245, 16777215))
        # self.setObjectName("customListWidget")

    def mousePressEvent(self, event):
        super(customListWidget, self).mousePressEvent(event)
        item = self.itemAt(event.pos())
        if item:
            text = item.text().split(":")[0]
            # check button clicked
            if event.button() == Qt.LeftButton:
                if (event.modifiers() == Qt.ShiftModifier) or (event.modifiers() == Qt.ControlModifier):
                    self.itemList.append(text)
                else:
                    count = self.itemList.count(text)
                    self.clearItems()
                    for c in range(count + 1):
                        self.itemList.append(text)
            elif event.button() == Qt.RightButton:
                if text in self.itemList:
                    self.itemList.remove(text)

            # update list text
            count = self.itemList.count(text)
            self.itemAt(event.pos()).setSelected(count)
            if count:
                self.itemAt(event.pos()).setText(text + ":" + str(count))
            else:
                self.itemAt(event.pos()).setText(text)

            self.customItemSelection.emit()
        else:
            self.clearItems()

    def clearItems(self):
        self.itemList = []
        for pos in range(self.count()):
            self.item(pos).setText(self.item(pos).text().split(":")[0])

    # return our custom selected item list
    def customItemList(self):
        return self.itemList

    # just for testing
    @Slot()
    def print(self):
        print("Selected items\n", self.itemList)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    gui = RoboCompDSLGui()
    gui.show()

    sys.exit(app.exec_())
