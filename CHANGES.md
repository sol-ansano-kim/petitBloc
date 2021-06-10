# 1.3.3

## Improve interface

 - show detail of block

## Bug fix

 - Fix copying of das object


# 1.3.2

## Bug fix

 - Fix selected nodes moving issue when copy and paste box
 - Paste nodes around cursor properly


# 1.3.1

## Bug fix

 - Fix recursively querying parameter issue
 - fix current block upating issue


# 1.3.0

## Mismatch packet count issue

- The process may stop when the packet counts on both sides do not match. To solve this problem, we created a network that generates packets based on the count of the static data. 1.3.0 provides simpler solutions.<br>You can find a example file at examples/mismatch_packet_counts.blcs

- Packet duplicator : Repeat, DuplicateFlow

<img src="https://github.com/sol-ansano-kim/petitBloc/wiki/images/duplicateFlow.png" width="200"> <br>
<img src="https://github.com/sol-ansano-kim/petitBloc/wiki/images/repeat.png" width="200"> 

- Parameter linking :　A linked input port generates an infinite number of packets from the parameter if the port is not connected to another port.

<img src="https://github.com/sol-ansano-kim/petitBloc/wiki/images/linked1.png" width="300"> 
<img src="https://github.com/sol-ansano-kim/petitBloc/wiki/images/linked2.png" width="300"><br> 

```python
class SomeBlock(Block):
    def initialize(self):
        some_port = self.addInput(str, "someInput")
        some_param = self.addParam(str, "someParam")
        some_port.linkParam(some_param)
```

## Public API Changes
- Added python interfaces <br>
```python
Version()
AllBlockTypes()
BlockInfo(blockName)
GetParams(path, block=None)
GetContextParams(path)
GetConnections(path)
GetBlocks(path)
QueryScene(path)
```
- Optional port : New option to notify explicitly that the port is not mandatory.

<img src="https://github.com/sol-ansano-kim/petitBloc/wiki/images/optional.png" width="300"><br> 
```python
class SomeBlock(Block):
    def initialize(self):
        self.addInput(str, "someInput", optional=True)
```

- SubprocessWorker provides outputs and errors function

## Block Changes
- Name changes : Selector -> Fork, RegexSelector -> RegexFork, CastToFloat -> ToFloat, CastToInt -> ToInt, CastToBool -> ToBool and many ports and parameters. (Will be fixed automatically when scene open)
- New List blocks : ToList, ListHas, ListSet, ListRemove, ListFormat
- New Dict blocks : Dict, ToDict, DictHas, DictGet, DictSet, DictKeys, DictValues, DictItems, DictIter, DictRemove, DictUpdate, DictFormat
- New File blocks : PathDirname, PathBasename, PathJoin, FileExtension, FileSetExtension
- New Logic blocks : BooleanOp, Repeat, DuplicateFlow
- New Math blocks : Min, Max
- New String blocks : StringSplit, StringJoin, StringIsEmpty, StringCompare, StringStrip, StringFormat
- ContextDict : Generates a dict packet of containing SceneContext values 

## GUI improvements
- Improved Backdrop handling
- Default log level is now Warning
- Packet history viewer scrolls per pixel
- Boolean type parameter supports expression by mouse right click
- Improved the appearance of the parameter editor

## Internal
- using das 0.10.0
