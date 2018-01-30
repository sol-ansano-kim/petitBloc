from Qt import QtWidgets
from Qt import QtCore
from Qt import QtGui
from . import const
from .. import util
import re
ReEqual = re.compile("^\s*[=]\s*")


class ParamLine(QtWidgets.QLineEdit):
    Value = 0
    Expression = 1
    ExpressionError = 2

    Changed = QtCore.Signal()

    def __init__(self, param, parent=None, isInt=False, isFloat=False):
        super(ParamLine, self).__init__(parent=parent)
        self.__normal_color = QtCore.Qt.black
        self.__expression_color = QtGui.QColor(10, 70, 70)
        self.__expression_error_color = QtGui.QColor(100, 10, 40)
        self.__current_state = ParamLine.Value
        self.__param = param

        if isInt:
            self.textEdited.connect(self.__intOnly)
            self.setMaximumWidth(const.ParamEditorMaximumWidth)
            self.setAlignment(QtCore.Qt.AlignRight)
            self.editingFinished.connect(self.__intFinished)
        elif isFloat:
            self.textEdited.connect(self.__floatOnly)
            self.setMaximumWidth(const.ParamEditorMaximumWidth)
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
        p = self.palette()

        if self.__current_state == ParamLine.Value:
            p.setColor(QtGui.QPalette.Base, self.__normal_color)
        elif self.__current_state == ParamLine.Expression:
            p.setColor(QtGui.QPalette.Base, self.__expression_color)
        elif self.__current_state == ParamLine.ExpressionError:
            p.setColor(QtGui.QPalette.Base, self.__expression_error_color)

        self.setPalette(p)

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


class ParamLayout(QtWidgets.QHBoxLayout):
    RegexInt = re.compile("[^0-9-]")
    RegexFloat = re.compile("[^0-9-.]")
    ParameterEdited = QtCore.Signal()

    def __init__(self, param):
        super(ParamLayout, self).__init__()
        self.__label = None
        self.__param = param
        self.__val_edit = None
        self.__need_to_refresh = False
        self.__initialize()

    def refresh(self):
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
        elif tc == int:
            self.__val_edit = ParamLine(self.__param, isInt=True)
            self.__val_edit.Changed.connect(self.__editedEmit)
        elif tc == float:
            self.__val_edit = ParamLine(self.__param, isFloat=True)
            self.__val_edit.Changed.connect(self.__editedEmit)
        elif tc == str:
            self.__val_edit = ParamLine(self.__param)
            self.__val_edit.Changed.connect(self.__editedEmit)

        self.addWidget(self.__val_edit)
        self.setSpacing(10)

        if tc != str:
            self.addStretch(100)

    def __boolChanged(self, state):
        self.__param.set(state == QtCore.Qt.Checked)
        self.__editedEmit()

    def __editedEmit(self):
        self.ParameterEdited.emit()


class ParamEditor(QtWidgets.QWidget):
    BlockRenamed = QtCore.Signal(object, str)

    def __init__(self, parent=None):
        super(ParamEditor, self).__init__()
        self.__bloc = None
        self.__param_layout = None
        self.__block_type_label = None
        self.__block_name = None
        self.__params = {}
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
        self.__params = {}

        self.__clearLayout(self.__param_layout)
        if self.__bloc is None:
            self.__block_type_label.setText("")
            self.__block_name.setText("")
            self.__block_type_label.hide()
            self.__block_name.hide()
        else:
            self.__block_type_label.show()
            self.__block_name.show()
            self.__block_name.setText(self.__bloc.name())
            self.__block_type_label.setText(self.__bloc.__class__.__name__)

        self.__build_params()

    def __build_params(self):
        if self.__bloc is None:
            return

        box_bloc = self.__bloc.parent()

        for p in self.__bloc.params():
            lay = ParamLayout(p)
            lay.ParameterEdited.connect(self.__update_all_params)
            self.__params[p] = lay
            self.__param_layout.addLayout(lay)

    def __update_all_params(self):
        for p in self.__params.values():
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
