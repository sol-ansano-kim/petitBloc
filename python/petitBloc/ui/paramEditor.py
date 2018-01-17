from Qt import QtWidgets
from Qt import QtCore
from . import const
import re


class ParamLayout(QtWidgets.QHBoxLayout):
    RegexInt = re.compile("[^0-9-]")
    RegexFloat = re.compile("[^0-9-.]")

    def __init__(self, param):
        super(ParamLayout, self).__init__()
        self.__param = param
        self.__val_edit = None
        self.__initialize()

    def __initialize(self):
        self.setAlignment(QtCore.Qt.AlignLeft)
        label = QtWidgets.QLabel(self.__paramLabel(self.__param.name()))
        label.setMinimumWidth(const.ParamLabelMinimumWidth)
        label.setMaximumWidth(const.ParamLabelMaximumWidth)
        self.addWidget(label)

        tc = self.__param.typeClass()
        if tc == bool:
            self.__val_edit = QtWidgets.QCheckBox()
            self.__val_edit.setChecked(self.__param.get())
            self.__val_edit.stateChanged.connect(self.__boolChanged)
        elif tc == int:
            self.__val_edit = QtWidgets.QLineEdit(str(self.__param.get()))
            self.__val_edit.setMaximumWidth(const.ParamEditorMaximumWidth)
            self.__val_edit.setAlignment(QtCore.Qt.AlignRight)
            self.__val_edit.textEdited.connect(self.__intOnly)
            self.__val_edit.editingFinished.connect(self.__intFinished)
        elif tc == float:
            self.__val_edit = QtWidgets.QLineEdit(str(self.__param.get()))
            self.__val_edit.setMaximumWidth(const.ParamEditorMaximumWidth)
            self.__val_edit.setAlignment(QtCore.Qt.AlignRight)
            self.__val_edit.textEdited.connect(self.__floatOnly)
            self.__val_edit.editingFinished.connect(self.__floatFinished)
        elif tc == str:
            self.__val_edit = QtWidgets.QLineEdit(str(self.__param.get()))
            self.__val_edit.editingFinished.connect(self.__strFinished)

        self.addWidget(self.__val_edit)
        self.setSpacing(10)

        if tc != str:
            self.addStretch(100)

    def __boolChanged(self, state):
        self.__param.set(state == QtCore.Qt.Checked)

    def __intFinished(self):
        txt = self.__val_edit.text()
        try:
            int(txt)
        except:
            self.__val_edit.setText(str(self.__param.get()))
        else:
            if not self.__param.set(int(txt)):
                self.__val_edit.setText(str(self.__param.get()))

    def __floatFinished(self):
        txt = self.__val_edit.text()
        try:
            float(txt)
        except:
            self.__val_edit.setText(str(self.__param.get()))
        else:
            if not self.__param.set(float(txt)):
                self.__val_edit.setText(str(self.__param.get()))

    def __strFinished(self):
        self.__param.set(str(self.__val_edit.text()))

    def __intOnly(self, txt):
        self.__val_edit.setText(ParamLayout.RegexInt.sub("", txt))

    def __floatOnly(self, txt):
        self.__val_edit.setText(ParamLayout.RegexFloat.sub("", txt))

    def __paramLabel(self, txt):
        txt = txt[0].upper() + txt[1:]
        return txt


class ParamEditor(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ParamEditor, self).__init__()
        self.__bloc = None
        self.__param_layout = None
        self.__block_type_label = None
        self.__block_name = None
        self.__initialize()
        self.__refresh()

    def setBlock(self, bloc):
        if self.__bloc == bloc:
            return

        self.__bloc = bloc
        self.__refresh()

    def __initialize(self):
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.__param_layout = QtWidgets.QVBoxLayout()
        self.__block_type_label = QtWidgets.QLabel()
        self.__block_type_label.setAlignment(QtCore.Qt.AlignCenter)
        self.__block_name = QtWidgets.QLineEdit()
        self.__block_name.setMaximumWidth(const.ParamEditorBlockNameMaximumWidth)
        main_layout.addWidget(self.__block_type_label)
        main_layout.addWidget(self.__block_name)
        main_layout.addLayout(self.__param_layout)

        self.setLayout(main_layout)

    def __refresh(self):
        self.__clearLayout(self.__param_layout)
        if self.__bloc is None:
            self.__block_type_label.setText("")
            self.__block_name.setText("")
        else:
            self.__block_name.setText(self.__bloc.name())
            self.__block_type_label.setText(self.__bloc.__class__.__name__)

        self.__build_params()

    def __build_params(self):
        if self.__bloc is None:
            return

        for p in self.__bloc.params():
            lay = ParamLayout(p)
            self.__param_layout.addLayout(lay)

    def __clearLayout(self, layout):
        while (True):
            item = layout.takeAt(0)
            if item:
                l = item.layout()
                w = item.widget()
                if l:
                    self.__clearLayout(l)
                if w:
                    layout.removeWidget(w)
                    w.setParent(None)

            else:
                break
