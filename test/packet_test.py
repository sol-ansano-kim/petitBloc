import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(__file__, "../../python")))
from petitBloc import packet


class PacketTest(unittest.TestCase):
    def test_init(self):
        none_pack = packet.Packet()
        self.assertIsNotNone(none_pack)
        self.assertEqual(str(none_pack), "Packet<'NoneType'>")
        self.assertEqual(none_pack.value(), None)

        int_pack = packet.Packet(1)
        self.assertIsNotNone(int_pack)
        self.assertEqual(str(int_pack), "Packet<'int'>")
        self.assertEqual(int_pack.value(), 1)

        str_pack = packet.Packet("Hello")
        self.assertIsNotNone(str_pack)
        self.assertEqual(str(str_pack), "Packet<'str'>")
        self.assertEqual(str_pack.value(), "Hello")

        class TestObject(object):
            def __init__(self):
                super(TestObject, self).__init__()

        obj = TestObject()
        obj_pack = packet.Packet(obj)
        self.assertEqual(str(obj_pack), "Packet<'TestObject'>")

    def test_ref_count(self):
        str_pack = packet.Packet("test")
        str_pack.pickUp()
        self.assertTrue(str_pack.drop())

    def test_cast_packet(self):
        float_pack = packet.Packet(1.5)
        float_pack.pickUp()
        int_pack = packet.CastedPacket(float_pack, int)
        int_pack.pickUp()
        bool_pack = packet.CastedPacket(float_pack, bool)
        bool_pack.pickUp()
        float_pack2 = packet.CastedPacket(bool_pack, float)
        float_pack2.pickUp()

        self.assertEqual(float_pack.value(), 1.5)
        self.assertEqual(int_pack.value(), 1)
        self.assertEqual(bool_pack.value(), True)
        self.assertEqual(float_pack2.value(), 1.0)

        self.assertFalse(float_pack.drop())
        self.assertEqual(float_pack.refCount(), 3)
        self.assertFalse(int_pack.drop())
        self.assertEqual(float_pack.refCount(), 2)
        self.assertFalse(bool_pack.drop())
        self.assertEqual(float_pack.refCount(), 1)
        self.assertTrue(float_pack2.drop())


if __name__ == "__main__":
    unittest.main()
