# https://www.geeksforgeeks.org/python-rotate-dictionary-by-k/


from gnuradio import gr
import pmt
import numpy as np


# track the seconds
_counter = 0

# sliding window for selected messages
_msg_window = np.empty(shape=(1, 1))


class blk(gr.sync_block):

    def __init__(self):
        gr.sync_block.__init__(
            self,
            name='ALS162 Code\nSequence Correlator',
            in_sig=None,
            out_sig=None
        )

        self.message_port_register_out(pmt.intern('msg_out'))
        self.message_port_register_in(pmt.intern('msg_in'))
        self.set_msg_handler(pmt.intern('msg_in'), self.handle_msg)

        # error threshold for position code distance
        self.position_thres = 3

        # error threshold for symbol code distance
        self.symbol_thres = 1

        # NOTE: symbol 2 counts both as minute marker and as a zero value
        self.symbol_code_dict = {
            "0": (+1,-1,-1,+1, 0, 0, 0, 0),
            "1": (+1,-1,-1,+1,+1,-1,-1,+1),
            "2": ( 0, 0, 0, 0, 0, 0, 0, 0)
        }

        # table maps positions to codewords (reversing the dictionary above)
        self.symbol_code_swap_dict = \
            {v: k for k, v in self.symbol_code_dict.items()}

        # table maps codewords to positions
        # NOTE: do not put position "00" to the front as this would
        # lead to dropping position "59" each minute
        self.position_code_dict = {
            "01": ( 0,+1,-1, 0, 0, 0,+1,-1, 0, 0, 0, 0, 0, 0, 0,-1,
                    0,+2, 0,-2, 0,+2, 0,-2, 0,+1, 0, 0, 0, 0, 0, 0),
            "02": (+1, 0,-2, 0,+2,-1,-1,+1,+1,-1,-1,+1, 0,+1, 0,-2,
                   +1, 0, 0,+1,-2, 0,+1, 0,+1,-1,-1,+1, 0, 0, 0, 0),
            "03": (+1,-1, 0, 0,-1,+2, 0,-1,-1, 0,+2,-1,-1,+2, 0,-1,
                   -1, 0,+2,-1,-1,+2, 0,-1,-1, 0,+1, 0, 0, 0, 0, 0),
            "04": (+1,-1,-1,+1,+1, 0,-1,-1,+1, 0,-1,+1, 0, 0, 0,+1,
                    0,-2,+1,+1,-1,-1, 0,+1,+1,-1,-1,+1, 0, 0, 0, 0),
            "05": (+1,-1, 0,+1,-2, 0,+1, 0,+1, 0,-1,-1, 0,+2, 0,-1,
                   -1, 0,+1,+1,-1,-1,+2,-1,-1,+1, 0, 0, 0, 0, 0, 0),
            "06": (+1,-1,-1,+1,+1, 0,-1,-1, 0,+1, 0,+1, 0,-2, 0,+2,
                    0,-2,+1,+1,-1,-1, 0,+2,-1,-1,+1, 0, 0, 0, 0, 0),
            "07": ( 0, 0, 0, 0,+1, 0,-1, 0,-1, 0,+1,+1, 0,-1,-1,+1,
                    0, 0, 0,-1,+1,+1, 0,-1,-1, 0,+1, 0, 0, 0, 0, 0),
            "08": ( 0, 0,+1, 0,-1, 0, 0, 0, 0,-1, 0,+1, 0, 0, 0, 0,
                    0, 0, 0, 0, 0,+1,-1,-1,+2,-1,-1,+1, 0, 0, 0, 0),
            "09": (+1,-1, 0,+1,-2,+1, 0,-1,+1,+1,-1,-1,+1,+1, 0,-1,
                   -1, 0,+1,+1, 0,-1,-1, 0,+1, 0, 0, 0, 0, 0, 0, 0),
            "10": ( 0,+1, 0,-1,-1, 0,+1,+1, 0,-1,-1, 0,+2,-1,-1,+1,
                   +1, 0,-1,-1,+1,+1,-2, 0,+1, 0, 0, 0, 0, 0, 0, 0),
            "11": ( 0,+1, 0,-1,-1,+1,+1,-2,+1, 0,-1,+1, 0,+1,-1, 0,
                   +1,-1, 0,-1, 0,+2,-1, 0, 0,-1,+1, 0, 0, 0, 0, 0),
            "12": ( 0,+1, 0,-1, 0, 0,-1, 0,+2,-1,-1,+1,+1, 0,-1, 0,
                   -1, 0,+1, 0, 0, 0, 0, 0,+1,-1,-1,+1, 0, 0, 0, 0),
            "13": (+1,-1,-1,+2, 0,-1,-1, 0,+1,+1,-1, 0,+1,-2, 0,+1,
                   +1,-1,-1,+1, 0, 0,+1, 0,-1,-1, 0,+1, 0, 0, 0, 0),
            "14": (+1, 0,-2,+1,+1,-2,+1, 0,-1,+2, 0,-2, 0,+1,+1,-1,
                    0, 0,-1,+1,+1,-1,-1,+2, 0,-2, 0,+1, 0, 0, 0, 0),
            "15": ( 0,+1,-1,-1,+1,+1, 0,-1, 0,-1, 0,+2, 0,-1, 0,-1,
                    0,+2,-1, 0,+1,-2, 0,+2,-1,-1,+1, 0, 0, 0, 0, 0),
            "16": ( 0, 0,+1, 0,-2,+1,+1,-1, 0, 0,-1,+1, 0,-1,+1, 0,
                    0, 0, 0,+1, 0,-2,+1,+1,-1,-1, 0,+1, 0, 0, 0, 0),
            "17": (+1, 0,-2, 0,+2,-1, 0,+1,-1, 0, 0,-1,+1,+1,-1, 0,
                    0,-1,+1,+1,-2,+1,+1,-2, 0,+1, 0, 0, 0, 0, 0, 0),
            "18": (+1,-1, 0,+1,-2, 0,+2,-1, 0,+1,-1, 0, 0,-1, 0,+2,
                    0,-1, 0,-1,+1, 0,-1,+1, 0, 0, 0, 0, 0, 0, 0, 0),
            "19": (+1, 0,-1, 0,-1, 0,+1,+1,-1, 0,+1,-2, 0,+2,-1,-1,
                   +1, 0, 0,+1,-1,-1,+1, 0, 0, 0, 0, 0, 0, 0, 0, 0),
            "20": (+1,-1,-1,+1, 0,+1, 0,-2, 0,+1, 0,+1,-1, 0,+1,-2,
                    0,+2,-1, 0,+1,-2, 0,+2,-1,-1,+1, 0, 0, 0, 0, 0),
            "21": ( 0, 0,+1,-1,-1,+2,-1, 0,+1,-1, 0,-1, 0,+1,+1,-1,
                    0,+1,-2,+1,+1,-1, 0,-1, 0,+1, 0, 0, 0, 0, 0, 0),
            "22": (+1,-1,-1,+2,-1, 0, 0,-1,+1, 0,+1, 0,-1,-1, 0,+2,
                    0,-2, 0,+2, 0,-1, 0,-1,+1, 0,-1,+1, 0, 0, 0, 0),
            "23": ( 0, 0, 0, 0,+1, 0,-1, 0, 0, 0, 0, 0,-1,+1,+1,-2,
                   +1, 0, 0,+1,-1,-1, 0,+2, 0,-2, 0,+1, 0, 0, 0, 0),
            "24": ( 0, 0, 0, 0,+1,-1, 0, 0, 0,+1,-2,+1, 0,-1,+2, 0,
                   -1,-1,+1,+1,-2,+1,+1,-1, 0,-1, 0,+1, 0, 0, 0, 0),
            "25": (+1, 0,-2, 0,+1, 0, 0, 0,+1, 0,-2, 0,+2, 0,-1, 0,
                    0,-1,+1, 0, 0,+1,-2,+1,+1,-2, 0,+1, 0, 0, 0, 0),
            "26": (+1,-1, 0,+1,-2, 0,+2,-1, 0, 0, 0,+1,-2, 0,+2,-1,
                   -1,+1, 0,+1,-1, 0,+1,-1,-1, 0,+1, 0, 0, 0, 0, 0),
            "27": (+1, 0,-2, 0,+1,+1,-1,-1,+1, 0,+1, 0,-2, 0,+2, 0,
                   -1,-1,+1, 0,-1,+1,+1, 0,-2, 0,+1, 0, 0, 0, 0, 0),
            "28": (+1, 0,-1,-1,+1,+1,-2,+1, 0, 0,+1,-2, 0,+1, 0,+1,
                   -1,-1,+2, 0,-1, 0,-1,+1,+1,-2, 0,+1, 0, 0, 0, 0),
            "29": ( 0,+1,-1,-1,+2, 0,-2, 0,+2, 0,-1, 0, 0, 0, 0,-1,
                    0,+2,-1,-1,+1, 0,+1,-1,-1,+1, 0, 0, 0, 0, 0, 0),
            "30": (+1, 0,-2, 0,+2,-1,-1,+1, 0,+1, 0,-2, 0,+2, 0,-2,
                   +1, 0, 0,+1,-2, 0,+1,+1, 0,-2, 0,+1, 0, 0, 0, 0),
            "31": ( 0,+1,-1, 0,+1,-2, 0,+1,+1, 0,-2,+1,+1,-1, 0,-1,
                    0,+2, 0,-1,-1, 0,+2,-1,-1,+1, 0, 0, 0, 0, 0, 0),
            "32": ( 0, 0,+1, 0,-2,+1,+1,-1,-1, 0,+1,+1, 0,-2, 0,+1,
                    0, 0, 0,+1, 0,-2,+1, 0, 0, 0,-1,+1, 0, 0, 0, 0),
            "33": (+1, 0,-1, 0,-1,+1, 0,-1,+1, 0, 0,+1,-1, 0,+1,-1,
                    0, 0, 0,-1, 0,+1,+1, 0,-2, 0,+1, 0, 0, 0, 0, 0),
            "34": ( 0, 0, 0, 0,+1, 0,-2, 0,+2,-1,-1,+2, 0,-1, 0, 0,
                    0,-1,+1,+1,-1, 0, 0, 0,-1, 0,+1, 0, 0, 0, 0, 0),
            "35": ( 0, 0, 0,+1, 0,-1, 0, 0,-1, 0,+1, 0,+1, 0,-2,+1,
                    0, 0,+1,-1, 0,-1, 0,+1,+1,-1,-1,+1, 0, 0, 0, 0),
            "36": (+1,-1, 0,+1,-1, 0, 0, 0,-1, 0,+2,-1, 0, 0, 0, 0,
                   -1,+1, 0, 0, 0,+1,-1, 0, 0,-1,+1, 0, 0, 0, 0, 0),
            "37": (+1,-1,-1,+1, 0,+1,-1,-1,+1,+1,-1,-1,+1, 0,+1, 0,
                   -2,+1, 0, 0,+1,-1,-1, 0,+1, 0, 0, 0, 0, 0, 0, 0),
            "38": ( 0,+1, 0,-2,+1,+1,-1, 0, 0, 0,-1, 0,+2,-1,-1,+1,
                   +1, 0,-2, 0,+1,+1,-1,-1,+1, 0, 0, 0, 0, 0, 0, 0),
            "39": ( 0,+1, 0,-1,-1,+1,+1,-2, 0,+2,-1,-1,+1,+1,-1, 0,
                   +1,-1, 0,-1, 0,+2,-1,-1,+1, 0, 0, 0, 0, 0, 0, 0),
            "40": ( 0,+1, 0,-1, 0, 0,-1, 0,+2,-1,-1,+1,+1,-1,-1,+1,
                   +1, 0,-1, 0, 0, 0, 0, 0,-1, 0,+1, 0, 0, 0, 0, 0),
            "41": ( 0,+1, 0,-1,-1,+1,+1,-2,+1,+1,-1, 0,-1, 0,+2,-1,
                   -1,+1, 0,+1, 0,-2,+1, 0,-1,+1, 0, 0, 0, 0, 0, 0),
            "42": (+1, 0,-1,-1,+1, 0,-1,+2, 0,-1,-1,+1,+1,-2, 0,+2,
                   -1,-1,+2, 0,-2, 0,+2, 0,-1,-1, 0,+1, 0, 0, 0, 0),
            "43": (+1, 0,-1, 0,-1, 0,+2, 0,-2, 0,+2,-1, 0,+1,-1, 0,
                    0, 0, 0,-1,+1, 0,-1,+1,+1,-1,-1,+1, 0, 0, 0, 0),
            "44": ( 0,+1,-1,-1,+2, 0,-2, 0,+2,-1, 0, 0, 0, 0, 0,+1,
                   -2,+1, 0,-1,+1, 0, 0, 0,+1,-1,-1,+1, 0, 0, 0, 0),
            "45": ( 0,+1, 0,-1, 0, 0,-1,+1,+1,-2,+1, 0,-1,+2, 0,-2,
                    0,+1, 0, 0, 0, 0, 0,+1,-1,-1,+1, 0, 0, 0, 0, 0),
            "46": (+1,-1,-1,+1,+1,-1,-1,+2, 0,-2, 0,+2,-1,-1,+1,+1,
                    0,-2,+1,+1,-2, 0,+2, 0,-2, 0,+1, 0, 0, 0, 0, 0),
            "47": ( 0, 0,+1, 0,-2, 0,+1, 0,+1, 0,-2,+1, 0,-1,+2,-1,
                    0, 1,-1,-1,+1,+1,-2,+1,+1,-2, 0,+1, 0, 0, 0, 0),
            "48": (+1, 0,-1,-1,+1, 0, 0,+1,-2,+1, 0,-1,+2, 0,-2,+1,
                    0,-1,+2, 0,-2,+1, 0, 0, 1,-2, 0,+1, 0, 0, 0, 0),
            "49": (+1,-1,-1,+2,-1,-1,+2, 0,-2, 0,+2, 0,-1, 0, 0, 0,
                   -1,+1,+1,-2,+1, 0,-1,+1,+1,-1,-1,+1, 0, 0, 0, 0),
            "50": ( 0, 0,+1, 0,-2, 0,+1, 0,+1,-1, 0, 0, 0, 0, 0,+1,
                   -1, 0, 0,-1,+1,+1,-1, 0,-1, 0,+1, 0, 0, 0, 0, 0),
            "51": (+1,-1,-1,+1, 0, 0, 0,+1,-1, 0,+1,-1,-1, 0,+2, 0,
                   -2,+1, 0, 0, 0,-1,+1, 0, 0, 0, 0, 0, 0, 0, 0, 0),
            "52": (+1, 0,-1,-1,+1,+1,-1, 0, 0, 0, 0,-1,+1, 0,-1,+2,
                   -1,-1,+2, 0,-1,-1,+1,+1,-1,-1, 0,+1, 0, 0, 0, 0),
            "53": ( 0,+1, 0,-1,-1, 0,+2, 0,-2, 0,+1,+1,-1,-1,+1,+1,
                    0,-1, 0,-1,+1, 0,-1,+1,+1,-1,-1,+1, 0, 0, 0, 0),
            "54": (+1, 0,-1,-1, 0,+1,+1, 0,-2,+1, 0, 0, 0, 0, 0, 0,
                    0,-1,+2,-1, 0, 0, 0, 0,-1,+1, 0, 0, 0, 0, 0, 0),
            "55": ( 0, 0,+1,-1, 0,+1,-2, 0,+2,-1,-1,+2,-1, 0, 0, 0,
                    0,-1,+2, 0,-1, 0,-1,+1, 0,-1,+1, 0, 0, 0, 0, 0),
            "56": ( 0, 0, 0, 0, 0, 0, 0,+1,-1,-1,+2, 0,-2, 0,+1, 0,
                    0,+1,-1, 0, 0,-1,+2,-1, 0, 0,-1,+1, 0, 0, 0, 0),
            "57": ( 0, 0,+1, 0,-2,+1, 0, 0,+1,-1,-1,+1, 0, 0,+1,-2,
                   +1,+1,-1,-1, 0,+1, 0,+1, 0,-2, 0,+1, 0, 0, 0, 0),
            "58": (+1, 0,-1, 0,-1,+1, 0,-1,+2,-1,-1,+2,-1,-1,+2,-1,
                    0,+1,-1,-1, 0,+1, 0, 0,+1,-1,-1,+1, 0, 0, 0, 0),
            "59": (+1, 0,-2, 0,+2, 0,-2, 0,+2, 0,-2, 0,+2, 0,-2, 0,
                   +2, 0,-2, 0,+1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
            "00": ( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        }

        self.position_code_swap_dict = \
            {v: k for k, v in self.position_code_dict.items()}

    def prepare_window(self, msg):
        global _msg_window

        # message contains whole spread sequence of a received second
        msg = pmt.to_python(msg)

        # first put each string into an array (separated by comma)
        received_msg = msg.split(",")

        # truncate last element ("") from list
        received_msg = received_msg[:-1]

        # convert to numpy array
        np_recv_seq = np.array(received_msg)

        # turn each array element into an integer value
        np_recv_seq = np.asarray(np_recv_seq, dtype=np.int32)

        _msg_window = np.append(_msg_window, np_recv_seq)

    def rotate_dict(self, dictionary, K):
        # circular rotation of the dictionary entries
        keys = list(dictionary.keys())
        vals = list(dictionary.values())

        keys = keys[K:] + keys[:K]
        vals = vals[K:] + vals[:K]

        return dict(zip(keys, vals))

    def compare_position_code(self, dictionary, msg_window, first_offs=8):
        global _counter

        min_dist = 15
        min_dist_idx = 0
        pos_key = ( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

        for idx, key in enumerate(dictionary):
            # turn tuple into numpy array
            np_key = np.array(list(key))

            # there must be at least 8 chips offset before
            # that position codeword containing the time information
            # (symbol 0 or 1)!
            for offset in range(first_offs, first_offs + 40):
                # decision metric: compare window with current codeword
                # by the (Euclidean distance metric) 2-norm
                dist = np.linalg.norm(msg_window[offset:offset + 32] - np_key)

                # update current minimum
                if min_dist > dist:
                    min_dist = dist

                # check decision threshold for minimum
                if dist <= self.position_thres:
                    min_dist = dist
                    min_dist_idx = offset
                    break

            if min_dist <= self.position_thres:
                pos_key = key
                break

        # to save almost all iterations in the next run
        # NOTE: unclear if rotating the dict is actually
        # faster than simply iterating over all 60 keys
        # in the worst case (if this step is omitted)?
        shift_val = int(dictionary[pos_key], 10) - _counter
        dictionary = self.rotate_dict(dictionary, shift_val)

        _counter = int(dictionary[pos_key], 10)

        if min_dist > self.position_thres:
            print("error, dropped position symbol:", msg_window)
            pos_key = ( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

        return [min_dist, min_dist_idx, pos_key, dictionary]

    def compare_symbol_code(self, dictionary, symbol_window, first_offs=0):
        min_dist = 15
        symb_key = ( 1, -1, -1, 1, 0, 0, 0, 0)

        for key in dictionary:
            # turn tuple into numpy array
            np_key = np.array(list(key))

            # decision metric: compare window with current time-symbol-
            # codeword using the (Euclidean distance metric) 2-norm
            for offset in range(first_offs,
                                max(1, len(symbol_window) - len(np_key) + 1)):
                dist = np.linalg.norm(
                    symbol_window[offset:offset + 8] - np_key)

                # update current minimum
                if min_dist > dist:
                    min_dist = dist

                # check decision threshold for minimum
                if min_dist <= self.symbol_thres:
                    symb_key = key
                    break

            if min_dist <= self.symbol_thres:
                symb_key = key
                break

        if min_dist > self.symbol_thres:
            print("error, dropped time symbol:", symbol_window)
            symb_key = ( 1, -1, -1, 1, 0, 0, 0, 0)

        return symb_key

    def handle_msg(self, msg):
        global _msg_window

        self.prepare_window(msg)

        if len(_msg_window) >= 79:
            cur_window = _msg_window.copy()

            # find position-codeword in _msg_window
            [min_dist, min_dist_idx, pos_key,
                self.position_code_swap_dict] = \
                self.compare_position_code(
                dictionary=self.position_code_swap_dict,
                msg_window=_msg_window.copy(),
                first_offs=8)

            symbol_window = _msg_window.copy()

            # truncate codeword from front
            if min_dist < self.position_thres:
                _msg_window = _msg_window[min_dist_idx + len(pos_key):]

                # mask time-symbol-codeword in front of position-codeword
                symbol_window = symbol_window[min_dist_idx - 8:min_dist_idx]

                # detect time-symbol-codeword in symbol_window
                symb_key = self.compare_symbol_code(
                    dictionary=self.symbol_code_swap_dict,
                    symbol_window=symbol_window,
                    first_offs=0)

                symb_code = self.symbol_code_swap_dict[symb_key]
                pos_code = self.position_code_swap_dict[pos_key]

                msg1_out = f"{symb_code}, {pos_code}"
                self.message_port_pub(pmt.intern("msg_out"),
                                      pmt.intern(msg1_out))

            # try to decode the time-symbol-codeword,
            # even though decoding the position-codword has failed
            else:
                print("decoding error in current window:\n", cur_window)
                # mask time-symbol-codeword in front of position-codeword
                # symbol_window = symbol_window[min_dist_idx-8:min_dist_idx]
                # symbol_window = cur_window.copy()[:42]

                # detect time-symbol-codeword in symbol_window
                symb_key = self.compare_symbol_code(
                    dictionary=self.symbol_code_swap_dict,
                    symbol_window=symbol_window,
                    first_offs=0)

                symb_code = self.symbol_code_swap_dict[symb_key]
                pos_code = self.position_code_swap_dict[pos_key]

                msg1_out = f"{symb_code}, {pos_code}"
                self.message_port_pub(pmt.intern("msg_out"),
                                      pmt.intern(msg1_out))

                _msg_window = _msg_window[30:]
