from Qt import QtWidgets
from Qt import QtCore
from Qt import QtGui
from . import const
from . import uiUtil
from .. import util
from .. import box
from .. import core
from functools import partial
import re


ReEqual = re.compile("^\s*[=]\s*")


class ParamCreator(QtWidgets.QDialog):
    ParamTypes = {"bool": bool, "int": int, "float": float, "str": str}

    def __init__(self, parent=None):
        super(ParamCreator, self).__init__(parent=parent)
        self.__type = None
        self.__name = None

        main_layout = QtWidgets.QVBoxLayout()

        param_layout = QtWidgets.QHBoxLayout()
        param_layout.addWidget(QtWidgets.QLabel("Type :"))
        self.__type_combo = QtWidgets.QComboBox()
        self.__type_combo.addItems(ParamCreator.ParamTypes.keys())
        param_layout.addWidget(self.__type_combo)
        param_layout.addWidget(QtWidgets.QLabel("Name :"))
        self.__name_line = QtWidgets.QLineEdit()
        param_layout.addWidget(self.__name_line)
        main_layout.addLayout(param_layout)

        button_layout = QtWidgets.QHBoxLayout()
        self.__add = QtWidgets.QPushButton("Add")
        self.__cancel = QtWidgets.QPushButton("Cancel")
        button_layout.addWidget(self.__add)
        button_layout.addWidget(self.__cancel)
        main_layout.addLayout(button_layout)

        self.__add.clicked.connect(self.accept)
        self.__cancel.clicked.connect(self.reject)

        self.__type_combo.currentIndexChanged.connect(self.__typeChanged)
        self.__name_line.editingFinished.connect(self.__nameChanged)
        self.__name_line.textEdited.connect(self.__nameCheck)

        self.setLayout(main_layout)

    def exec_(self):
        self.__name = None
        self.__type_combo.setCurrentIndex(0)
        self.__typeChanged(0)
        self.__name_line.setText("")
        self.__nameCheck("")

        return super(ParamCreator, self).exec_()

    def __typeChanged(self, a):
        self.__type = ParamCreator.ParamTypes[self.__type_combo.itemText(a)]

    def __nameChanged(self):
        self.__name = str(self.__name_line.text())

    def __nameCheck(self, text):
        self.__add.setEnabled((True if text else False))

    def getType(self):
        return self.__type

    def getName(self):
        return self.__name


class ParamEnum(QtWidgets.QComboBox):
    Changed = QtCore.Signal()

    def __init__(self, param, parent=None):
        super(ParamEnum, self).__init__(parent=parent)
        self.__param = param
        self.addItems(param.getLabels())
        self.setCurrentIndex(param.get())
        self.currentIndexChanged.connect(self.__indexChanged)

    def __indexChanged(self, index):
        self.__param.set(index)
        self.Changed.emit()


class ParamLine(QtWidgets.QLineEdit):
    Value = 0
    Expression = 1
    ExpressionError = 2

    Changed = QtCore.Signal()

    def __init__(self, param, parent=None, isInt=False, isFloat=False):
        super(ParamLine, self).__init__(parent=parent)
        self.__style = "QLineEdit{ background-color: %s; border: 1px solid #1D1D1D; }"
        self.__normal_color = "#1D1D1D"
        self.__expression_color = "#0A4646"
        self.__expression_error_color = "#640A28"
        self.__current_state = ParamLine.Value
        self.__param = param

        if isInt:
            self.textEdited.connect(self.__intOnly)
            self.setAlignment(QtCore.Qt.AlignRight)
            self.editingFinished.connect(self.__intFinished)
        elif isFloat:
            self.textEdited.connect(self.__floatOnly)
            self.setAlignment(QtCore.Qt.AlignRight)
            self.editingFinished.connect(self.__floatFinished)
        else:
            self.editingFinished.connect(self.__strFinished)

        self.blockSignals(True)
        self.setText(str(self.__param.get()))
        self.blockSignals(False)

        self.refresh()

    def refresh(self):
        if not self.__param.hasExpression():
            self.__current_state = ParamLine.Value
        elif self.__param.validExpression():
            self.__current_state = ParamLine.Expression
        else:
            self.__current_state = ParamLine.ExpressionError

        self.blockSignals(True)

        if self.hasFocus() and self.__param.hasExpression():
            self.setText(str(self.__param.getExpression()))
        else:
            self.setText(str(self.__param.get()))

        self.blockSignals(False)

        self.__setBackgroundColor()

    def focusInEvent(self, evnt):
        super(ParamLine, self).focusInEvent(evnt)
        self.refresh()

    def focusOutEvent(self, evnt):
        super(ParamLine, self).focusOutEvent(evnt)
        self.refresh()

    def __setBackgroundColor(self):
        if self.__current_state == ParamLine.Value:
            s = self.__style % self.__normal_color
        elif self.__current_state == ParamLine.Expression:
            s = self.__style % self.__expression_color
        elif self.__current_state == ParamLine.ExpressionError:
            s = self.__style % self.__expression_error_color

        self.setStyleSheet(s)

    def __intOnly(self, txt):
        if not ReEqual.search(txt):
            self.setText(ParamLayout.RegexInt.sub("", txt))

    def __floatOnly(self, txt):
        if not ReEqual.search(txt):
            self.setText(ParamLayout.RegexFloat.sub("", txt))

    def __intFinished(self):
        txt = str(self.text())

        if ReEqual.search(txt):
            if self.__param.setExpression(txt):
                self.Changed.emit()
                return

        try:
            int(txt)
        except:
            self.setText(str(self.__param.get()))
        else:
            self.__param.setExpression(None)
            if not self.__param.set(int(txt)):
                self.setText(str(self.__param.get()))

        self.Changed.emit()

    def __floatFinished(self):
        txt = str(self.text())

        if ReEqual.search(txt):
            if self.__param.setExpression(txt):
                self.Changed.emit()
                return

        try:
            float(txt)
        except:
            self.setText(str(self.__param.get()))
        else:
            self.__param.setExpression(None)
            if not self.__param.set(float(txt)):
                self.setText(str(self.__param.get()))

        self.Changed.emit()

    def __strFinished(self):
        txt = str(self.text())

        if ReEqual.search(txt):
            self.__param.setExpression(txt)
        else:
            self.__param.setExpression(None)
            self.__param.set(txt)

        self.Changed.emit()


class ColorPicker(QtWidgets.QHBoxLayout):
    Changed = QtCore.Signal()

    def __init__(self, r, g, b):
        super(ColorPicker, self).__init__()
        self.__r = r
        self.__g = g
        self.__b = b
        self.__button = None
        self.__style = "QPushButton{ background-color: rgb(%s, %s, %s); border: 1px solid #1D1D1D; }"
        self.initialize()
        self.refresh()

    def initialize(self):
        self.setAlignment(QtCore.Qt.AlignLeft)
        __label = QtWidgets.QLabel("Color")
        __label.setMinimumWidth(const.ParamLabelMinimumWidth)
        __label.setMaximumWidth(const.ParamLabelMaximumWidth)
        self.__button = QtWidgets.QPushButton()
        self.addWidget(__label)
        self.addWidget(self.__button)

        self.__button.clicked.connect(self.__pickColor)

    def refresh(self):
        self.__button.setStyleSheet(self.__style % (self.__r.get(), self.__g.get(), self.__b.get()))
        self.Changed.emit()

    def __pickColor(self):
        color = QtWidgets.QColorDialog.getColor(QtGui.QColor(self.__r.get(), self.__g.get(), self.__b.get()), self.__button)
        if not color.isValid():
            return

        self.__r.set(color.red())
        self.__g.set(color.green())
        self.__b.set(color.blue())
        self.refresh()


class ParamLayout(QtWidgets.QHBoxLayout):
    RegexInt = re.compile("[^0-9-]")
    RegexFloat = re.compile("[^0-9-.]")
    ParameterEdited = QtCore.Signal()
    DeleteRequest = QtCore.Signal(object)

    def __init__(self, param, deletable=False):
        super(ParamLayout, self).__init__()
        self.__label = None
        self.__param = param
        self.__val_edit = None
        self.__delete_button = None
        self.__need_to_refresh = True
        self.__deletable = deletable
        self.__initialize()

    def refresh(self):
        if self.__need_to_refresh:
            self.__val_edit.refresh()

    def __initialize(self):
        self.setAlignment(QtCore.Qt.AlignLeft)
        self.__label = QtWidgets.QLabel(self.__param.name())
        self.__label.setMinimumWidth(const.ParamLabelMinimumWidth)
        self.__label.setMaximumWidth(const.ParamLabelMaximumWidth)
        self.addWidget(self.__label)

        tc = self.__param.typeClass()
        if tc == bool:
            self.__val_edit = QtWidgets.QCheckBox()
            self.__val_edit.setChecked(self.__param.get())
            self.__val_edit.stateChanged.connect(self.__boolChanged)
            self.__need_to_refresh = False
        elif tc == int:
            self.__val_edit = ParamLine(self.__param, isInt=True)
            self.__val_edit.Changed.connect(self.__editedEmit)
        elif tc == float:
            self.__val_edit = ParamLine(self.__param, isFloat=True)
            self.__val_edit.Changed.connect(self.__editedEmit)
        elif tc == str:
            self.__val_edit = ParamLine(self.__param)
            self.__val_edit.Changed.connect(self.__editedEmit)
        elif tc == core.PBEnum:
            self.__val_edit = ParamEnum(self.__param)
            self.__val_edit.Changed.connect(self.__editedEmit)
            self.__need_to_refresh = False

        self.__delete_button = QtWidgets.QPushButton()
        self.__delete_button.setObjectName("RemoveButton")
        self.__delete_button.setFixedSize(14, 14)
        self.__delete_button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.__delete_button.clicked.connect(self.__deleteParam)
        if not self.__deletable:
            self.__delete_button.hide()

        self.addWidget(self.__val_edit)
        self.addWidget(self.__delete_button)

        self.setSpacing(10)

    def __deleteParam(self):
        self.DeleteRequest.emit(self.__param)

    def __boolChanged(self, state):
        self.__param.set(state == QtCore.Qt.Checked)
        self.__editedEmit()

    def __editedEmit(self):
        self.ParameterEdited.emit()


class ParamEditor(QtWidgets.QWidget):
    BlockRenamed = QtCore.Signal(object, str)
    DeleteRequest = QtCore.Signal(object, object)
    NodeRefreshRequest = QtCore.Signal(object)

    def __init__(self, parent=None):
        super(ParamEditor, self).__init__()
        self.__bloc = None
        self.__param_layout = None
        self.__block_type_label = None
        self.__name_label = None
        self.__block_name = None
        self.__add_param_button = None
        self.__param_creator = None
        self.__params = []
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

        name_layout = QtWidgets.QHBoxLayout()
        self.__block_name = QtWidgets.QLineEdit()
        self.__name_label = QtWidgets.QLabel("Name")
        self.__name_label.setMinimumWidth(const.ParamLabelMinimumWidth + 4)
        self.__name_label.setMaximumWidth(const.ParamLabelMaximumWidth)
        name_layout.addWidget(self.__name_label)
        name_layout.addWidget(self.__block_name)
        name_layout.setAlignment(QtCore.Qt.AlignLeft)
        name_layout.addStretch(10)
        self.__block_name.setMaximumWidth(const.ParamEditorBlockNameMaximumWidth)

        add_layout = QtWidgets.QHBoxLayout()
        self.__add_param_button = QtWidgets.QPushButton()
        self.__add_param_button.setObjectName("AddButton")
        self.__add_param_button.setFixedSize(18, 18)
        self.__add_param_button.setFocusPolicy(QtCore.Qt.NoFocus)
        add_layout.setAlignment(QtCore.Qt.AlignCenter)
        add_layout.addWidget(self.__add_param_button)

        main_layout.addWidget(self.__block_type_label)
        main_layout.addLayout(name_layout)
        main_layout.addLayout(self.__param_layout)
        main_layout.addLayout(add_layout)
        self.__add_param_button.hide()

        self.setLayout(main_layout)

        self.__param_creator = ParamCreator(self)

        self.__add_param_button.clicked.connect(self.__addParam)
        self.__block_name.editingFinished.connect(self.__renameBloc)
        self.__block_name.textEdited.connect(self.__nameCheck)

    def __nameCheck(self, txt):
        self.__block_name.setText(util.ReForbiddenName.sub("", txt))

    def __renameBloc(self):
        if not self.__bloc:
            self.__block_name.setText(self.__block.name())

        parent_box = self.__bloc.parent()

        if not parent_box:
            self.__block_name.setText(self.__block.name())

        old_name = self.__bloc.name()
        new_name = self.__block_name.text()

        if old_name == new_name:
            return

        if not util.ValidateName(new_name):
            self.__block_name.setText(old_name)
            return

        uniq_name = parent_box.getUniqueName(self.__bloc, new_name)
        self.__bloc.rename(uniq_name)
        self.__block_name.setText(uniq_name)

        if old_name == uniq_name:
            return

        self.BlockRenamed.emit(self.__bloc, uniq_name)

    def __refresh(self):
        self.__params = []

        self.__clearLayout(self.__param_layout)
        if self.__bloc is None:
            self.__block_type_label.setText("")
            self.__block_name.setText("")
            self.__block_type_label.hide()
            self.__name_label.hide()
            self.__block_name.hide()
            self.__add_param_button.hide()
        else:
            self.__block_type_label.show()
            self.__name_label.show()
            self.__block_name.show()
            self.__block_name.setText(self.__bloc.name())
            self.__block_type_label.setText("<{}>".format(self.__bloc.__class__.__name__))

            if self.__bloc and self.__bloc.expandable():
                self.__add_param_button.show()
            else:
                self.__add_param_button.hide()

            if isinstance(self.__bloc, box.SceneContext):
                self.__block_name.setEnabled(False)
            else:
                self.__block_name.setEnabled(True)

        self.__build_params()

    def __build_params(self):
        if self.__bloc is None:
            return

        if self.__bloc.isBlank():
            lay = ColorPicker(self.__bloc.param("r"), self.__bloc.param("g"), self.__bloc.param("b"))
            lay.Changed.connect(partial(self.NodeRefreshRequest.emit, self.__bloc))
            self.__params.append(lay)
            self.__param_layout.addLayout(lay)
            return

        for p in self.__bloc.params(includeExtraParam=False):
            lay = ParamLayout(p)
            lay.ParameterEdited.connect(self.__update_all_params)
            lay.DeleteRequest.connect(self.__deleteParam)
            self.__params.append(lay)
            self.__param_layout.addLayout(lay)

        for p in self.__bloc.extraParams():
            lay = ParamLayout(p, deletable=True)
            lay.ParameterEdited.connect(self.__update_all_params)
            lay.DeleteRequest.connect(self.__deleteParam)
            self.__params.append(lay)
            self.__param_layout.addLayout(lay)

    def __addParam(self):
        if self.__param_creator.exec_() == QtWidgets.QDialog.Accepted:
            type_class = self.__param_creator.getType()
            name = self.__param_creator.getName()
            if type_class and name:
                self.__bloc.addExtraParam(type_class, name=name)
                self.__refresh()

    def __deleteParam(self, param):
        self.__bloc.removeParam(param)
        self.__refresh()

    def __update_all_params(self):
        for p in self.__params:
            p.refresh()

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
