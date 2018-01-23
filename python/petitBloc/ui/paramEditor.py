from Qt import QtWidgets
from Qt import QtCore
from . import const
from .. import util
import re


class Label(QtWidgets.QLabel):
    AddToBox = QtCore.Signal()
    RemoveFromBox = QtCore.Signal()
    RemoveProxy = QtCore.Signal()

    def __init__(self, text="", allowProxy=False, hasProxy=False, parent=None, isProxy=False):
        super(Label, self).__init__(text, parent=parent)
        self.__is_proxy = isProxy
        self.__show_menu = allowProxy
        self.__has_proxy = False
        self.setProxyStatus(hasProxy)

    def setProxyStatus(self, v):
        self.__has_proxy = v
        font = self.font()
        font.setItalic(self.__has_proxy)
        font.setBold(self.__has_proxy)
        self.setFont(font)

    def mousePressEvent(self, evnt):
        if self.__show_menu and (evnt.button() == QtCore.Qt.RightButton):
            menu = QtWidgets.QMenu(self)

            if self.__is_proxy:
                action = QtWidgets.QAction("Remove Proxy", menu)
                action.triggered.connect(self.__removeProxy)

            elif not self.__has_proxy:
                action = QtWidgets.QAction("Add to box", menu)
                action.triggered.connect(self.__addToBox)

            else:
                action = QtWidgets.QAction("Remove from box", menu)
                action.triggered.connect(self.__removeFromBox)

            menu.addAction(action)

            pos = self.mapToGlobal(evnt.pos())
            menu.popup(QtCore.QPoint(pos.x() - 10, pos.y() - 10))

    def __addToBox(self):
        self.AddToBox.emit()

    def __removeFromBox(self):
        self.RemoveFromBox.emit()

    def __removeProxy(self):
        self.RemoveProxy.emit()


class ParamLayout(QtWidgets.QHBoxLayout):
    RegexInt = re.compile("[^0-9-]")
    RegexFloat = re.compile("[^0-9-.]")
    AddProxyParam = QtCore.Signal(object)
    RemoveProxyParam = QtCore.Signal(object)

    def __init__(self, param, allowProxy=False, hasProxy=False, isProxy=False):
        super(ParamLayout, self).__init__()
        self.__label = None
        self.__param = param
        self.__val_edit = None
        self.__allow_proxy = allowProxy
        self.__has_proxy = hasProxy
        self.__is_proxy = isProxy
        self.__initialize()

    def setProxyStatus(self, v):
        self.__has_proxy = v
        self.__label.setProxyStatus(v)

    def __addToBox(self):
        self.AddProxyParam.emit(self.__param)

    def __removeFromBox(self):
        self.RemoveProxyParam.emit(self.__param)

    def __removeProxy(self):
        self.RemoveProxyParam.emit(self.__param)

    def __initialize(self):
        self.setAlignment(QtCore.Qt.AlignLeft)
        self.__label = Label(self.__paramLabel(self.__param.name()), allowProxy=self.__allow_proxy, hasProxy=self.__has_proxy, isProxy=self.__is_proxy)
        self.__label.setMinimumWidth(const.ParamLabelMinimumWidth)
        self.__label.setMaximumWidth(const.ParamLabelMaximumWidth)
        self.addWidget(self.__label)
        self.__label.AddToBox.connect(self.__addToBox)
        self.__label.RemoveFromBox.connect(self.__removeFromBox)
        self.__label.RemoveProxy.connect(self.__removeProxy)

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
    BlockRenamed = QtCore.Signal(object, str)

    def __init__(self, parent=None):
        super(ParamEditor, self).__init__()
        self.__bloc = None
        self.__param_layout = None
        self.__block_type_label = None
        self.__block_name = None
        self.__allow_proxy = False
        self.__params = {}
        self.__initialize()
        self.__refresh()

    def allowProxy(self, value):
        self.__allow_proxy = value

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

    def addProxyParam(self, param):
        box_bloc = self.__bloc.parent()
        if box_bloc is not None and box_bloc.hasNetwork():
            if box_bloc.addProxyParam(param) is not None:
                self.__params[param].setProxyStatus(True)

    def removeProxyParam(self, param):
        if self.__bloc.hasNetwork():
            if self.__bloc.removeProxyParam(param):
                self.__clearLayout(self.__params[param])

        else:
            box_bloc = self.__bloc.parent()
            if box_bloc is not None and box_bloc.hasNetwork():
                if box_bloc.removeProxyParamFromParam(param):
                    self.__params[param].setProxyStatus(False)

    def __build_params(self):
        if self.__bloc is None:
            return

        if self.__bloc.hasNetwork():
            for p in self.__bloc.proxyParams():
                lay = ParamLayout(p, allowProxy=True, isProxy=True)
                self.__params[p] = lay
                self.__param_layout.addLayout(lay)
                lay.RemoveProxyParam.connect(self.removeProxyParam)

        else:
            box_bloc = self.__bloc.parent()

            check_func = None
            if box_bloc is not None and box_bloc.hasNetwork():
                check_func = box_bloc.hasProxyParam
            else:
                check_func = lambda x: False

            for p in self.__bloc.params():
                lay = ParamLayout(p, allowProxy=self.__allow_proxy, hasProxy=check_func(p))
                lay.AddProxyParam.connect(self.addProxyParam)
                lay.RemoveProxyParam.connect(self.removeProxyParam)
                self.__params[p] = lay
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
