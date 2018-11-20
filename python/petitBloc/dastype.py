from .core import Das


def DasType(schema):
    class SchemaType(Das):
        Schema = schema
        def __init__(self, value):
            super(SchemaType, self).__init__(value)
        
    return SchemaType
