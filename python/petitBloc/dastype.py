from .core import Das
from .core import DasTypeBase


def DasType(schema):
    class SchemaType(Das):
        Schema = schema
        def __init__(self, value):
            super(SchemaType, self).__init__(value)
        
    return SchemaType
