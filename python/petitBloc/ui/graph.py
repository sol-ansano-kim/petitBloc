import os
import re
from Nodz import nodz_main
from Nodz import nodz_utils
from Qt import QtGui
from Qt import QtCore
from Qt import QtWidgets
from . import model
from . import blockCreator
from . import uiUtil
from .. import anytype
from .. import dastype
import copy
from functools import partial


ReFirstSlash = re.compile("^/+")


def getConfigFile():
    return os.path.abspath(os.path.join(__file__, "../nodzConfig.json"))


class Graph(nodz_main.Nodz):
    KeyPressed = QtCore.Signal(int)
    ShowGraphRequest = QtCore.Signal(object)
    BlockDeleted = QtCore.Signal(object)
    BoxCreated = QtCore.Signal(object)
    BoxDeleted = QtCore.Signal(object)
    CurrentNodeChanged = QtCore.Signal(object)
    RefreshParamRequest = QtCore.Signal()

    def __init__(self, name="", boxObject=None, parent=None):
        super(Graph, self).__init__(parent, configPath=getConfigFile())
        self.__model = model.BoxModel(name=name, boxObject=boxObject)
        self.__updateConfig()
        self.__current_block = None
        # TODO : SceneContext
        self.__creator = blockCreator.BlockCreator(self, self.__model.blockClassNames(), excludeList=([] if isinstance(self, Graph) else ["SceneContext"]))
        self.__creator.BlockCreatorEnd.connect(self.addBlock)
        self.__context_node = None
        self.signal_NodeDeleted.connect(self.__nodeDeleted)
        self.signal_NodeSelected.connect(self.__nodeSelected)
        self.installEventFilter(self)
        self.initialize()
        self.gridVisToggle = False

        self.__zoom_factor = self.config["zoom_factor"]

    def _focus(self):
        if self.scene().selectedItems():
            itemsArea = self._getSelectionBoundingbox()

        else:
            itemsArea = self.scene().itemsBoundingRect()

        offset_x = 0
        offset_y = 0

        if itemsArea.x() < 0:
            offset_x = -itemsArea.x() + 40
        if itemsArea.y() < 0:
            offset_y = -itemsArea.y() + 40

        if offset_x > 0 or offset_y > 0:
            for itm in self.scene().items():
                if isinstance(itm, nodz_main.NodeItem):
                    itm.moveBy(offset_x, offset_y)

            if offset_x > 0:
                itemsArea.setX(0)
            if offset_y > 0:
                itemsArea.setY(0)

            self.scene().updateScene()

        itemsArea.setX(itemsArea.x() - 40)
        itemsArea.setY(itemsArea.y() - 40)
        itemsArea.setWidth(itemsArea.width() + 40)
        itemsArea.setHeight(itemsArea.height() + 40)
        self.fitInView(itemsArea, QtCore.Qt.KeepAspectRatio)

    def isTop(self):
        return True

    def proxyPaths(self):
        return []

    def cleanUpProxies(self):
        pass

    def __updateConfig(self):
        for b in self.__model.blockClassNames() + ["ProxyBlock"]:
            base = copy.deepcopy(self.config.get(b, self.config.get("Block")))
            for k, v in self.__model.config(b).iteritems():
                base[k] = v
            self.config[b] = base

    def wheelEvent(self, event):
        self.currentState = 'ZOOM_VIEW'
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorViewCenter)

        delta = 0
        if hasattr(event, "source"):
            if event.source() == QtCore.Qt.MouseEventSynthesizedBySystem and hasattr(event, "pixelDelta"):
                delta = event.pixelDelta().y()

            elif hasattr(event, "angleDelta"):
                delta = event.angleDelta().y()

        elif hasattr(event, "delta"):
            delta = event.delta()

        if delta > 0:
            self.scale(self.__zoom_factor, self.__zoom_factor)

        elif delta < 0:
            factor = 1 / self.__zoom_factor
            self.scale(factor, factor)

        self.currentState = 'DEFAULT'

    def boxModel(self):
        return self.__model

    def box(self):
        return self.__model.box()

    def hasContext(self):
        return self.__context_node is not None

    def addContextBlock(self, position=None):
        if self.__context_node is None:

            cntx_bloc = self.__model.createContext()
            if cntx_bloc is None:
                raise Exception, "Error : Failed to create a context block"

            self.__context_node = ContextItem(cntx_bloc, False, self.config)

            self.scene().nodes[cntx_bloc.name()] = self.__context_node
            self.scene().addItem(self.__context_node)
            if not position:
                position = self.mapToScene(self.viewport().rect().center())

            self.__context_node.setPos(position - self.__context_node.nodeCenter)

            return self.__context_node

    def mouseDoubleClickEvent(self, evnt):
        itm = self.itemAt(evnt.pos())

        if itm is not None and isinstance(itm, BlocItem) and itm.block().hasNetwork():
            self.ShowGraphRequest.emit(itm.block())

    def mousePressEvent(self, evnt):
        if evnt.button() == QtCore.Qt.RightButton and evnt.modifiers() == QtCore.Qt.NoModifier:
            self.__showMenu(evnt.pos())
            return

        if evnt.button() == QtCore.Qt.LeftButton and evnt.modifiers() == QtCore.Qt.AltModifier:
            self.currentState = 'DRAG_VIEW'
            self.prevPos = evnt.pos()
            self.setCursor(QtCore.Qt.ClosedHandCursor)
            self.setInteractive(False)
            return

        elif evnt.button() == QtCore.Qt.LeftButton and evnt.modifiers() == QtCore.Qt.ShiftModifier:
            scn_pos = self.mapToScene(evnt.pos())
            for item in self.scene().items(scn_pos):
                if isinstance(item, BackdropItem):
                    if item.isOnEvent():
                        item.setSelected(item.isSelected() == False)
                        return

        if evnt.button() == QtCore.Qt.LeftButton and evnt.modifiers() == QtCore.Qt.NoModifier:
            blocs = []
            scn_pos = self.mapToScene(evnt.pos())
            for item in self.scene().items(scn_pos):
                if isinstance(item, BackdropItem):
                    if item.isOnEvent():
                        super(Graph, self).mousePressEvent(evnt)
                        return
                else:
                    blocs.append(item)

            if blocs:
                self.currentState = 'DRAG_ITEM'
                self.setInteractive(True)
                QtWidgets.QGraphicsView.mousePressEvent(self, evnt)
                return
            else:
                self.currentState = 'SELECTION'
                self._initRubberband(evnt.pos())
                self.setInteractive(False)
                return

        super(Graph, self).mousePressEvent(evnt)

    def mouseReleaseEvent(self, evnt):
        if self.currentState == "DRAG_ITEM":
            items = self.scene().selectedItems()
            super(Graph, self).mouseReleaseEvent(evnt)
            for it in items:
                it.setSelected(True)

        if self.currentState in ['SELECTION', 'ADD_SELECTION', 'SUBTRACT_SELECTION', 'TOGGLE_SELECTION']:
            self.rubberband.setGeometry(QtCore.QRect(self.origin, evnt.pos()).normalized())
            pp = self._releaseRubberband()
            self.setInteractive(True)

            block_items = {}
            backdrop_items = {}
            target_items = []

            path_rect = pp.boundingRect()

            for item in self.scene().items(pp):
                if isinstance(item, BackdropItem):
                    sr = item.mapRectToScene(item.boundingRect().toRect())
                    if path_rect.contains(sr):
                        backdrop_items[item] = sr
                        target_items.append(item)
                else:
                    br = item.boundingRect()
                    block_items[item] = item.mapRectToScene(item.boundingRect().toRect())

            ignore = []
            for item, item_bound in block_items.items():
                included = False
                for bd, br in backdrop_items.items():
                    if br.contains(item_bound):
                        included = True
                        break
                if not included:
                    target_items.append(item)

            if self.currentState == "SELECTION":
                for item in self.scene().items():
                    item.setSelected(False)

                for item in target_items:
                    item.setSelected(True)

            elif self.currentState == "ADD_SELECTION":
                for item in target_items:
                    item.setSelected(True)

            elif self.currentState == "SUBTRACT_SELECTION":
                for item in target_items:
                    item.setSelected(False)

            else:
                for item in target_items:
                    item.setSelected(item.isSelected() == False)

            self.currentState = 'DEFAULT'

        else:
            super(Graph, self).mouseReleaseEvent(evnt)

    def findNodeFromName(self, name):
        for nodename, node in self.scene().nodes.iteritems():
            if name == nodename:
                return node

        return None

    def findNode(self, bloc):
        for node in self.scene().nodes.values():
            if node.block() == bloc:
                return node

        return None

    def renameNode(self, bloc, new_name):
        for node in self.scene().nodes.values():
            if node.block() == bloc:
                self.editNode(node, new_name)
                return True

        return False

    def eventFilter(self, obj, evnt):
        if obj != self:
            return False

        if evnt.type() == QtCore.QEvent.KeyPress:
            key = evnt.key()
            self.KeyPressed.emit(evnt.key())
            if key == QtCore.Qt.Key_Tab:
                self.__creator.show(self.mapFromGlobal(QtGui.QCursor.pos()))

                return True

            if key == QtCore.Qt.Key_Up:
                parent = self.box().parent()
                if parent is not None:
                    self.ShowGraphRequest.emit(parent)

                return True

            if key == QtCore.Qt.Key_Down or key == QtCore.Qt.Key_Return:
                for b in self.scene().selectedItems():
                    if isinstance(b, BlocItem) and b.block().hasNetwork():
                        self.ShowGraphRequest.emit(b.block())
                        break

                return True

        return False

    def currentBlock(self):
        return self.__current_block

    def __showMenu(self, pos):
        menu = QtWidgets.QMenu(self)
        block_menu = menu.addMenu("Create Block")

        categories = {}

        def getCategory(name):
            name = ReFirstSlash.sub("", name)
            cate = categories.get(name)
            if cate is not None:
                return cate

            pname = os.path.dirname(name)

            if pname:
                parent = getCategory(pname)
            else:
                parent = block_menu

            cate = parent.addMenu(os.path.basename(name))
            categories[name] = cate

            return cate

        block_tree = self.__model.blockTree()
        for c in sorted(block_tree.keys()):
            cate = getCategory(c)
            blocks = block_tree.get(c, [])
            for b in sorted(blocks):
                if b == "SceneContext" and not self.isTop():
                    continue

                action = cate.addAction(b)
                action.triggered.connect(partial(self.addBlock, b, position=self.mapToScene(pos)))
                if b == "SceneContext" and self.hasContext():
                    action.setEnabled(False)

        menu.popup(self.viewport().mapToGlobal(pos))

    def __nodeSelected(self, selectedNodes):
        if not selectedNodes:
            self.__current_block = None
            self.CurrentNodeChanged.emit(None)
            return

        node = selectedNodes[0]
        if self.__context_node and self.__context_node.name == node:
            self.__current_block = self.__context_node.block()
            self.CurrentNodeChanged.emit(self.__current_block)
            return

        self.__current_block = self.__model.block(node)
        self.CurrentNodeChanged.emit(self.__current_block)

    def _deleteSelectedNodes(self):
        selected_nodes = list()
        for node in self.scene().selectedItems():
            if isinstance(node, ProxyItem):
                continue

            selected_nodes.append(node.name)
            node._remove()

        self.signal_NodeDeleted.emit(selected_nodes)

    def __nodeDeleted(self, deletedNodes):
        for n in deletedNodes:
            if self.__context_node and self.__context_node.name == n:
                self.__model.deleteContext()
                self.__context_node = None
                continue

            b = self.__model.block(n)
            self.BlockDeleted.emit(b)
            if b.hasNetwork():
                self.BoxDeleted.emit(b)
            self.__model.deleteNode(n)

    def portConnected(self, srcPort, dstPort):
        self.__model.connect(srcPort, dstPort)

        if self.__current_block == srcPort.parent() or self.__current_block == dstPort.parent():
            self.RefreshParamRequest.emit()

    def portDisconnected(self, srcPort, dstPort):
        self.__model.disconnect(srcPort, dstPort)

        if self.__current_block == srcPort.parent() or self.__current_block == dstPort.parent():
            self.RefreshParamRequest.emit()

    def addBlock(self, blockType, blockName=None, position=None):
        if not blockType:
            return None

        # TODO : make this more smarter
        if blockType == "SceneContext":
            return self.addContextBlock(position=position)

        bloc = self.__model.addBlock(blockType, name=blockName)
        if bloc is None:
            return None

        if position is None:
            position = self.mapToScene(self.mapFromGlobal(QtGui.QCursor.pos()))

        node = self.createNode(bloc, position=position)

        if bloc.hasNetwork():
            self.BoxCreated.emit(bloc)

        for ip in bloc.inputs():
            self.createAttribute(node=node, port=ip, plug=False, socket=True, dataType=ip.typeClass())

        for op in bloc.outputs():
            self.createAttribute(node=node, port=op, plug=True, socket=False, dataType=op.typeClass())

        return node

    def createNode(self, bloc, preset='Block', position=None, alternate=True):
        if bloc.name() in self.scene().nodes.keys():
            print('A node with the same name already exists : {0}'.format(bloc.name()))
            print('Node creation aborted !')
            return

        # TODO : make this more smarter
        if bloc.isBlank():
            nodeItem = BackdropItem(bloc, self.config)
        else:
            nodeItem = BlocItem(bloc, alternate, self.config)

        # Store node in scene.
        self.scene().nodes[bloc.name()] = nodeItem

        if not position:
            # Get the center of the view.
            position = self.mapToScene(self.viewport().rect().center())

        # Set node position.
        self.scene().addItem(nodeItem)
        nodeItem.setPos(position - nodeItem.nodeCenter)

        # Emit signal.
        self.signal_NodeCreated.emit(bloc.name())

        return nodeItem

    def createAttribute(self, node, port, index=-1, preset='port_default', plug=True, socket=True, dataType=None, proxyNode=None):
        if not node in self.scene().nodes.values():
            print('Node object does not exist !')
            print('Attribute creation aborted !')
            return

        if port.name() in node.attrs:
            print('An attribute with the same name already exists : {0}'.format(port.name()))
            print('Attribute creation aborted !')
            return

        if isinstance(node, ProxyItem) or (node.block().hasNetwork()):
            if port.typeClass() == bool:
                preset = "box_bool_port"

            elif port.typeClass() == int:
                preset = "box_int_port"

            elif port.typeClass() == float:
                preset = "box_float_port"

            elif issubclass(port.typeClass(), basestring):
                preset = "box_str_port"

            elif issubclass(port.typeClass(), anytype.Any):
                preset = "box_any_port"

            elif issubclass(port.typeClass(), dastype.Das):
                preset = "box_das_port"

        else:
            if port.typeClass() == bool:
                preset = "bool_port"

            elif port.typeClass() == int:
                preset = "int_port"

            elif port.typeClass() == float:
                preset = "float_port"

            elif issubclass(port.typeClass(), basestring):
                preset = "str_port"

            elif issubclass(port.typeClass(), anytype.Any):
                preset = "any_port"

            elif issubclass(port.typeClass(), dastype.Das):
                preset = "das_port"

        node._createAttribute(port, index=index, preset=preset, plug=plug, socket=socket, dataType=dataType, proxyNode=proxyNode)

        # Emit signal.
        self.signal_AttrCreated.emit(node.name, index)

    def createConnection(self, sourceNode, sourceAttr, targetNode, targetAttr):
        plug = self.scene().nodes[sourceNode].plugs[sourceAttr]
        socket = self.scene().nodes[targetNode].sockets[targetAttr]

        connection = ChainItem(plug.center(), socket.center(), plug, socket)

        connection.plugNode = plug.parentItem().name
        connection.plugAttr = plug.attribute
        connection.socketNode = socket.parentItem().name
        connection.socketAttr = socket.attribute

        plug.connect(socket, connection)
        socket.connect(plug, connection)

        connection.updatePath()

        self.scene().addItem(connection)

        return connection

    def copy(self):
        include = map(lambda x : x.block().path(), self.scene().selectedItems())
        if not include:
            return {}

        exclude = self.proxyPaths()
        return self.__model.serialize(include=include, exclude=exclude)


class SubNet(Graph):
    ProxyPortAdded = QtCore.Signal(object, object, object)
    ProxyPortRemoved = QtCore.Signal(object, object, str)

    def __init__(self, name="", boxObject=None, parent=None):
        super(SubNet, self).__init__(name=name, boxObject=boxObject, parent=parent)
        self.__proxy_in = ProxyItem(self.boxModel().inProxyBlock(), ProxyItem.In, False, self.config)
        self.__proxy_out = ProxyItem(self.boxModel().outProxyBlock(), ProxyItem.Out, False, self.config)
        center = QtCore.QPointF(int(self.config["scene_width"] * 0.5), int(self.config["scene_height"] * 0.5))
        self.__proxy_in.setPos(center - self.__proxy_in.nodeCenter - QtCore.QPoint(0, self.__proxy_in.height) * 1.5)
        self.__proxy_out.setPos(center - self.__proxy_in.nodeCenter + QtCore.QPoint(0, self.__proxy_in.height) * 1.5)

        self.scene().nodes[self.__proxy_in.block().name()] = self.__proxy_in
        self.scene().nodes[self.__proxy_out.block().name()] = self.__proxy_out
        self.scene().addItem(self.__proxy_in)
        self.scene().addItem(self.__proxy_out)

        self.BlockDeleted.connect(self.cleanUpProxies)

    def isTop(self):
        return False

    def proxyPaths(self):
        return [self.__proxy_in.block().path(), self.__proxy_out.block().path()]

    def cleanUpProxies(self):
        inputs = self.boxModel().cleanUpInputProxies()
        for p in inputs:
            self.deleteAttribute(self.__proxy_in, self.__proxy_in.attrs.index(p.name()))
            self.ProxyPortRemoved.emit(self.boxModel().box(), self.__proxy_in, p.name())

        outputs = self.boxModel().cleanUpOutputProxies()
        for p in outputs:
            self.deleteAttribute(self.__proxy_out, self.__proxy_out.attrs.index(p.name()))
            self.ProxyPortRemoved.emit(self.boxModel().box(), self.__proxy_out, p.name())

        self.__proxy_in.scene().updateScene()
        self.__proxy_out.scene().updateScene()

    def addInputProxy(self, typeClass, name):
        prx = self.boxModel().addInputProxy(typeClass, name)
        proxy_node = self.inProxyNode()
        self.createAttribute(node=proxy_node, port=prx.outPort(), plug=True, socket=False, dataType=prx.typeClass(), proxyNode=proxy_node)
        self.ProxyPortAdded.emit(self.box(), proxy_node, prx.inPort())
        return prx

    def addOutputProxy(self, typeClass, name):
        prx = self.boxModel().addOutputProxy(typeClass, name)
        proxy_node = self.outProxyNode()
        self.createAttribute(node=proxy_node, port=prx.inPort(), plug=False, socket=True, dataType=prx.typeClass(), proxyNode=proxy_node)
        self.ProxyPortAdded.emit(self.box(), proxy_node, prx.outPort())
        return prx

    def removeInputProxy(self, port):
        self.boxModel().removeInputProxy(port)

    def removeOutputProxy(self, port):
        self.boxModel().removeOutputProxy(port)

    def inProxyNode(self):
        return self.__proxy_in

    def outProxyNode(self):
        return self.__proxy_out

    def inProxyConnected(self, proxyPort, port):
        self.boxModel().connectInProxy(proxyPort, port)

    def outProxyConnected(self, proxyPort, port):
        self.boxModel().connectOutProxy(proxyPort, port)

    def inProxyDisConnected(self, proxyPort, port):
        self.boxModel().disconnectInProxy(proxyPort, port)

    def outProxyDisConnected(self, proxyPort, port):
        self.boxModel().disconnectOutProxy(proxyPort, port)


class BlocItem(nodz_main.NodeItem):
    def __init__(self, bloc, alternate, config):
        super(BlocItem, self).__init__(bloc.name(), alternate, bloc.__class__.__name__, config)
        self.__block = bloc
        # TODO : set style from config
        self.__error_pen = QtGui.QPen(QtGui.QColor(242, 38, 94))
        self.__error_brush = QtGui.QBrush(QtGui.QColor(75, 0, 0, 125))
        self.__hl_pen = QtGui.QPen(QtGui.QColor(98, 215, 234))
        self.__hl_pen.setStyle(QtCore.Qt.SolidLine)
        self.__hl_pen.setWidth(self.border + 2)
        self.__emphasize = False

    def mouseMoveEvent(self, event):
        if self.scene().views()[0].gridVisToggle and (self.scene().views()[0].gridSnapToggle or self.scene().views()[0]._nodeSnap):
            gridSize = self.scene().gridSize

            currentPos = self.mapToScene(event.pos().x() - self.baseWidth / 2,
                                         event.pos().y() - self.height / 2)

            snap_x = (round(currentPos.x() / gridSize) * gridSize) - gridSize/4
            snap_y = (round(currentPos.y() / gridSize) * gridSize) - gridSize/4
            snap_pos = QtCore.QPointF(snap_x, snap_y)
            self.setPos(snap_pos)

            self.scene().updateScene()
        else:
            self.scene().updateScene()
            super(nodz_main.NodeItem, self).mouseMoveEvent(event)

    @property
    def pen(self):
        if self.__emphasize:
            return self.__hl_pen
        if self.isSelected():
            return self._penSel

        return self._pen

    def emphasize(self, value):
        self.__emphasize = value

    def block(self):
        return self.__block

    def _createAttribute(self, port, index, preset, plug, socket, dataType, proxyNode=None):
        if port in self.attrs:
            print('An attribute with the same name already exists on this node : {0}'.format(port))
            print('Attribute creation aborted !')
            return

        self.attrPreset = preset
        port_name = None

        if port.isProxy():
            port_name = port.parent().name()
        else:
            port_name = port.name()

        if plug:
            if proxyNode:
                plugInst = OutputProxyPortItem(parent=self,
                                               proxyNode=proxyNode,
                                               port=port,
                                               index=self.attrCount,
                                               preset=preset,
                                               dataType=dataType)

            else:
                plugInst = OutputPortItem(parent=self,
                                          port=port,
                                          index=self.attrCount,
                                          preset=preset,
                                          dataType=dataType)

            self.plugs[port_name] = plugInst

        if socket:
            if proxyNode:
                socketInst = InputProxyPortItem(parent=self,
                                                proxyNode=proxyNode,
                                                port=port,
                                                index=self.attrCount,
                                                preset=preset,
                                                dataType=dataType)
            else:
                socketInst = InputPortItem(parent=self,
                                           port=port,
                                           index=self.attrCount,
                                           preset=preset,
                                           dataType=dataType)

            self.sockets[port_name] = socketInst

        self.attrCount += 1

        if index == -1 or index > self.attrCount:
            self.attrs.append(port_name)
        else:
            self.attrs.insert(index, port_name)

        self.attrsData[port_name] = {'name': port_name,
                                     'port': port,
                                     'socket': socket,
                                     'plug': plug,
                                     'preset': preset,
                                     'dataType': dataType}

        self.update()

    def paint(self, painter, option, widget):
        """
        Paint the node and attributes.

        """
        # Node base.
        painter.setBrush(self._brush)
        painter.setPen(self.pen)

        painter.drawRoundedRect(0, 0,
                                self.baseWidth,
                                self.height,
                                self.radius,
                                self.radius)

        # Node label.
        painter.setPen(self._textPen)
        painter.setFont(self._nodeTextFont)

        metrics = QtGui.QFontMetrics(painter.font())
        text_width = metrics.boundingRect(self.name).width() + 14
        text_height = metrics.boundingRect(self.name).height() + 14
        margin = (text_width - self.baseWidth) * 0.5
        textRect = QtCore.QRect(-margin,
                                -text_height,
                                text_width,
                                text_height)

        painter.drawText(textRect,
                         QtCore.Qt.AlignCenter,
                         self.name)

        # Attributes.
        offset = 0
        for attr in self.attrs:
            nodzInst = self.scene().views()[0]
            config = nodzInst.config

            # Attribute rect.
            rect = QtCore.QRect(self.border / 2,
                                self.baseHeight - self.radius + offset,
                                self.baseWidth - self.border,
                                self.attrHeight)



            attrData = self.attrsData[attr]
            name = attr

            preset = attrData['preset']


            bloc_class_name = self.__block.__class__.__name__
            # Attribute base.

            brush_color = config[bloc_class_name].get("port_bg", config[preset]['bg'])
            self._attrBrush.setColor(uiUtil.ConvertDataToColor(brush_color))
            if self.alternate:
                self._attrBrushAlt.setColor(uiUtil.ConvertDataToColor(brush_color, True, config['alternate_value']))

            self._attrPen.setColor(uiUtil.ConvertDataToColor([0, 0, 0, 0]))
            painter.setPen(self._attrPen)
            painter.setBrush(self._attrBrush)

            if self.alternate:
                if (offset / self.attrHeight) % 2:
                    painter.setBrush(self._attrBrushAlt)

            painter.drawRect(rect)

            # Attribute label.
            text_color = config[bloc_class_name].get("port_text", config[preset]['text'])
            painter.setPen(uiUtil.ConvertDataToColor(text_color))
            painter.setFont(self._attrTextFont)

            # Search non-connectable attributes.
            if nodzInst.drawingConnection:
                if self == nodzInst.currentHoveredNode:
                    port = attrData['port']
                    if (nodzInst.sourceSlot.slotType == 'plug' and attrData['socket'] == False) or (nodzInst.sourceSlot.slotType == 'socket' and attrData['plug'] == False):
                        # Set non-connectable attributes color.
                        painter.setPen(uiUtil.ConvertDataToColor(config['non_connectable_color']))

            textRect = QtCore.QRect(rect.left() + self.radius,
                                     rect.top(),
                                     rect.width() - 2*self.radius,
                                     rect.height())
            painter.drawText(textRect, QtCore.Qt.AlignVCenter, name)

            offset += self.attrHeight

        if self.__block.isFailed():
            painter.setBrush(self.__error_brush)
            painter.drawRoundedRect(0, 0, self.baseWidth, self.height, self.radius, self.radius)
            self.__error_pen
            painter.setPen(self.__error_pen)
            font = QtGui.QFont(self._nodeTextFont)
            font.setPointSize(30)
            painter.setFont(font)
            textRect = QtCore.QRect(0, 0, self.baseWidth, self.height)
            painter.drawText(textRect, QtCore.Qt.AlignCenter, "ERROR")


class BackdropItem(BlocItem):
    BDEventNoEvent = 0
    BDEventResizeLeftBorder = 1
    BDEventResizeRightBorder = 2
    BDEventResizeTopBorder = 3
    BDEventResizeBottomBorder = 4
    BDEventResizeTopLeftCorner = 5
    BDEventResizeTopRightCorner = 6
    BDEventResizeBottomLeftCorner = 7
    BDEventResizeBottomRightCorner = 8
    BDEventMove = 9

    def __init__(self, bloc, config):
        self.__back = bloc
        self.__config = config
        self.__in_area = []
        self._attrBrush = QtGui.QBrush()
        self._attrBrushAlt = QtGui.QBrush()
        self._attrPen = QtGui.QPen()
        self.nodeCenter = QtCore.QPointF()
        self._brush = QtGui.QBrush()
        self._pen = QtGui.QPen()
        self._penSel = QtGui.QPen()
        self._textPen = QtGui.QPen()
        self.__text_bound = QtCore.QRect()

        super(BackdropItem, self).__init__(bloc, False, config)
        self.setZValue(-10)
        self.setZValue = lambda x: x
        self.__resize_mode = BackdropItem.BDEventNoEvent
        self.__pre_event_pos = QtCore.QPointF()

    def isResizing(self):
        return self.__resize_mode != BackdropItem.BDEventNoEvent

    def __leftBorderRect(self):
        return QtCore.QRectF(0, 0, self.border, self.height)

    def __rightBorderRect(self):
        return QtCore.QRectF(self.baseWidth - self.border, 0, self.border, self.height)

    def __topBorderRect(self):
        return QtCore.QRectF(0, 0, self.baseWidth, self.border)

    def __bottomBorderRect(self):
        return QtCore.QRectF(0, self.height - self.border, self.baseWidth, self.border)

    def __topLeftCornerRect(self):
        return QtCore.QRectF(0, 0, self.border, self.border)

    def __topRightCornerRect(self):
        return QtCore.QRectF(self.baseWidth - self.border, 0, self.border, self.border)

    def __bottomLeftCornerRect(self):
        return QtCore.QRectF(0, self.height - self.border, self.border, self.border)

    def __bottomRightCornerRect(self):
        return QtCore.QRectF(self.baseWidth - self.border, self.height - self.border, self.border, self.border)

    def __pointInRect(self, pos, rect):
        px = pos.x()
        py = pos.y()
        left = rect.x()
        top = rect.y()
        right = left + rect.width()
        bottom = top + rect.height()

        if px >= left and px <= right and py >= top and py <= bottom:
            return True

        return False

    def hoverMoveEvent(self, evnt):
        pos = self.mapToItem(self, evnt.pos().x(), evnt.pos().y())
        if self.__pointInRect(pos, self.__topLeftCornerRect()):
            self.__resize_mode = BackdropItem.BDEventResizeTopLeftCorner
            self.setCursor(QtCore.Qt.SizeFDiagCursor)
        elif self.__pointInRect(pos, self.__topRightCornerRect()):
            self.__resize_mode = BackdropItem.BDEventResizeTopRightCorner
            self.setCursor(QtCore.Qt.SizeBDiagCursor)
        elif self.__pointInRect(pos, self.__bottomLeftCornerRect()):
            self.__resize_mode = BackdropItem.BDEventResizeBottomLeftCorner
            self.setCursor(QtCore.Qt.SizeBDiagCursor)
        elif self.__pointInRect(pos, self.__bottomRightCornerRect()):
            self.__resize_mode = BackdropItem.BDEventResizeBottomRightCorner
            self.setCursor(QtCore.Qt.SizeFDiagCursor)
        elif self.__pointInRect(pos, self.__leftBorderRect()):
            self.__resize_mode = BackdropItem.BDEventResizeLeftBorder
            self.setCursor(QtCore.Qt.SizeHorCursor)
        elif self.__pointInRect(pos, self.__rightBorderRect()):
            self.__resize_mode = BackdropItem.BDEventResizeRightBorder
            self.setCursor(QtCore.Qt.SizeHorCursor)
        elif self.__pointInRect(pos, self.__topBorderRect()):
            self.__resize_mode = BackdropItem.BDEventResizeTopBorder
            self.setCursor(QtCore.Qt.SizeVerCursor)
        elif self.__pointInRect(pos, self.__bottomBorderRect()):
            self.__resize_mode = BackdropItem.BDEventResizeBottomBorder
            self.setCursor(QtCore.Qt.SizeVerCursor)
        elif self.__pointInRect(pos, self.__text_bound):
            self.__resize_mode = BackdropItem.BDEventMove
            self.setCursor(QtCore.Qt.PointingHandCursor)
        else:
            self.__resize_mode = BackdropItem.BDEventNoEvent
            self.setCursor(QtCore.Qt.ArrowCursor)

        super(BackdropItem, self).hoverMoveEvent(evnt)

    def hoverLeaveEvent(self, evnt):
        self.__resize_mode = BackdropItem.BDEventNoEvent
        self.setCursor(QtCore.Qt.ArrowCursor)
        super(BackdropItem, self).hoverLeaveEvent(evnt)

    @property
    def height(self):
        return self.__back.param("height").get()

    def resizeButtonRect(self):
        x = self.baseWidth - 20
        y = self.height - 20
        return QtCore.QRectF(x, y, 20, 20)

    def refresh(self):
        self._createStyle(self.__config)

    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemSelectedHasChanged:
            for item in self.scene().items(QtCore.QRectF(self.pos(), self.boundingRect().size()), QtCore.Qt.ContainsItemShape):
                item.setSelected(value)

        return super(BackdropItem, self).itemChange(change, value)

    def mousePressEvent(self, event):
        self.__pre_event_pos = event.pos()
        super(BackdropItem, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        pre_node_pos = self.pos()
        cur_event_pos = event.pos()

        delta = cur_event_pos - self.__pre_event_pos

        if self.__resize_mode is BackdropItem.BDEventMove or self.__resize_mode is BackdropItem.BDEventNoEvent:
            super(BackdropItem, self).mouseMoveEvent(event)
        else:
            w_pam = self.__back.param("width")
            h_pam = self.__back.param("height")

            if self.__resize_mode is BackdropItem.BDEventResizeTopLeftCorner:
                w_pam.set(w_pam.get() - delta.x())
                h_pam.set(h_pam.get() - delta.y())
                self.setPos(pre_node_pos + delta)

            elif self.__resize_mode is BackdropItem.BDEventResizeTopRightCorner:
                w_pam.set(w_pam.get() + delta.x())
                h_pam.set(h_pam.get() - delta.y())
                self.setPos(pre_node_pos.x(), (pre_node_pos + delta).y())
                self.__pre_event_pos = QtCore.QPointF(cur_event_pos.x(), self.__pre_event_pos.y())

            elif self.__resize_mode is BackdropItem.BDEventResizeBottomLeftCorner:
                w_pam.set(w_pam.get() - delta.x())
                h_pam.set(h_pam.get() + delta.y())
                self.setPos((pre_node_pos + delta).x(), pre_node_pos.y())
                self.__pre_event_pos = QtCore.QPointF(self.__pre_event_pos.x(), cur_event_pos.y())

            elif self.__resize_mode is BackdropItem.BDEventResizeBottomRightCorner:
                w_pam.set(w_pam.get() + delta.x())
                h_pam.set(h_pam.get() + delta.y())
                self.__pre_event_pos = cur_event_pos

            elif self.__resize_mode is BackdropItem.BDEventResizeLeftBorder:
                w_pam.set(w_pam.get() - delta.x())
                self.setPos((pre_node_pos + delta).x(), pre_node_pos.y())

            elif self.__resize_mode is BackdropItem.BDEventResizeRightBorder:
                w_pam.set(w_pam.get() + delta.x())
                self.__pre_event_pos = cur_event_pos

            elif self.__resize_mode is BackdropItem.BDEventResizeTopBorder:
                h_pam.set(h_pam.get() - delta.y())
                self.setPos(pre_node_pos.x(), (pre_node_pos + delta).y())

            elif self.__resize_mode is BackdropItem.BDEventResizeBottomBorder:
                h_pam.set(h_pam.get() + delta.y())
                self.__pre_event_pos = cur_event_pos

            if w_pam.get() < 50:
                w_pam.set(50)

            if h_pam.get() < 50:
                h_pam.set(50)

            self.refresh()
            self.update()

        self.scene().updateScene()

    def _createStyle(self, config):
        self.setAcceptHoverEvents(True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)

        self.baseWidth  = self.__back.param("width").get()
        self.border = 4
        self.radius = 5

        self.nodeCenter.setX(self.baseWidth * 0.5)
        self.nodeCenter.setY(self.height * 0.5)

        self.__r = self.__back.param("r").get()
        self.__g = self.__back.param("g").get()
        self.__b = self.__back.param("b").get()

        self._brush.setStyle(QtCore.Qt.SolidPattern)
        self._brush.setColor(QtGui.QColor(self.__r, self.__g, self.__b))

        self._pen.setStyle(QtCore.Qt.SolidLine)
        self._pen.setWidth(self.border)
        self._pen.setColor(QtGui.QColor(25, 25, 25))

        self._penSel.setStyle(QtCore.Qt.SolidLine)
        self._penSel.setWidth(self.border)
        self._penSel.setColor(QtGui.QColor(98, 215, 234))

        self._textPen.setStyle(QtCore.Qt.SolidLine)
        self._textPen.setColor(QtGui.QColor(255, 255, 255))

        self._nodeTextFont = QtGui.QFont(config['node_font'], config['node_font_size'] + 20, QtGui.QFont.Bold)
        self._attrTextFont = QtGui.QFont(config['attr_font'], config['attr_font_size'], QtGui.QFont.Normal)

        self._attrBrush.setStyle(QtCore.Qt.SolidPattern)
        self._attrBrushAlt.setStyle(QtCore.Qt.SolidPattern)
        self._attrPen.setStyle(QtCore.Qt.SolidLine)

    def isOnEvent(self):
        return self.__resize_mode != BackdropItem.BDEventNoEvent

    def paint(self, painter, option, widget):
        painter.setBrush(self._brush)
        painter.setPen(self.pen)
        painter.drawRoundedRect(0, 0, self.baseWidth, self.height, self.radius, self.radius)

        painter.setPen(self._textPen)
        painter.setFont(self._nodeTextFont)
        metrics = QtGui.QFontMetrics(painter.font())
        text_bound = metrics.boundingRect(self.name)
        # self.__text_bound = QtCore.QRect(0, 0, self.baseWidth, text_bound.height())
        text_width = text_bound.width() + 14
        text_height = text_bound.height() + 14
        margin = (text_width - self.baseWidth) * 0.5
        self.__text_bound = QtCore.QRect(-margin, 0, text_width, text_height)

        painter.drawText(self.__text_bound, QtCore.Qt.AlignCenter, self.name)


class ContextItem(BlocItem):
    def __init__(self, bloc, alternate, config):
        super(ContextItem, self).__init__(bloc, alternate, config)


class ProxyItem(BlocItem):
    In = 0
    Out = 1
    def __init__(self, bloc, direction, alternate, config):
        super(ProxyItem, self).__init__(bloc, alternate, config)
        self.__bloc = bloc
        self.__direction = direction

    def isInProxy(self):
        return self.__direction is ProxyItem.In

    def isOutProxy(self):
        return self.__direction is ProxyItem.Out

    def _remove(self):
        pass

    def _deleteAttribute(self, index):
        self.prepareGeometryChange()
        super(ProxyItem, self)._deleteAttribute(index)

    def paint(self, painter, option, widget):
        nodzInst = self.scene().views()[0]
        self.emphasize(False)

        if nodzInst.drawingConnection:
            if self == nodzInst.currentHoveredNode:
                if (self.isOutProxy() and nodzInst.sourceSlot.slotType == 'plug') or ((self.isInProxy() and nodzInst.sourceSlot.slotType == 'socket')):
                    self.emphasize(True)

        super(ProxyItem, self).paint(painter, option, widget)


class OutputPortItem(nodz_main.PlugItem):
    def __init__(self, parent, port, index, preset, dataType):
        name = port.name()
        if port.isProxy():
            name = port.parent().name()

        super(OutputPortItem, self).__init__(parent, name, index, preset, dataType)
        self._connectable_pen = QtGui.QPen()
        self._connectable_pen.setStyle(QtCore.Qt.SolidLine)
        self._connectable_pen.setWidth(2)
        self._connectable_pen.setColor(QtGui.QColor(255, 255, 255, 255))
        self.__port = port

    def port(self):
        return self.__port

    def paint(self, painter, option, widget):
        painter.setBrush(self.brush)
        painter.setPen(self.pen)

        nodzInst = self.scene().views()[0]
        config = nodzInst.config
        if nodzInst.drawingConnection:
            if self.parentItem() == nodzInst.currentHoveredNode:
                painter.setBrush(uiUtil.ConvertDataToColor(config['non_connectable_color']))
                if (self.slotType == nodzInst.sourceSlot.slotType or (self.slotType != nodzInst.sourceSlot.slotType and not nodzInst.sourceSlot.port().match(self.port()))):
                    painter.setBrush(uiUtil.ConvertDataToColor(config['non_connectable_color']))
                else:
                    painter.setPen(self._connectable_pen)
                    painter.setBrush(self.brush)

        rect =  self.boundingRect()

        if self.__port.isOptional():
            poly = QtGui.QPolygonF()
            poly.append(QtCore.QPointF(rect.x() + rect.width() * 0.5, rect.y() + 2))
            poly.append(QtCore.QPointF(rect.x() + rect.width(), rect.y() + rect.height()))
            poly.append(QtCore.QPointF(rect.x(), rect.y() + rect.height()))
            painter.drawPolygon(poly)
        else:
            painter.drawEllipse(rect)

    def connect(self, socket_item, connection):
        """
        Connect to the given socket_item.

        """
        # Populate connection.
        connection.socketItem = socket_item
        connection.plugNode = self.parentItem().name
        connection.plugAttr = self.attribute

        # Add socket to connected slots.
        if socket_item in self.connected_slots:
            self.connected_slots.remove(socket_item)
        self.connected_slots.append(socket_item)

        # Add connection.
        if connection not in self.connections:
            self.connections.append(connection)

        # Emit signal.
        nodzInst = self.scene().views()[0]

        nodzInst.portConnected(self.port(), socket_item.port())
        nodzInst.signal_PlugConnected.emit(connection.plugNode, connection.plugAttr, connection.socketNode, connection.socketAttr)

    def disconnect(self, connection):
        """
        Disconnect the given connection from this plug item.

        """
        # Emit signal.
        socket_item = connection.socketItem

        nodzInst = self.scene().views()[0]
        if socket_item is not None:
            nodzInst.portDisconnected(self.port(), socket_item.port())

        # Remove connected socket from plug
        if connection.socketItem in self.connected_slots:
            self.connected_slots.remove(connection.socketItem)

        # Remove connection
        self.connections.remove(connection)

    def mouseReleaseEvent(self, event):
        nodzInst = self.scene().views()[0]
        if event.button() == QtCore.Qt.LeftButton:
            nodzInst.drawingConnection = False
            nodzInst.currentDataType = None

            target = self.scene().itemAt(event.scenePos().toPoint(), QtGui.QTransform())

            if not isinstance(target, nodz_main.SlotItem) and not isinstance(target, ProxyItem):
                self.newConnection._remove()
                super(nodz_main.SlotItem, self).mouseReleaseEvent(event)

                return

            if isinstance(self, OutputProxyPortItem):
                if isinstance(target, ProxyItem) and self.proxyNode().block().parent() == target.block().parent():
                    self.newConnection._remove()
                    super(nodz_main.SlotItem, self).mouseReleaseEvent(event)

                    return

                if isinstance(target, InputProxyPortItem) and self.proxyNode().block().parent() == target.proxyNode().block().parent():
                    self.newConnection._remove()
                    super(nodz_main.SlotItem, self).mouseReleaseEvent(event)

                    return

            if isinstance(target, ProxyItem):
                if target.isInProxy():
                    self.newConnection._remove()
                    super(nodz_main.SlotItem, self).mouseReleaseEvent(event)

                    return
                else:
                    if target.block().hasConnection(self.__port):
                        self.newConnection._remove()
                        super(nodz_main.SlotItem, self).mouseReleaseEvent(event)

                        return
                    else:
                        new_name = self.port().name()
                        prnt = self.port().parent()
                        if prnt:
                            new_name = "{}_{}".format(prnt.name(), new_name)
                        prx = nodzInst.addOutputProxy(self.port().typeClass(), new_name)
                        proxy_node = nodzInst.outProxyNode()
                        target_port = proxy_node.sockets[prx.name()]
                        self.newConnection.target = target_port
                        self.newConnection.source = self
                        self.newConnection.target_point = target_port.center()
                        self.newConnection.source_point = self.center()

                        self.connect(target_port, self.newConnection)
                        target_port.connect(self, self.newConnection)

                        self.newConnection.updatePath()
            else:
                if target.accepts(self):
                    self.newConnection.target = target
                    self.newConnection.source = self
                    self.newConnection.target_point = target.center()
                    self.newConnection.source_point = self.center()

                    # Perform the ConnectionItem.
                    self.connect(target, self.newConnection)
                    target.connect(self, self.newConnection)

                    self.newConnection.updatePath()
                else:
                    self.newConnection._remove()
        else:
            super(nodz_main.SlotItem, self).mouseReleaseEvent(event)

        nodzInst.currentHoveredNode = None

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.newConnection = ChainItem(self.center(),
                                           self.mapToScene(event.pos()),
                                           self,
                                           None)

            self.connections.append(self.newConnection)
            self.scene().addItem(self.newConnection)

            nodzInst = self.scene().views()[0]
            nodzInst.drawingConnection = True
            nodzInst.sourceSlot = self
            nodzInst.currentDataType = self.dataType
        else:
            super(SlotItem, self).mousePressEvent(event)

    def accepts(self, socket_item):
        if isinstance(socket_item, nodz_main.SocketItem):
            if self.parentItem() != socket_item.parentItem():
                if socket_item.port().match(self.port()):
                    if socket_item in self.connected_slots:
                        return False
                    else:
                        return True
            else:
                return False
        else:
            return False


class InputPortItem(nodz_main.SocketItem):
    def __init__(self, parent, port, index, preset, dataType):
        name = port.name()
        if port.isProxy():
            name = port.parent().name()

        super(InputPortItem, self).__init__(parent, name, index, preset, dataType)
        self.__port = port
        self._connectable_pen = QtGui.QPen()
        self._connectable_pen.setStyle(QtCore.Qt.SolidLine)
        self._connectable_pen.setWidth(2)
        self._connectable_pen.setColor(QtGui.QColor(255, 255, 255, 255))

    def port(self):
        return self.__port

    def paint(self, painter, option, widget):
        painter.setBrush(self.brush)
        painter.setPen(self.pen)

        nodzInst = self.scene().views()[0]
        config = nodzInst.config
        if nodzInst.drawingConnection:
            if self.parentItem() == nodzInst.currentHoveredNode:
                painter.setBrush(uiUtil.ConvertDataToColor(config['non_connectable_color']))
                if (self.slotType == nodzInst.sourceSlot.slotType or (self.slotType != nodzInst.sourceSlot.slotType and not self.port().match(nodzInst.sourceSlot.port()))):
                    painter.setBrush(uiUtil.ConvertDataToColor(config['non_connectable_color']))
                else:
                    painter.setPen(self._connectable_pen)
                    painter.setBrush(self.brush)

        rect =  self.boundingRect()

        if self.__port.isOptional():
            poly = QtGui.QPolygonF()
            poly.append(QtCore.QPointF(rect.x() + rect.width() * 0.5, rect.y() + 2))
            poly.append(QtCore.QPointF(rect.x() + rect.width(), rect.y() + rect.height()))
            poly.append(QtCore.QPointF(rect.x(), rect.y() + rect.height()))
            painter.drawPolygon(poly)
        elif self.__port.hasLinkedParam():
            painter.drawRect(rect)
        else:
            painter.drawEllipse(rect)

    def connect(self, plug_item, connection):
        """
        Connect to the given plug item.

        """
        need_to_cleanup = False

        if len(self.connected_slots) > 0:
            # Already connected.
            self.connections[0]._remove()
            self.connected_slots = list()
            need_to_cleanup = True

        # Populate connection.
        connection.plugItem = plug_item
        connection.socketNode = self.parentItem().name
        connection.socketAttr = self.attribute

        # Add plug to connected slots.
        self.connected_slots.append(plug_item)

        # Add connection.
        if connection not in self.connections:
            self.connections.append(connection)

        # Emit signal.
        nodzInst = self.scene().views()[0]
        nodzInst.portConnected(plug_item.port(), self.port())

        nodzInst.signal_SocketConnected.emit(connection.plugNode, connection.plugAttr, connection.socketNode, connection.socketAttr)
        if need_to_cleanup:
            nodzInst.cleanUpProxies()

    def disconnect(self, connection):
        """
        Disconnect the given connection from this socket item.

        """
        # Emit signal.
        plug_item = connection.plugItem

        nodzInst = self.scene().views()[0]
        if plug_item is not None:
            nodzInst.portDisconnected(plug_item.port(), self.port())

        # Remove connected plugs
        if connection.plugItem in self.connected_slots:
            self.connected_slots.remove(connection.plugItem)

        # Remove connections
        self.connections.remove(connection)

    def mouseReleaseEvent(self, event):
        nodzInst = self.scene().views()[0]
        if event.button() == QtCore.Qt.LeftButton:
            nodzInst.drawingConnection = False
            nodzInst.currentDataType = None

            target = self.scene().itemAt(event.scenePos().toPoint(), QtGui.QTransform())

            if not isinstance(target, nodz_main.SlotItem) and not isinstance(target, ProxyItem):
                self.newConnection._remove()
                super(nodz_main.SlotItem, self).mouseReleaseEvent(event)

                return

            if isinstance(self, InputProxyPortItem):
                if isinstance(target, ProxyItem) and self.proxyNode().block().parent() == target.block().parent():
                    self.newConnection._remove()
                    super(nodz_main.SlotItem, self).mouseReleaseEvent(event)

                    return

                if isinstance(target, OutputProxyPortItem) and self.proxyNode().block().parent() == target.proxyNode().block().parent():
                    self.newConnection._remove()
                    super(nodz_main.SlotItem, self).mouseReleaseEvent(event)

                    return

            if isinstance(target, ProxyItem):
                if target.isOutProxy():
                    self.newConnection._remove()
                    super(nodz_main.SlotItem, self).mouseReleaseEvent(event)

                    return
                else:
                    proxy_bloc = target.block()
                    if proxy_bloc.hasConnection(self.__port):
                        self.newConnection._remove()
                        super(nodz_main.SlotItem, self).mouseReleaseEvent(event)

                        return

                    else:
                        new_name = self.port().name()
                        prnt = self.port().parent()
                        if prnt:
                            new_name = "{}_{}".format(prnt.name(), new_name)
                        prx = nodzInst.addInputProxy(self.port().typeClass(), new_name)
                        proxy_node = nodzInst.inProxyNode()
                        target_port = proxy_node.plugs[prx.name()]
                        self.newConnection.target = target_port
                        self.newConnection.source = self
                        self.newConnection.target_point = target_port.center()
                        self.newConnection.source_point = self.center()

                        self.connect(target_port, self.newConnection)
                        target_port.connect(self, self.newConnection)

                        self.newConnection.updatePath()

            else:
                if target.accepts(self):
                    self.newConnection.target = target
                    self.newConnection.source = self
                    self.newConnection.target_point = target.center()
                    self.newConnection.source_point = self.center()

                    self.connect(target, self.newConnection)
                    target.connect(self, self.newConnection)

                    self.newConnection.updatePath()
                else:
                    self.newConnection._remove()
        else:
            super(nodz_main.SlotItem, self).mouseReleaseEvent(event)

        nodzInst.currentHoveredNode = None

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.newConnection = ChainItem(self.center(),
                                           self.mapToScene(event.pos()),
                                           self,
                                           None)

            self.connections.append(self.newConnection)
            self.scene().addItem(self.newConnection)

            nodzInst = self.scene().views()[0]
            nodzInst.drawingConnection = True
            nodzInst.sourceSlot = self
            nodzInst.currentDataType = self.dataType
        else:
            super(SlotItem, self).mousePressEvent(event)

    def accepts(self, plug_item):
        if isinstance(plug_item, nodz_main.PlugItem):
            if (self.parentItem() != plug_item.parentItem() and
                len(self.connected_slots) <= 1):
                if self.port().match(plug_item.port()):
                    if plug_item in self.connected_slots:
                        return False
                    else:
                        return True
            else:
                return False
        else:
            return False


class OutputProxyPortItem(OutputPortItem):
    def __init__(self, parent, proxyNode, port, index, preset, dataType):
        super(OutputProxyPortItem, self).__init__(parent, port, index, preset, dataType)
        self.__proxy_node = proxyNode

    def proxyNode(self):
        return self.__proxy_node


class InputProxyPortItem(InputPortItem):
    def __init__(self, parent, proxyNode, port, index, preset, dataType):
        super(InputProxyPortItem, self).__init__(parent, port, index, preset, dataType)
        self.__proxy_node = proxyNode

    def proxyNode(self):
        return self.__proxy_node


class ChainItem(nodz_main.ConnectionItem):
    def __init__(self, source_point, target_point, source, target):
        super(ChainItem, self).__init__(source_point, target_point, source, target)

    def updatePath(self):
        self._createStyle()
        super(ChainItem, self).updatePath()

    def _updatePen(self):
        color = None
        config = None

        for p in [self.source, self.target]:
            if p is None:
                continue

            if config is None:
                config = p.scene().views()[0].config

            color = p.brush.color()
            if p.port().isInPort():
                break

        if color is None:
            color = uiUtil.ConvertDataToColor(config['connection_color'])

        self._pen = QtGui.QPen(color)
        self._pen.setWidth(config['connection_width'])

    def _createStyle(self):
        self._updatePen()
        self.setAcceptHoverEvents(True)
        self.setZValue(-1)

    def mouseReleaseEvent(self, evnt):
        nodzInst = self.scene().views()[0]
        super(ChainItem, self).mouseReleaseEvent(evnt)
        if isinstance(nodzInst, SubNet):
            nodzInst.cleanUpProxies()
