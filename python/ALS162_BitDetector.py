"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""

import numpy as np
from gnuradio import gr
import pmt


# the detector is initially out of sync
_in_sync = 0

# counted number of one samples for +1
_num_ones_p1 = 0
# counted number of one samples for -1
_num_ones_m1 = 0
# counted number of one samples for  0
_num_ones_z0 = 0
# counted number of one samples for +2
_num_ones_p2 = 0
# counted number of one samples for -2
_num_ones_m2 = 0

# counts number of samples after a zero- or
# one-symbol has been detected
_skip_count = 0
# determines how many samples shall be skipped
# after the detection of a zero- or one-symbol
_cur_skipframe = 50000
_cur_sec = 0


class blk(gr.sync_block):

    def __init__(self, scaling=8, sample_rate=192000,
                 tolerance=0.002, debug=False):
        gr.sync_block.__init__(
            self,
            name='Bit-Detector ALS162',
            in_sig=[np.float32, np.float32, np.float32,
                    np.float32, np.float32],
            out_sig=[np.float32]
        )

        self.scaling = scaling
        self.sample_rate = sample_rate
        self._tolerance = self.sample_rate/self.scaling*tolerance

        # True: display status-tags
        self.debug = debug

        # messaging port
        self.message_port_register_out(pmt.intern('msg_out'))

        """
        values from slope signal computed by derivative FIR filter
        symbols are constructed by a sequence of clocked sub-frames
        Zero-Symbol:
        0, +1, -1, -1, +1, 0

        One-Symbol:
        0, +1, -1, -1, +1, +1, -1, -1, +1

        New-Minute-Symbol:
        1275 ms a sequence 0 values only
        """

        # each subframe lasts approx. 25ms
        self._subframe_lo = int(0.025 * self.sample_rate/self.scaling
                                - self._tolerance)
        self._subframe_hi = int(0.025 * self.sample_rate/self.scaling
                                + self._tolerance)

        # lasts roughly 1275 ms
        self._reinit_zero_lo = int(1.275*self.sample_rate/self.scaling
                                   - 4*self._tolerance)
        self._reinit_zero_hi = int(1.275*self.sample_rate/self.scaling
                                   + 4*self._tolerance)

        # after a successful zero or one-symbol has been detected
        # ignore the signal for almost the rest of the second
        self._skipframe_zero = int(0.8*self.sample_rate/self.scaling
                                   - self._tolerance)
        self._skipframe_one = int(0.7*self.sample_rate/self.scaling
                                  - self._tolerance)

        print("zero_reinit_length", (self._reinit_zero_hi
                                     + self._reinit_zero_lo)/2)
        print("subframe_length: ", (self._subframe_hi + self._subframe_lo)/2)
        print("skipframe_zero_length: ", self._skipframe_zero)
        print("skipframe_one_length: ", self._skipframe_one)
        print("tolerance_length: ", self._tolerance)

    def work(self, input_items, output_items):
        inp_p1 = input_items[0]     # +1
        inp_m1 = input_items[1]     # -1
        inp_z0 = input_items[2]     # 0
        inp_p2 = input_items[3]     # +2
        inp_m2 = input_items[4]     # -2

        out = output_items[0]

        out[:] = self.extract_bits(inp_p1, inp_m1, inp_z0, inp_p2, inp_m2)

        # forward input tagged signal
        return len(output_items[0])

    def clear_counters(self):
        global _num_ones_p1
        global _num_ones_m1
        global _num_ones_z0
        global _num_ones_p2
        global _num_ones_m2

        _num_ones_p1 = 0
        _num_ones_m1 = 0
        _num_ones_z0 = 0
        _num_ones_p2 = 0
        _num_ones_m2 = 0

        # _cur_sec = 0

    def extract_bits(self, inp_p1, inp_m1, inp_z0, inp_p2, inp_m2):
        global _in_sync
        global _skip_count
        global _cur_skipframe
        global _cur_sec

        global _num_ones_p1
        global _num_ones_m1
        global _num_ones_z0
        global _num_ones_p2
        global _num_ones_m2

        # -1 => represents no relevant output
        out = -np.ones(len(inp_p1))

        # iterate through all three (parallel) input streams concurrently
        for idx in range(len(inp_p1)):
            # get symbol values at same idx for each input stream
            ch_p1 = inp_p1[idx]
            ch_m1 = inp_m1[idx]
            ch_z0 = inp_z0[idx]
            ch_p2 = inp_p2[idx]
            ch_m2 = inp_m2[idx]

            if ch_z0 == 1:
                _num_ones_z0 += 1

            if _cur_sec > 59:
                _cur_sec = 0

            # to avoid an overflow of _skip_count
            # stop counting after given limit and hold the value
            if _skip_count < _cur_skipframe + 1:
                # after a zero or one has been detected
                # the next bit should not be detected earlier
                # than the duration of the skip frame
                # (slightly less than a second)
                _skip_count += 1

            else:
                _skip_count = _cur_skipframe + 15

                # increment current counters of ones per
                # input stream, correspondingly
                if ch_p1 == 1:
                    _num_ones_p1 += 1

                if ch_m1 == 1:
                    _num_ones_m1 += 1

                # any p2-symbol will trigger a de-sync
                if ch_p2 == 1:
                    _num_ones_p2 += 1
                    _in_sync = 0

                # any m2-symbol will trigger a de-sync
                if ch_m2 == 1:
                    _num_ones_m2 += 1
                    _in_sync = 0

                # 1st step of synchronization
                if _in_sync == 0:
                    if (_num_ones_z0 >= self._reinit_zero_lo and
                            _num_ones_z0 <= self._reinit_zero_hi):

                        self.clear_counters()

                        # marking detected new minute
                        key = pmt.intern("b")
                        value = pmt.intern("new minute")
                        self.add_item_tag(0,
                                          self.nitems_written(0) + idx,
                                          key,
                                          value)

                        # new minute-symbol for ALS162-decoder
                        self.message_port_pub(pmt.intern("msg_out"),
                                              pmt.intern("2"))

                        out[idx] = 3

                        _cur_sec = 0

                    if (ch_p1 == 1 and
                            _num_ones_z0 >= self._subframe_lo):
                        _in_sync = 1

                        self.clear_counters()
                        _num_ones_p1 = 1

                        if self.debug is True:
                            key = pmt.intern("s")
                            value = pmt.intern("1")
                            self.add_item_tag(0,
                                              self.nitems_written(0) + idx,
                                              key,
                                              value)

                    # do not (yet) synchronize
                    elif ch_p1 == 0:
                        _num_ones_p1 = 0
                        _num_ones_m1 = 0
                        # _num_ones_z0 = 0
                        _num_ones_p2 = 0
                        _num_ones_m2 = 0

                elif _in_sync == 1:
                    # detect end of subframe 2
                    if (ch_p1 == 0 and
                            (_num_ones_p1 >= self._subframe_lo and
                             _num_ones_p1 <= self._subframe_hi)):
                        _in_sync = 2

                        self.clear_counters()

                        if self.debug is True:
                            key = pmt.intern("s")
                            value = pmt.intern("2")
                            self.add_item_tag(0,
                                              self.nitems_written(0) + idx,
                                              key,
                                              value)

                    # out of sync
                    elif (ch_p1 == 0 and
                            (_num_ones_p1 < self._subframe_lo or
                             _num_ones_p1 > self._subframe_hi)):
                        _in_sync = 0

                        self.clear_counters()

                elif _in_sync == 2:
                    # detect end of subframe 3
                    if (_num_ones_m1 >= 2*self._subframe_lo and
                            _num_ones_m1 <= 2*self._subframe_hi):
                        _in_sync = 3

                        self.clear_counters()

                        if self.debug is True:
                            key = pmt.intern("s")
                            value = pmt.intern("3")
                            self.add_item_tag(0,
                                              self.nitems_written(0) + idx,
                                              key,
                                              value)

                    # out of sync
                    elif _num_ones_m1 > 2*self._subframe_hi:
                        _in_sync = 0

                        self.clear_counters()

                    elif _num_ones_z0 >= 2*self._tolerance:
                        _in_sync = 0

                        self.clear_counters()

                elif _in_sync == 3:
                    # detect end of subframe 5
                    if (_num_ones_p1 > self._subframe_lo and
                            _num_ones_p1 < self._subframe_hi and ch_p1 == 0):
                        _in_sync = 5

                        self.clear_counters()

                        if self.debug is True:
                            key = pmt.intern("s")
                            value = pmt.intern("5")
                            self.add_item_tag(0,
                                              self.nitems_written(0) + idx,
                                              key,
                                              value)

                    # detect end of subframe 6
                    if (_num_ones_p1 >= 2*self._subframe_lo and
                            _num_ones_p1 <= 2*self._subframe_hi):
                        _in_sync = 6

                        self.clear_counters()

                        if self.debug is True:
                            key = pmt.intern("s")
                            value = pmt.intern("6")
                            self.add_item_tag(0,
                                              self.nitems_written(0) + idx,
                                              key,
                                              value)

                    # out of sync
                    elif _num_ones_p1 > 2*self._subframe_hi:
                        _in_sync = 0

                        self.clear_counters()

                    elif _num_ones_z0 > 2*self._tolerance:
                        _in_sync = 0

                        self.clear_counters()

                elif _in_sync == 5:
                    # detect subframe 6
                    if (_num_ones_z0 >= 1*self._subframe_lo and
                            _skip_count >= _cur_skipframe):
                        _in_sync = 0

                        self.clear_counters()

                        # marking detected zero-symbol
                        key = pmt.intern("b")
                        value = pmt.intern("0")
                        self.add_item_tag(0,
                                          self.nitems_written(0) + idx,
                                          key,
                                          value)

                        # successfully detected a zero symbol
                        # print("Sec: ", _cur_sec)
                        self.message_port_pub(pmt.intern("msg_out"),
                                              pmt.intern("0"))
                        out[idx] = 1

                        _cur_sec += 1

                        # reset skip counter
                        _skip_count = 0
                        _cur_skipframe = self._skipframe_zero

                    elif _num_ones_p1 >= 2*self._tolerance:
                        _in_sync = 0

                        self.clear_counters()

                elif _in_sync == 6:
                    # detect end of subframe 7
                    if (_num_ones_m1 >= 2*self._subframe_lo and
                            _num_ones_m1 <= 2*self._subframe_hi):
                        _in_sync = 7

                        self.clear_counters()

                        if self.debug is True:
                            key = pmt.intern("s")
                            value = pmt.intern("7")
                            self.add_item_tag(0,
                                              self.nitems_written(0) + idx,
                                              key,
                                              value)

                    # out of sync
                    elif (_num_ones_z0 > self._subframe_hi):
                        _in_sync = 0

                        self.clear_counters()

                elif _in_sync == 7:
                    if (_num_ones_p1 >= self._subframe_lo and
                            _num_ones_p1 <= self._subframe_hi and
                            _skip_count >= _cur_skipframe):
                        _in_sync = 0

                        self.clear_counters()

                        # marking detected zero-symbol
                        key = pmt.intern("b")
                        value = pmt.intern("1")
                        self.add_item_tag(0,
                                          self.nitems_written(0) + idx,
                                          key,
                                          value)

                        # successfully detected a one symbol
                        # print("Sec: ", _cur_sec)
                        self.message_port_pub(pmt.intern("msg_out"),
                                              pmt.intern("1"))
                        out[idx] = 2

                        _cur_sec += 1

                        # reset skip counter
                        _skip_count = 0
                        _cur_skipframe = self._skipframe_one

                    elif _num_ones_z0 >= 2*self._tolerance:
                        _in_sync = 0

                        self.clear_counters()

        return out
