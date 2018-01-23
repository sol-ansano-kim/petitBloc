from .Nodz import nodz_main
from .Nodz import nodz_utils
from Qt import QtGui
from Qt import QtCore
from Qt import QtWidgets
from . import model
from . import blockCreator


class Graph(nodz_main.Nodz):
    KeyPressed = QtCore.Signal(int)
    ItemDobleClicked = QtCore.Signal(object)
    BlockDeleted = QtCore.Signal(object)
    BoxCreated = QtCore.Signal(object, bool)
    BoxDeleted = QtCore.Signal(object)
    CurrentNodeChanged = QtCore.Signal(object)

    def __init__(self, name="", boxObject=None, parent=None):
        super(Graph, self).__init__(parent)
        self.__model = model.BoxModel(name=name, boxObject=boxObject)
        self.__current_block = None
        self.__creator = blockCreator.BlockCreator(self, self.__model.blockClassNames())
        self.__creator.BlockCreatorEnd.connect(self.addBlock)
        self.signal_NodeDeleted.connect(self.__nodeDeleted)
        self.signal_NodeSelected.connect(self.__nodeSelected)
        self.installEventFilter(self)
        self.initialize()

    def boxModel(self):
        return self.__model

    def box(self):
        return self.__model.box()

    def mouseDoubleClickEvent(self, evnt):
        itm = self.itemAt(evnt.pos())

        if itm is not None:
            if itm.block().hasNetwork():
                self.ItemDobleClicked.emit(itm.block())

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

        if evnt.type() == QtCore.QEvent.Type.KeyPress:
            self.KeyPressed.emit(evnt.key())
            if evnt.key() == QtCore.Qt.Key_Tab:
                self.__creator.show(self.mapFromGlobal(QtGui.QCursor.pos()))
                return True

        return False

    def currentBlock(self):
        return self.__current_block

    def __nodeSelected(self, selectedNodes):
        if not selectedNodes:
            self.__current_block = None
            self.CurrentNodeChanged.emit(None)
            return

        node = selectedNodes[0]
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
            b = self.__model.block(n)
            self.BlockDeleted.emit(b)
            if b.hasNetwork():
                self.BoxDeleted.emit(b)
            self.__model.deleteNode(n)

    def portConnected(self, srcPort, dstPort):
        self.__model.connect(srcPort, dstPort)

    def portDisconnected(self, srcPort, dstPort):
        self.__model.disconnect(srcPort, dstPort)

    def addBlock(self, blockType, blockName=None, position=None, init=True):
        if not blockType:
            return None

        bloc = self.__model.addBlock(blockType, name=blockName)
        if bloc is None:
            return None

        if position is None:
            position = self.mapToScene(self.mapFromGlobal(QtGui.QCursor.pos()))

        node = self.createNode(bloc, position=position)

        if bloc.hasNetwork():
            self.BoxCreated.emit(bloc, init)

        # TODO : preset
        for ip in bloc.inputs():
            self.createAttribute(node=node, port=ip, plug=False, socket=True, preset="attr_preset_1", dataType=ip.typeClass())

        for op in bloc.outputs():
            self.createAttribute(node=node, port=op, plug=True, socket=False, preset="attr_preset_1", dataType=op.typeClass())

        return node

    def createNode(self, bloc, preset='node_default', position=None, alternate=True):
        if bloc.name() in self.scene().nodes.keys():
            print('A node with the same name already exists : {0}'.format(bloc.name()))
            print('Node creation aborted !')
            return

        nodeItem = BlocItem(bloc, alternate, preset, self.config)

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

    def createAttribute(self, node, port, index=-1, preset='attr_default', plug=True, socket=True, dataType=None, proxyNode=None):
        if not node in self.scene().nodes.values():
            print('Node object does not exist !')
            print('Attribute creation aborted !')
            return

        if port.name() in node.attrs:
            print('An attribute with the same name already exists : {0}'.format(port.name()))
            print('Attribute creation aborted !')
            return

        node._createAttribute(port, index=index, preset=preset, plug=plug, socket=socket, dataType=dataType, proxyNode=proxyNode)

        # Emit signal.
        self.signal_AttrCreated.emit(node.name, index)

    def initProxyNode(self):
        pass


class SubNet(Graph):
    ProxyPortAdded = QtCore.Signal(object, object, object)
    ProxyPortRemoved = QtCore.Signal(object, object, str)

    def __init__(self, name="", boxObject=None, parent=None):
        super(SubNet, self).__init__(name=name, boxObject=boxObject, parent=parent)
        self.__proxy_in = ProxyItem(self.boxModel().inProxyBlock(), ProxyItem.In, False, "node_default", self.config)
        self.__proxy_out = ProxyItem(self.boxModel().outProxyBlock(), ProxyItem.Out, False, "node_default", self.config)

        self.scene().nodes[self.__proxy_in.block().name()] = self.__proxy_in
        self.scene().nodes[self.__proxy_out.block().name()] = self.__proxy_out
        self.scene().addItem(self.__proxy_in)
        self.scene().addItem(self.__proxy_out)

        self.BlockDeleted.connect(self.cleanUpProxies)

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

    def cleanUpProxies(self):
        inputs, outputs = self.boxModel().cleanUpInputProxies()
        for p in outputs:
            self.deleteAttribute(self.__proxy_in, self.__proxy_in.attrs.index(p))
        for p in inputs:
            self.ProxyPortRemoved.emit(self.boxModel().box(), self.__proxy_in, p)

        inputs, outputs = self.boxModel().cleanUpOutputProxies()
        for p in inputs:
            self.deleteAttribute(self.__proxy_out, self.__proxy_out.attrs.index(p))
        for p in outputs:
            self.ProxyPortRemoved.emit(self.boxModel().box(), self.__proxy_out, p)

        self.__proxy_in.scene().updateScene()
        self.__proxy_out.scene().updateScene()

    def addInputProxy(self, typeClass, name):
        ip, op = self.boxModel().addInputProxy(typeClass, name)
        proxy_node = self.inProxyNode()
        self.createAttribute(node=proxy_node, port=op, plug=True, socket=False, preset="attr_preset_1", dataType=op.typeClass(), proxyNode=proxy_node)
        self.ProxyPortAdded.emit(self.box(), proxy_node, ip)
        return ip, op

    def addOutputProxy(self, typeClass, name):
        ip, op = self.boxModel().addOutputProxy(typeClass, name)
        proxy_node = self.outProxyNode()
        self.createAttribute(node=proxy_node, port=ip, plug=False, socket=True, preset="attr_preset_1", dataType=ip.typeClass(), proxyNode=proxy_node)
        self.ProxyPortAdded.emit(self.box(), proxy_node, op)
        return ip, op

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

    def initProxyNode(self):
        position = self.mapToScene(self.viewport().rect().center())
        self.__proxy_in.setPos(position - self.__proxy_in.nodeCenter - QtCore.QPoint(0, self.__proxy_in.height) * 1.5)
        self.__proxy_out.setPos(position - self.__proxy_in.nodeCenter + QtCore.QPoint(0, self.__proxy_in.height) * 1.5)


class BlocItem(nodz_main.NodeItem):
    def __init__(self, bloc, alternate, preset, config):
        super(BlocItem, self).__init__(bloc.name(), alternate, preset, config)
        self.__block = bloc
        # TODO : set style from config
        self.__error_pen = QtGui.QPen(QtGui.QColor(242, 38, 94))
        self.__error_brush = QtGui.QBrush(QtGui.QColor(75, 0, 0, 125))
        self.__hl_pen = QtGui.QPen(QtGui.QColor(98, 215, 234))
        self.__hl_pen.setStyle(QtCore.Qt.SolidLine)
        self.__hl_pen.setWidth(self.border + 2)
        self.__emphasize = False

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

            self.plugs[port.name()] = plugInst

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

            self.sockets[port.name()] = socketInst

        self.attrCount += 1

        if index == -1 or index > self.attrCount:
            self.attrs.append(port.name())
        else:
            self.attrs.insert(index, port.name())

        self.attrsData[port.name()] = {'name': port.name(),
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


            # Attribute base.
            self._attrBrush.setColor(nodz_utils._convertDataToColor(config[preset]['bg']))
            if self.alternate:
                self._attrBrushAlt.setColor(nodz_utils._convertDataToColor(config[preset]['bg'], True, config['alternate_value']))

            self._attrPen.setColor(nodz_utils._convertDataToColor([0, 0, 0, 0]))
            painter.setPen(self._attrPen)
            painter.setBrush(self._attrBrush)
            if (offset / self.attrHeight) % 2:
                painter.setBrush(self._attrBrushAlt)

            painter.drawRect(rect)

            # Attribute label.
            painter.setPen(nodz_utils._convertDataToColor(config[preset]['text']))
            painter.setFont(self._attrTextFont)

            # Search non-connectable attributes.
            if nodzInst.drawingConnection:
                if self == nodzInst.currentHoveredNode:
                    port = attrData['port']
                    if (nodzInst.sourceSlot.slotType == 'plug' and attrData['socket'] == False) or (nodzInst.sourceSlot.slotType == 'socket' and attrData['plug'] == False):
                        # Set non-connectable attributes color.
                        painter.setPen(nodz_utils._convertDataToColor(config['non_connectable_color']))

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


class ProxyItem(BlocItem):
    In = 0
    Out = 1
    def __init__(self, bloc, direction, alternate, preset, config):
        super(ProxyItem, self).__init__(bloc, alternate, preset, config)
        self.__bloc = bloc
        self.__direction = direction

    def isInProxy(self):
        return self.__direction is ProxyItem.In

    def isOutProxy(self):
        return self.__direction is ProxyItem.Out

    def _remove(self):
        pass

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
        super(OutputPortItem, self).__init__(parent, port.name(), index, preset, dataType)
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
                painter.setBrush(nodz_utils._convertDataToColor(config['non_connectable_color']))
                if (self.slotType == nodzInst.sourceSlot.slotType or (self.slotType != nodzInst.sourceSlot.slotType and not nodzInst.sourceSlot.port().match(self.port()))):
                    painter.setBrush(nodz_utils._convertDataToColor(config['non_connectable_color']))
                else:
                    _penValid = QtGui.QPen()
                    _penValid.setStyle(QtCore.Qt.SolidLine)
                    _penValid.setWidth(2)
                    _penValid.setColor(QtGui.QColor(255, 255, 255, 255))
                    painter.setPen(_penValid)
                    painter.setBrush(self.brush)

        painter.drawEllipse(self.boundingRect())

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
                        ip, op = nodzInst.addOutputProxy(self.port().typeClass(), self.port().name())
                        proxy_node = nodzInst.outProxyNode()
                        target_port = proxy_node.sockets[ip.name()]
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
        super(InputPortItem, self).__init__(parent, port.name(), index, preset, dataType)
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
                painter.setBrush(nodz_utils._convertDataToColor(config['non_connectable_color']))
                if (self.slotType == nodzInst.sourceSlot.slotType or (self.slotType != nodzInst.sourceSlot.slotType and not self.port().match(nodzInst.sourceSlot.port()))):
                    painter.setBrush(nodz_utils._convertDataToColor(config['non_connectable_color']))
                else:
                    _penValid = QtGui.QPen()
                    _penValid.setStyle(QtCore.Qt.SolidLine)
                    _penValid.setWidth(2)
                    _penValid.setColor(QtGui.QColor(255, 255, 255, 255))
                    painter.setPen(_penValid)
                    painter.setBrush(self.brush)

        painter.drawEllipse(self.boundingRect())

    def connect(self, plug_item, connection):
        """
        Connect to the given plug item.

        """
        if len(self.connected_slots) > 0:
            # Already connected.
            self.connections[0]._remove()
            self.connected_slots = list()

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
                        ip, op = nodzInst.addInputProxy(self.port().typeClass(), self.port().name())
                        proxy_node = nodzInst.inProxyNode()
                        target_port = proxy_node.plugs[op.name()]
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

    def mouseReleaseEvent(self, evnt):
        nodzInst = self.scene().views()[0]
        super(ChainItem, self).mouseReleaseEvent(evnt)
        if isinstance(nodzInst, SubNet):
            nodzInst.cleanUpProxies()
