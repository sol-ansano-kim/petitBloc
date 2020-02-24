

# PetitBloc

<img src="https://github.com/sol-ansano-kim/petitBloc/wiki/images/logo.jpg" width="640">

PetitBloc is a process chain framework, implemented in python.
This concept is derived from Flow Based Programming by [J. Paul Rodker-Morrison](http://www.jpaulmorrison.com/fbp/), and since it is implemented in Python, it can be used on almost all of the platforms and softwares that Python can be run.</p>

<img src="https://github.com/sol-ansano-kim/petitBloc/wiki/images/petit_title.jpeg" width="640">

[Nodz](https://github.com/LeGoffLoic/Nodz) and [Qt.py](https://github.com/mottosso/Qt.py) are used for its GUI. </p>Qt python module is required (PySide1 or 2, PyQt4 or 5).

## How to use it


[![Alt text](https://github.com/sol-ansano-kim/petitBloc/wiki/images/play_image.jpg)](https://youtu.be/GcFggNRwomo)


### GUI

You can make and run the process graph on PatitBloc GUI, or it can be run with python IDLE or standalone.

[GUI Tutorial](https://youtu.be/U8yAEK6vDQc)

- python
```python
import petitBloc.ui
petitBloc.ui.Show()
```

- standalone
```sh
bin/petitBlocUI
```


### CUI
The graph(.blcs file) can be called without GUI from python IDLE or petitBloc CUI.

- python
```python
import petitBloc
petitBloc.Run(path=<blcs file>)
```

- CUI
```sh
bin/petitBloc -s <blcs file>
```
More details of CUI 'petitBloc --help'

##
### Term
- Block : a basic unit of process
- Box : network of processes
- Packet : a basic unit of information
- Port : connection between processes, sending or accepting packet
- Parameter : attributes for block


### Box & ConditionalBox
Box is a network of Blocks. It contains several Blocks or Boxes and connects inside and outside.
ConditionalBox has a port named 'condition' and it won't run its network until the 'condition' accept the packet which is value 'True'.


### Expression & SceneContext
Parameters can be set by expressions with '='.

e.g.
```
= 1 * 2
= "test{}".format(1)
```

And it can reference other parameters of itself or others with absolute path or relative path.

e.g.
```
= ../@test * 2
= /scene/Box@test * 2
```

To get any environment variables, use '$'.
e.g.
```
= "$PATH"
```

SceneContext is an unique block in the scene and contains user defined parameters. These parameters can also be referenced in the expression with “$.

```
= $testInt * 2
= "$testString" + " test"
```

When execute the scene with CUI, parameters and sceneContext can be overridden with '-p', '-c'. (More details 'petitBloc --help')


## Expansion

### Writing a Custom Block

You can write some low-level or high-level blocks as a py file, and the directory has to be added to PETITBLOC_BLOCK_PATH environment variable.

```python
from petitBloc import block

class PlusNumber(block.Block):
    def __init__(self):
        super(PlusOne, self).__init__()
```

```sh
export PETITBLOC_BLOCK_PATH=$PETITBLOC_BLOCK_PATH:<file directory>
or
set PETITBLOC_BLOCK_PATH=%PETITBLOC_BLOCK_PATH%;<file directory>
```


And add any ports or parameters in the initialize method.

```python
...
    def initialize(self):
        self.addInput(float, "input")
        self.addParam(float, "number")
        self.addOutput(float, "output")
...
```

Possible to declare that the port is optional explicitly.

Also possible to link a port and a parameter. ([More detail](CHANGES.md#mismatch-packet-count-issue))

```python
...
    def initialize(self):
        self.addInput(float, "input1", optional=True)
        inport = self.addInput(float, "input2",)
        num_param = self.addParam(float, "number")
        inport.linkParam(num_param)
...
```


Write processing of a packet(s) into process() method.
The process() method will be called by run() method, and when the process() returns True, the block will keep accepting packets from input ports.

```python
...
    def process(self):
        input_packet = self.input("input").receive()

        # EOP means 'End of Packets'.
        # The previous process was done, so no more packet to process
        if input_packet.isEOP():
            return False

        value = input_packet.value()

        # drop() will decrease reference count of the packet.
        # Ofcourse python has a garbage collection, so we probably don`t worry about deleting the variables,
        # but this way make it more clear and to do it accurate time.
        input_packet.drop()

        number = self.param("number").get()

        self.output("output").send(value + number)

        return True
...
```

In some cases, we want to determine how the loop works. We can describe it with overriding run() method.

By default, run() method will work like this.

```python
...
    def run(self):
        while (True):
            if not self.process():
                break
...

```


Basically process() requires one packet at a time from all ports, and this may be inconvenient in some cases.
You can find several examples of asymmetric packet processing in blocks/stringBlocks.py


### Customizing Block Style

You can specify the styles of blocks in the "block file name".config.


### Logging

If you want logging of some information, you can output it with debug, warn or error method.
```python
...
    self.debug("DEBUG TEST")
    self.warn("WARNING TEST")
    self.error("ERROR TEST")
...
```

## Changes

[Release Notes](CHANGES.md)

## Block Packages

- [DCC software](https://github.com/sol-ansano-kim/pbDCCPacks)
- [Web toolkits](https://github.com/sol-ansano-kim/pbWebPacks)
