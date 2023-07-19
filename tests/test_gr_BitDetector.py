
import sys

import numpy as np
import pmt
from gnuradio import gr, gr_unittest
from gnuradio import blocks

sys.path.append('..')
from examples.ALS162_Receiver import ALS162_Receiver_epy_block_0 as ALS162_BitDetector
import msg_test_block


class test_gr_bitDetector(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()
        #self.maxDiff = None

    def setUp_Block(self):
        # NOTE the vector is just simple default value for the instantiation
        vin = np.zeros(1)

        vin_p1 = vin.copy().tolist()
        vin_m1 = vin.copy().tolist()
        vin_z0 = vin.copy().tolist()
        vin_p2 = vin.copy().tolist()
        vin_m2 = vin.copy().tolist()

        src_sig1 = blocks.vector_source_f(vin_p1, False)
        src_sig2 = blocks.vector_source_f(vin_m1, False)
        src_sig3 = blocks.vector_source_f(vin_z0, False)
        src_sig4 = blocks.vector_source_f(vin_p2, False)
        src_sig5 = blocks.vector_source_f(vin_m2, False)

        self.snk_sig = blocks.vector_sink_f(1)
        self.snk_msg = msg_test_block.msg_receiver_test_block()

        # NOTE the test_block must be instantiated and run once
        #      before a subroutines is called manually
        self.test_block = ALS162_BitDetector.ALS162_BitDetector_blk(
            sample_rate=16000, tolerance=0.004, queue_len=1)

        self.tb.connect(src_sig1, (self.test_block, 0))
        self.tb.connect(src_sig2, (self.test_block, 1))
        self.tb.connect(src_sig3, (self.test_block, 2))
        self.tb.connect(src_sig4, (self.test_block, 3))
        self.tb.connect(src_sig5, (self.test_block, 4))

        self.tb.connect((self.test_block, 0), self.snk_sig)
        self.tb.msg_connect((self.test_block, 'msg_out'), (self.snk_msg, "msg_in"))

        self.tb.run()

    def tearDown(self):
        # return to initial state
        ALS162_BitDetector._num_ones_p1 = 0
        ALS162_BitDetector._num_ones_p2 = 0
        ALS162_BitDetector._num_ones_m1 = 0
        ALS162_BitDetector._num_ones_m2 = 0
        ALS162_BitDetector._num_ones_z0 = 0
        ALS162_BitDetector._num_zeros = 0

        self.tb = None

    def test_gr_work(self):
        self.setUp_Block()

        vin = np.zeros(2)
        vin_p1 = vin.copy().tolist()
        vin_m1 = vin.copy().tolist()
        vin_z0 = vin.copy().tolist()
        vin_p2 = vin.copy().tolist()
        vin_m2 = vin.copy().tolist()

        vout = [vin.copy().tolist()]
        # TODO verify 2 is indeed to be expected
        objective = 2
        result = self.test_block.work(input_items=[vin_p1.copy(), vin_m1.copy(),
                                                   vin_z0.copy(), vin_p2.copy(),
                                                   vin_m2.copy()], output_items=vout)
        self.assertEqual(objective, result)

        # check default sample_rate
        objective = 16000
        result = self.test_block.sample_rate
        self.assertEqual(objective, result)

        # check default tolerance
        objective = 64
        result = self.test_block._tolerance
        self.assertEqual(objective, result)

        # check subframe length
        objective = 400
        result = self.test_block._subframe
        self.assertEqual(objective, result)

        # check subframe_lo length
        objective = 336
        result = self.test_block._subframe_lo
        self.assertEqual(objective, result)

        # check subframe_lo2 length
        objective = 208
        result = self.test_block._subframe_lo2
        self.assertEqual(objective, result)

        self.tb.stop()

        del self.test_block
        self.tearDown()

    def test_clear_counters(self):
        self.setUp_Block()

        ALS162_BitDetector._num_ones_p1 = 4
        ALS162_BitDetector._num_ones_m1 = 4
        ALS162_BitDetector._num_ones_z0 = 4
        ALS162_BitDetector._num_ones_p2 = 4
        ALS162_BitDetector._num_ones_m2 = 4
        self.test_block.clear_counters()

        objective = 0
        self.assertEqual(objective, ALS162_BitDetector._num_ones_p1)
        self.assertEqual(objective, ALS162_BitDetector._num_ones_m1)
        self.assertEqual(objective, ALS162_BitDetector._num_ones_z0)
        self.assertEqual(objective, ALS162_BitDetector._num_ones_p2)
        self.assertEqual(objective, ALS162_BitDetector._num_ones_m2)

        del self.test_block
        self.tearDown()

    def gr_bitDetector_tester(self, val, stream_len):
        vin_zero = np.zeros(stream_len + 1)
        vin_one = np.ones(stream_len)
        vin_one = np.append(vin_one, np.zeros(1))

        vin_p1 = vin_zero.copy().tolist()
        vin_m1 = vin_zero.copy().tolist()
        vin_z0 = vin_zero.copy().tolist()
        vin_p2 = vin_zero.copy().tolist()
        vin_m2 = vin_zero.copy().tolist()

        if val == 2:
            vin_p2 = vin_one.copy().tolist()
        elif val == -2:
            vin_m2 = vin_one.copy().tolist()
        elif val == 1:
            vin_p1 = vin_one.copy().tolist()
        elif val == -1:
            vin_m1 = vin_one.copy().tolist()
        elif val == 0:
            vin_z0 = vin_one.copy().tolist()

        result = self.test_block.extract_bits(vin_p1.copy(), vin_m1.copy(),
                                              vin_z0.copy(), vin_p2.copy(),
                                              vin_m2.copy())
        self.tb.run()
        self.tb.stop()

        # check output message
        if val > 0:
            objective = pmt.intern(f"+{val},")
        elif val <= 0:
            objective = pmt.intern(f"{val},")
        self.assertEqual(objective, self.snk_msg.cur_msg)

        self.tearDown()

        return result

    def test_gr_bitDetector_p2(self):
        self.setUp_Block()

        stream_len = 300
        objective = [0]*stream_len + [2]
        result = self.gr_bitDetector_tester(2, stream_len)
        self.assertListEqual(objective, result.tolist())

        # TODO check tags in output signal

        del self.test_block
        self.tearDown()

    def test_gr_bitDetector_m2(self):
        self.setUp_Block()

        stream_len = 300
        objective = [0]*stream_len + [-2]
        result = self.gr_bitDetector_tester(-2, stream_len)
        self.assertListEqual(objective, result.tolist())

        # TODO check tags in output signal

        del self.test_block
        self.tearDown()

    def test_gr_bitDetector_p1_a(self):
        self.setUp_Block()

        stream_len = 336
        objective = [0]*stream_len + [1]
        result = self.gr_bitDetector_tester(1, stream_len)
        self.assertListEqual(objective, result.tolist())

        # TODO check tags in output signal

        del self.test_block
        self.tearDown()

    def test_gr_bitDetector_p1_b(self):
        self.setUp_Block()

        stream_len = 399
        objective = [0]*stream_len + [1]
        result = self.gr_bitDetector_tester(1, stream_len)
        self.assertListEqual(objective, result.tolist())

        # TODO check tags in output signal

        del self.test_block
        self.tearDown()

    def test_gr_bitDetector_p1_c(self):
        self.setUp_Block()

        stream_len = 400
        objective = [0]*399 + [1] + [0]
        result = self.gr_bitDetector_tester(1, stream_len)
        self.assertListEqual(objective, result.tolist())

        # TODO check tags in output signal

        del self.test_block
        self.tearDown()

    def test_gr_bitDetector_p1_d(self):
        self.setUp_Block()

        stream_len = 405
        objective = [0]*399 + [1] + [0]*6
        result = self.gr_bitDetector_tester(1, stream_len)
        self.assertListEqual(objective, result.tolist())

        # TODO check tags in output signal

        del self.test_block
        self.tearDown()

    def test_gr_bitDetector_p1_e(self):
        self.setUp_Block()

        stream_len = 799
        objective = [0]*399 + [1] + [0]*399 + [1]
        result = self.gr_bitDetector_tester(1, stream_len)
        self.assertListEqual(objective, result.tolist())

        # TODO check tags in output signal

        del self.test_block
        self.tearDown()

    def test_gr_bitDetector_m1(self):
        self.setUp_Block()

        stream_len = 336
        objective = [0] * stream_len + [-1]
        result = self.gr_bitDetector_tester(-1, stream_len)
        self.assertListEqual(objective, result.tolist())

        # TODO check tags in output signal

        del self.test_block
        self.tearDown()

    def test_gr_bitDetector_m1_c(self):
        self.setUp_Block()

        stream_len = 400
        objective = [0]*399 + [-1] + [0]
        result = self.gr_bitDetector_tester(-1, stream_len)
        self.assertListEqual(objective, result.tolist())

        # TODO check tags in output signal

        del self.test_block
        self.tearDown()

    def test_gr_bitDetector_z0(self):
        self.setUp_Block()

        stream_len = 300
        objective = [0] * stream_len + [0]
        result = self.gr_bitDetector_tester(0, stream_len)
        self.assertListEqual(objective, result.tolist())

        # TODO check tags in output signal

        del self.test_block
        self.tearDown()

    def test_gr_bitDetector_z0_c(self):
        self.setUp_Block()

        stream_len = 400
        objective = [0]*399 + [0] + [0]
        result = self.gr_bitDetector_tester(0, stream_len)
        self.assertListEqual(objective, result.tolist())

        # TODO check tags in output signal

        del self.test_block
        self.tearDown()

if __name__ == '__main__':
    gr_unittest.run(test_gr_bitDetector.test_gr_work(), "test_gr_BitDetector.xml")
    gr_unittest.run(test_gr_bitDetector.test_gr_bitDetector_p2(), "test_gr_BitDetector.xml")
