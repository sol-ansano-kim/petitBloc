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


class ParamStatus():
    Value = 0
    Expression = 1
    ExpressionError = 2

    NormalColor = "#1D1D1D"
    ExpressionColor = "#0A4646"
    ExpressionErrorColor = "#640A28"


class CheckBox(QtWidgets.QCheckBox):
    def __init__(self, checkable, parent=None):
        super(CheckBox, self).__init__(parent=parent)
        self.__checkable = checkable

    def nextCheckState(self):
        if self.__checkable:
            self.setChecked(not self.isChecked())
        else:
            self.setChecked(self.isChecked())

    def setCheckable(self, v):
        self.__checkable = v


class ParamCheck(QtWidgets.QWidget):
    Changed = QtCore.Signal()

    def __init__(self, param, parent=None):
        super(ParamCheck, self).__init__(parent=parent)
        self.__normal_style = "QCheckBox::indicator{ border: 1px solid #1D1D1D; }"
        self.__exp_style = "QCheckBox::indicator{ margin 2px; border: 3px solid %s; }"
        self.__current_state = ParamStatus.Value
        self.__param = param

        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)
        self.__check_box = CheckBox(True, self)
        self.__check_box.toggled.connect(self.__toggled)
        self.__exp_line = QtWidgets.QLineEdit(self)
        self.__exp_line.hide()
        layout.addWidget(self.__check_box)
        layout.addWidget(self.__exp_line)

        self.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.__check_box.blockSignals(True)
        self.__check_box.setChecked(self.__param.get())
        self.__check_box.blockSignals(False)
        self.__exp_line.editingFinished.connect(self.__expFinished)

        self.refresh()

    def contextMenuEvent(self, evnt):
        menu = QtWidgets.QMenu(self)
        set_action = menu.addAction("Set Expression")
        delete_action = menu.addAction("Delete Expression")
        menu.popup(self.mapToGlobal(evnt.pos()))
        set_action.triggered.connect(self.__startSetExpression)
        delete_action.triggered.connect(self.__deleteExpression)

    def __toggled(self, v):
        self.__param.set(v)
        self.Changed.emit()

    def __startSetExpression(self):
        self.__check_box.hide()
        self.__exp_line.show()
        if self.__param.hasExpression():
            self.__exp_line.setText(self.__param.getExpression())
        else:
            self.__exp_line.setText("= ")
        self.__exp_line.setFocus(QtCore.Qt.OtherFocusReason)

    def __deleteExpression(self):
        self.__check_box.show()
        self.__exp_line.hide()
        self.__param.setExpression(None)
        self.refresh()

    def refresh(self):
        if not self.__param.hasExpression():
            self.__current_state = ParamStatus.Value
            self.__check_box.setCheckable(True)
        elif self.__param.validExpression():
            self.__check_box.setCheckable(False)
            self.__current_state = ParamStatus.Expression
        else:
            self.__check_box.setCheckable(False)
            self.__current_state = ParamStatus.ExpressionError

        self.__setBackgroundColor()

    def __setBackgroundColor(self):
        if self.__current_state == ParamStatus.Value:
            s = self.__normal_style
        elif self.__current_state == ParamStatus.Expression:
            s = self.__exp_style % ParamStatus.ExpressionColor
        elif self.__current_state == ParamStatus.ExpressionError:
            s = self.__exp_style % ParamStatus.ExpressionErrorColor

        self.setStyleSheet(s)

    def __expFinished(self):
        txt = self.__exp_line.text()
        if txt:
            self.__param.setExpression(str(txt))
        else:
            self.__param.setExpression(None)

        self.Changed.emit()
        self.__check_box.setChecked(self.__param.get())
        self.__check_box.show()
        self.__exp_line.hide()
        self.refresh()


class ParamLine(QtWidgets.QLineEdit):
    Changed = QtCore.Signal()

    def __init__(self, param, parent=None, isInt=False, isFloat=False):
        super(ParamLine, self).__init__(parent=parent)
        self.__style = "QLineEdit{ background-color: %s; border: 1px solid #1D1D1D; }"
        self.__current_state = ParamStatus.Value
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

        self.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.blockSignals(True)
        self.setText(str(self.__param.get()))
        self.blockSignals(False)

        self.refresh()

    def contextMenuEvent(self, evnt):
        menu = QtWidgets.QMenu(self)
        set_action = menu.addAction("Set Expression")
        delete_action = menu.addAction("Delete Expression")
        menu.popup(self.mapToGlobal(evnt.pos()))
        set_action.triggered.connect(self.__startSetExpression)
        delete_action.triggered.connect(self.__deleteExpression)

    def __startSetExpression(self):
        if self.__param.hasExpression():
            self.setText(self.__param.getExpression())
        else:
            self.setText("= ")
        self.setEditFocus(True)

    def __deleteExpression(self):
        self.__param.setExpression(None)
        self.refresh()

    def refresh(self):
        if not self.__param.hasExpression():
            self.__current_state = ParamStatus.Value
        elif self.__param.validExpression():
            self.__current_state = ParamStatus.Expression
        else:
            self.__current_state = ParamStatus.ExpressionError

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
        if self.__current_state == ParamStatus.Value:
            s = self.__style % ParamStatus.NormalColor
        elif self.__current_state == ParamStatus.Expression:
            s = self.__style % ParamStatus.ExpressionColor
        elif self.__current_state == ParamStatus.ExpressionError:
            s = self.__style % ParamStatus.ExpressionErrorColor

        self.setStyleSheet(s)

    def __intOnly(self, txt):
        if not ReEqual.search(txt):
            self.setText(Parameter.RegexInt.sub("", txt))

    def __floatOnly(self, txt):
        if not ReEqual.search(txt):
            self.setText(Parameter.RegexFloat.sub("", txt))

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


class ColorPicker(QtCore.QObject):
    Changed = QtCore.Signal()

    def __init__(self, r, g, b):
        super(ColorPicker, self).__init__()
        self.__r = r
        self.__g = g
        self.__b = b
        self.__label = None
        self.__button = None
        self.__style = "QPushButton{ background-color: rgb(%s, %s, %s); border: 1px solid #1D1D1D; }"
        self.initialize()
        self.refresh()

    def widgets(self):
        return [self.__label, self.__button]

    def initialize(self):
        self.__label = QtWidgets.QLabel("Color")
        self.__label.setMinimumWidth(const.ParamLabelMinimumWidth)
        self.__label.setMaximumWidth(const.ParamLabelMaximumWidth)
        self.__button = QtWidgets.QPushButton()
        self.__button.setFixedSize(18, 18)

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


class Parameter(QtCore.QObject):
    RegexInt = re.compile("[^0-9-]")
    RegexFloat = re.compile("[^0-9-.]")
    ParameterEdited = QtCore.Signal()
    DeleteRequest = QtCore.Signal(object)

    def __init__(self, param, deletable=False):
        super(Parameter, self).__init__()
        self.__label = None
        self.__param = param
        self.__val_edit = None
        self.__delete_button = None
        self.__need_to_refresh = True
        self.__deletable = deletable
        self.__initialize()

    def widgets(self):
        widgets = [self.__label, self.__val_edit]
        if self.__delete_button:
            widgets.append(self.__delete_button)

        return widgets

    def refresh(self):
        if self.__need_to_refresh:
            self.__val_edit.refresh()

    def __initialize(self):
        self.__label = QtWidgets.QLabel(self.__param.name())

        tc = self.__param.typeClass()
        if tc == bool:
            self.__val_edit = ParamCheck(self.__param)
            self.__val_edit.Changed.connect(self.__editedEmit)
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

        if self.__deletable:
            self.__delete_button = QtWidgets.QPushButton()
            self.__delete_button.setObjectName("RemoveButton")
            self.__delete_button.setFixedSize(14, 14)
            self.__delete_button.setFocusPolicy(QtCore.Qt.NoFocus)
            self.__delete_button.clicked.connect(self.__deleteParam)

    def __deleteParam(self):
        self.DeleteRequest.emit(self.__param)

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

    def forceRefresh(self):
        self.__refresh()

    def __initialize(self):
        # scroll area
        main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(main_layout)

        contents_widget = QtWidgets.QWidget()
        contents_layout = QtWidgets.QVBoxLayout()
        contents_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        contents_widget.setLayout(contents_layout)

        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(contents_widget)
        main_layout.addWidget(scroll_area)

        # parameters
        self.__param_layout = QtWidgets.QGridLayout()
        self.__param_layout.setSpacing(10)
        self.__param_layout.setVerticalSpacing(5)
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

        contents_layout.addWidget(self.__block_type_label)
        contents_layout.addLayout(name_layout)
        contents_layout.addLayout(self.__param_layout)
        contents_layout.addLayout(add_layout)
        self.__add_param_button.hide()

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
        r = 0
        if self.__bloc is None:
            return

        if self.__bloc.isBlank():
            pm = ColorPicker(self.__bloc.param("r"), self.__bloc.param("g"), self.__bloc.param("b"))
            pm.Changed.connect(partial(self.NodeRefreshRequest.emit, self.__bloc))
            self.__params.append(pm)
            for c, pw in enumerate(pm.widgets()):
                self.__param_layout.addWidget(pw, r, c)
            r += 1
            return

        to_disable = set()
        for ip in self.__bloc.inputs():
            if ip.hasLinkedParam() and ip.isConnected():
                to_disable.add(ip.linkedParam().name())

        for p in self.__bloc.params(includeExtraParam=False):
            pm = Parameter(p)
            pm.ParameterEdited.connect(self.__update_all_params)
            pm.DeleteRequest.connect(self.__deleteParam)
            self.__params.append(pm)

            enable = p.name() not in to_disable

            for c, pw in enumerate(pm.widgets()):
                pw.setEnabled(enable)
                self.__param_layout.addWidget(pw, r, c)
            r += 1

        for p in self.__bloc.extraParams():
            pm = Parameter(p, deletable=True)
            pm.ParameterEdited.connect(self.__update_all_params)
            pm.DeleteRequest.connect(self.__deleteParam)
            self.__params.append(pm)
            enable = p.name() not in to_disable

            for c, pw in enumerate(pm.widgets()):
                pw.setEnabled(enable)
                self.__param_layout.addWidget(pw, r, c)
            r += 1

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
