import sys

import numpy as np
import pmt
from gnuradio import gr, gr_unittest

sys.path.append('..')
from examples.ALS162_Receiver \
    import ALS162_Receiver_epy_block_2 as ALS162_Correlation


class test_gr_Correlation(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def setUp_Block(self):
        self.test_block = ALS162_Correlation.ALS162_Correlation_blk()

    def tearDown(self):
        # return to initial state
        ALS162_Correlation._counter = 0
        ALS162_Correlation._msg_window = np.empty(0)

    def test_gr_handle_msg(self):
        # check default sample_rate
        self.setUp_Block()
        objective = 3
        result = self.test_block.position_thres
        self.assertEqual(objective, result)
        del self.test_block
        self.tearDown()

        self.setUp_Block()
        objective = 1
        result = self.test_block.symbol_thres
        self.assertEqual(objective, result)
        del self.test_block
        self.tearDown()

        self.setUp_Block()
        objective = []
        self.test_block.handle_msg(pmt.intern("0"))
        result = ALS162_Correlation._msg_window
        self.assertEqual(objective, list(result))
        del self.test_block
        self.tearDown()

        self.setUp_Block()
        objective_msg = "2, 00"
        objective_window = 39*[0.0]
        msg = "0,0,0,0,0,0,0,0,0,0," + \
              "0,0,0,0,0,0,0,0,0,0," + \
              "0,0,0,0,0,0,0,0,0,0," + \
              "0,0,0,0,0,0,0,0,0,0," + \
              "0,0,0,0,0,0,0,0,0,0," + \
              "0,0,0,0,0,0,0,0,0,0," + \
              "0,0,0,0,0,0,0,0,0,0," + \
              "0,0,0,0,0,0,0,0,0,0"
        pmt_msg = pmt.intern(msg)
        result_msg = self.test_block.handle_msg(pmt_msg)
        result_window = ALS162_Correlation._msg_window
        self.assertEqual(objective_window, list(result_window))
        self.assertEqual(objective_msg, result_msg)
        del self.test_block
        self.tearDown()

        self.setUp_Block()
        objective_msg = "1, 27"
        objective_window = 39*[0.0]
        msg = "+1,-1,-1,+1,+1,-1,-1,+1,+1,0," + \
              "-2,0,+1,+1,-1,-1,+1,0,+1," + \
              "0,-2,0,+2,0,-1,-1,+1,0,-1," + \
              "+1,+1,0,-2,0,+1,0,0,0,0,0," + \
              "0,0,0,0,0,0,0,0,0,0,0,0,0," + \
              "0,0,0,0,0,0,0,0,0,0,0,0,0," + \
              "0,0,0,0,0,0,0,0,0,0,0,0,0,"
        pmt_msg = pmt.intern(msg)
        result_msg = self.test_block.handle_msg(pmt_msg)
        result_window = ALS162_Correlation._msg_window
        self.assertEqual(objective_window, list(result_window))
        self.assertEqual(objective_msg, result_msg)
        del self.test_block
        self.tearDown()

        self.setUp_Block()
        objective_msg = "E, 27"
        objective_window = 39*[0.0]
        msg = "+1,-1,-2,+1,+1,0,-2,+1,+1,0," + \
              "-2,0,+1,+1,-1,-1,+1,0,+1," + \
              "0,-2,0,+2,0,-1,-1,+1,0,-1," + \
              "+1,+1,0,-2,0,+1,0,0,0,0,0," + \
              "0,0,0,0,0,0,0,0,0,0,0,0,0," + \
              "0,0,0,0,0,0,0,0,0,0,0,0,0," + \
              "0,0,0,0,0,0,0,0,0,0,0,0,0,"
        pmt_msg = pmt.intern(msg)
        result_msg = self.test_block.handle_msg(pmt_msg)
        result_window = ALS162_Correlation._msg_window
        self.assertEqual(objective_window, list(result_window))
        self.assertEqual(objective_msg, result_msg)
        del self.test_block
        self.tearDown()

        self.setUp_Block()
        objective_msg = "0, EE"
        objective_window = [+1,-1,-1,+1,0,0,0,0] + 16*[-1,+1]
        msg = "+1,-1,-1,+1,0,0,0,0,+1," + \
              "+1,+1,-1,-1,+1,+1,-1,0,-1,-1,+1," + \
              "-2,+1,0,-1,+2,-1,-1,+2,2,-1," + \
              "-1,+1,-2,-1,-1,+2,+1,0,0,0,+1," + \
              "-1,-1,+1,0,0,0,0,-1,+1,-1,+1,-1,+1," + \
              "-1,+1,-1,+1,-1,+1,-1,+1,-1,+1,-1,+1,-1," + \
              "+1,-1,+1,-1,+1,-1,+1,-1,+1,-1,+1,-1,+1,"
        pmt_msg = pmt.intern(msg)
        result_msg = self.test_block.handle_msg(pmt_msg)
        result_window = ALS162_Correlation._msg_window
        self.assertEqual(objective_window, list(result_window))
        self.assertEqual(objective_msg, result_msg)
        del self.test_block
        self.tearDown()

        self.setUp_Block()
        objective_msg = "E, EE"
        objective_window = ([-1,+1,-2,-1,-1,+2,+1,0,0,0,
                            +1,-1,-1,+1,-2,+2,0,0] + 16*[-1,+1])
        msg = "+1,-1,-1,+1,0,+2,-2,0,+1," + \
              "+1,+1,-1,-1,+1,+1,-1,0,-1,-1,+1," + \
              "-2,+1,0,-1,+2,-1,-1,+2,2,-1," + \
              "-1,+1,-2,-1,-1,+2,+1,0,0,0,+1," + \
              "-1,-1,+1,-2,+2,0,0,-1,+1,-1,+1,-1,+1," + \
              "-1,+1,-1,+1,-1,+1,-1,+1,-1,+1,-1,+1,-1," + \
              "+1,-1,+1,-1,+1,-1,+1,-1,+1,-1,+1,-1,+1,"
        pmt_msg = pmt.intern(msg)
        result_msg = self.test_block.handle_msg(pmt_msg)
        result_window = ALS162_Correlation._msg_window
        self.assertEqual(objective_window, list(result_window))
        self.assertEqual(objective_msg, result_msg)
        del self.test_block
        self.tearDown()

    def test_gr_prepare_window(self):
        self.setUp_Block()
        msg = pmt.intern("1,0,1,0,")
        objective = [1, 0, 1, 0]
        self.test_block.prepare_window(msg)
        result = ALS162_Correlation._msg_window
        self.assertListEqual(objective, list(result))
        self.tearDown()

        self.setUp_Block()
        msg = pmt.intern("0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,")
        objective = 20*[0]
        self.test_block.prepare_window(msg)
        result = ALS162_Correlation._msg_window
        self.assertListEqual(objective, list(result))
        self.tearDown()

        self.setUp_Block()
        msg = pmt.intern("1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,")
        objective = [1] + 19*[0]
        self.test_block.prepare_window(msg)
        result = ALS162_Correlation._msg_window
        self.assertListEqual(objective, list(result))
        self.tearDown()

    def test_gr_rotate_dict(self):
        self.setUp_Block()
        dictionary = {0: (0, 0), 1: (1, 0), 2: (2, 0), 3: (3, 0)}
        objective = {0: (0, 0), 1: (1, 0), 2: (2, 0), 3: (3, 0)}
        result = self.test_block.rotate_dict(dictionary, 0)
        self.assertListEqual(list(objective.keys()), list(result.keys()))
        self.assertListEqual(list(objective.values()), list(result.values()))
        self.tearDown()

        self.setUp_Block()
        dictionary = {0: (0,0), 1: (1,0), 2: (2,0), 3: (3,0)}
        objective = {1: (1,0), 2: (2,0), 3: (3,0), 0: (0,0)}
        result = self.test_block.rotate_dict(dictionary, 1)
        self.assertListEqual(list(objective.keys()), list(result.keys()))
        self.assertListEqual(list(objective.values()), list(result.values()))
        self.tearDown()

        self.setUp_Block()
        dictionary = {0: (0, 0), 1: (1, 0), 2: (2, 0), 3: (3, 0)}
        objective = {2: (2, 0), 3: (3, 0), 0: (0, 0), 1: (1, 0)}
        result = self.test_block.rotate_dict(dictionary, 2)
        self.assertListEqual(list(objective.keys()), list(result.keys()))
        self.assertListEqual(list(objective.values()), list(result.values()))
        self.tearDown()

        self.setUp_Block()
        dictionary = {0: (0, 0), 1: (1, 0), 2: (2, 0), 3: (3, 0)}
        objective = {3: (3, 0), 0: (0, 0), 1: (1, 0), 2: (2, 0)}
        result = self.test_block.rotate_dict(dictionary, -1)
        self.assertListEqual(list(objective.keys()), list(result.keys()))
        self.assertListEqual(list(objective.values()), list(result.values()))
        self.tearDown()

    def test_gr_compare_position_code(self):
        self.setUp_Block()
        objective_min_dist = 0
        objective_min_dist_idx = 0
        objective_pos_key = (0,+1,-1, 0, 0, 0,+1,-1, 0, 0, 0, 0, 0, 0, 0,-1,
                             0,+2, 0,-2, 0,+2, 0,-2, 0,+1, 0, 0, 0, 0, 0, 0)
        objective_dictionary = self.test_block.position_code_swap_dict.copy()
        objective_error = False
        window = [0,+1,-1, 0, 0, 0,+1,-1, 0, 0, 0, 0, 0, 0, 0,-1,
                  0,+2, 0,-2, 0,+2, 0,-2, 0,+1, 0, 0, 0, 0, 0, 0]
        [min_dist, min_dist_idx, pos_key, dictionary, error] = \
            self.test_block.compare_position_code(
                self.test_block.position_code_swap_dict.copy(),
                window,
                0)
        self.assertEqual(objective_min_dist, min_dist)
        self.assertEqual(objective_min_dist_idx, min_dist_idx)
        self.assertEqual(objective_pos_key, pos_key)
        self.assertEqual(objective_dictionary, dictionary)
        self.assertEqual(objective_error, error)
        self.tearDown()

        self.setUp_Block()
        objective_min_dist = 0
        objective_min_dist_idx = 6
        objective_error = False
        objective_pos_key = (0, +1,-1, 0, 0, 0,+1,-1, 0, 0, 0, 0, 0, 0, 0,-1,
                             0, +2, 0,-2, 0,+2, 0,-2, 0,+1, 0, 0, 0, 0, 0, 0)
        objective_dictionary = self.test_block.position_code_swap_dict.copy()
        window = [0, 0, 0, 0, 0, 0,
                  0,+1,-1, 0, 0, 0,+1,-1, 0, 0, 0, 0, 0, 0, 0,-1,
                  0,+2, 0,-2, 0,+2, 0,-2, 0,+1, 0, 0, 0, 0, 0, 0]
        [min_dist, min_dist_idx, pos_key, dictionary, error] = \
            self.test_block.compare_position_code(
                self.test_block.position_code_swap_dict.copy(),
                window,
                0)

        self.assertEqual(objective_min_dist, min_dist)
        self.assertEqual(objective_min_dist_idx, min_dist_idx)
        self.assertEqual(objective_pos_key, pos_key)
        self.assertEqual(objective_dictionary, dictionary)
        self.assertEqual(objective_error, error)
        self.tearDown()

        self.setUp_Block()
        objective_min_dist = 0
        objective_min_dist_idx = 0
        objective_pos_key = (+1, 0,-2, 0,+2,-1,-1,+1,+1,-1,-1,+1, 0,+1, 0,-2,
                             +1, 0, 0,+1,-2, 0,+1, 0,+1,-1,-1,+1, 0, 0, 0, 0)
        objective_dictionary = self.test_block.position_code_swap_dict.copy()
        objective_error = False
        window = [+1, 0,-2, 0,+2,-1,-1,+1,+1,-1,-1,+1, 0,+1, 0,-2,
                  +1, 0, 0,+1,-2, 0,+1, 0,+1,-1,-1,+1, 0, 0, 0, 0]
        [min_dist, min_dist_idx, pos_key, dictionary, error] = \
            self.test_block.compare_position_code(
                self.test_block.position_code_swap_dict.copy(),
                window,
                0)

        self.assertEqual(objective_min_dist, min_dist)
        self.assertEqual(objective_min_dist_idx, min_dist_idx)
        self.assertEqual(objective_pos_key, pos_key)
        self.assertEqual(objective_dictionary, dictionary)
        self.assertEqual(objective_error, error)
        self.tearDown()

        self.setUp_Block()
        objective_min_dist = 0
        objective_min_dist_idx = 0
        objective_pos_key = (+1, 0,-1,-1,+1, 0, 0,+1,-2,+1, 0,-1,+2, 0,-2,+1,
                             0,-1,+2, 0,-2,+1, 0, 0, 1,-2, 0,+1, 0, 0, 0, 0)
        objective_dictionary = self.test_block.position_code_swap_dict.copy()
        objective_error = False
        window = [+1, 0,-1,-1,+1, 0, 0,+1,-2,+1, 0,-1,+2, 0,-2,+1,
                  0,-1,+2, 0,-2,+1, 0, 0, 1,-2, 0,+1, 0, 0, 0, 0]
        [min_dist, min_dist_idx, pos_key, dictionary, error] = \
            self.test_block.compare_position_code(
                self.test_block.position_code_swap_dict.copy(),
                window,
                0)

        self.assertEqual(objective_min_dist, min_dist)
        self.assertEqual(objective_min_dist_idx, min_dist_idx)
        self.assertEqual(objective_pos_key, pos_key)
        self.assertEqual(objective_dictionary, dictionary)
        self.assertEqual(objective_error, error)
        self.tearDown()

        self.setUp_Block()
        objective_min_dist = 11.313708498984761
        objective_min_dist_idx = 0
        objective_pos_key = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        objective_dictionary = self.test_block.position_code_swap_dict.copy()
        objective_error = True
        window = [+2,-2,+2,-2,+2,-2,+2,-2,+2,-2,+2,-2,+2,-2,+2,-2,
                  +2,-2,+2,-2,+2,-2,+2,-2,+2,-2,+2,-2,+2,-2,+2,-2]
        [min_dist, min_dist_idx, pos_key, dictionary, error] = \
            self.test_block.compare_position_code(
                self.test_block.position_code_swap_dict.copy(),
                window,
                0)

        self.assertEqual(objective_min_dist, min_dist)
        self.assertEqual(objective_min_dist_idx, min_dist_idx)
        self.assertEqual(objective_pos_key, pos_key)
        self.assertEqual(objective_dictionary, dictionary)
        self.assertEqual(objective_error, error)
        self.tearDown()

    def test_gr_compare_symbol_code(self):
        self.setUp_Block()

        objective = (1, -1, -1, 1, 0, 0, 0, 0)
        objective_error = False
        window = [1, -1, -1, 1, 0, 0, 0, 0]
        [result, error] = self.test_block.compare_symbol_code(
            self.test_block.symbol_code_swap_dict, window, 0)
        self.assertEqual(objective, result)
        self.assertEqual(objective_error, error)

        objective = (1, -1, -1, 1, 1, -1, -1, 1)
        objective_error = False
        window = [1, -1, -1, 1, 1, -1, -1, 1]
        [result, error] = self.test_block.compare_symbol_code(
            self.test_block.symbol_code_swap_dict, window, 0)
        self.assertEqual(objective, result)
        self.assertEqual(objective_error, error)

        objective = (0, 0, 0, 0, 0, 0, 0, 0)
        objective_error = False
        window = [0, 0, 0, 0, 0, 0, 0, 0]
        [result, error] = self.test_block.compare_symbol_code(
            self.test_block.symbol_code_swap_dict, window, 0)
        self.assertEqual(objective, result)
        self.assertEqual(objective_error, error)

        objective = (1, -1, -1, 1, 0, 0, 0, 0)
        objective_error = True
        window = [1, -2, 1, -1, 2, -1, 1, -1]
        [result, error] = self.test_block.compare_symbol_code(
            self.test_block.symbol_code_swap_dict, window, 0)
        self.assertEqual(objective, result)
        self.assertEqual(objective_error, error)

        objective = (1, -1, -1, 1, 0, 0, 0, 0)
        objective_error = True
        window = [0, 0, 0, 1, 2, 2, -2, -2]
        [result, error] = self.test_block.compare_symbol_code(
            self.test_block.symbol_code_swap_dict, window, 0)
        self.assertEqual(objective, result)
        self.assertEqual(objective_error, error)

        self.tearDown()


if __name__ == '__main__':
    gr_unittest.run(test_gr_Correlation.test_gr_handle_msg())
    gr_unittest.run(test_gr_Correlation.test_gr_prepare_window())
    gr_unittest.run(test_gr_Correlation.test_gr_rotate_dict())
    gr_unittest.run(test_gr_Correlation.test_gr_compare_position_code())
    gr_unittest.run(test_gr_Correlation.test_gr_compare_symbol_code())
