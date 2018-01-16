from Qt import QtWidgets
from Qt import QtCore


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
        self.__block_name = QtWidgets.QLineEdit()
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
            print p

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
