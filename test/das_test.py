import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(__file__, "../../python")))
sys.path.append(os.path.abspath(os.path.join(__file__, "../../das/python")))
os.environ["DAS_SCHEMA_PATH"] = os.path.abspath(os.path.join(__file__, "../../testBlock"))
from petitBloc import block
from petitBloc import port
from petitBloc import chain
from petitBloc import dastype
import das


class DasTest(unittest.TestCase):
    def test_dasType(self):
        i = dastype.DasType("dasTest.intType")
        self.assertIsNotNone(i)
        f = dastype.DasType("dasTest.floatType")
        self.assertIsNotNone(f)
        self.assertEqual(i.Schema, "dasTest.intType")
        self.assertEqual(f.Schema, "dasTest.floatType")
        self.assertNotEqual(i.Schema, f.Schema)

        self.assertIsNotNone(i(1))
        self.assertIsNotNone(f(1.0))
        self.assertTrue(i.check(1))
        self.assertFalse(i.check(2.25))
        self.assertTrue(f.check(1))
        self.assertTrue(f.check(12.12))
        self.assertFalse(i.check("a"))

        st = dastype.DasType("dasTest.struct")
        self.assertTrue(st.check({"i": 1, "f": 1.0, "s": "string"}))        
        self.assertFalse(st.check({"i": 1, "s": "string"}))
        self.assertFalse(st.check({"i": 1, "f": 1.0, "s": 1}))
        sti = st({"i": 1, "f": 1.0, "s": "string", "trash": 1})
        self.assertFalse(hasattr(sti.value(), "trash"))

    def test_dasPort(self):
        src_port1 = port.OutPort(dastype.DasType("dasTest.struct"))
        dst_port1 = port.InPort(dastype.DasType("dasTest.struct"))
        dst_port2 = port.InPort(dastype.DasType("dasTest.intType"))
        self.assertIsNotNone(src_port1)
        self.assertIsNotNone(dst_port1)
        self.assertIsNotNone(dst_port2)
        self.assertIsNotNone(chain.Chain(src_port1, dst_port1))
        self.assertIsNone(chain.Chain(src_port1, dst_port2))
        src_port1.activate()
        self.assertTrue(src_port1.send({"i": 1, "f": 1.0, "s": "string", "trash": "aa"}))
        p = dst_port1.receive()
        self.assertFalse(p.isEOP())
        self.assertEqual(p.value(), {"i": 1, "f": 1.0, "s": "string"})

        self.assertTrue(src_port1.match(dst_port1))
        self.assertFalse(src_port1.match(dst_port2))


if __name__ == "__main__":
    unittest.main()
