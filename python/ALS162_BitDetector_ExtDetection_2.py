
import numpy as np
from gnuradio import gr
import pmt


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

# This alternative detector can operate on a single input stream
# of all 5 symbols (+2,+1, 0,-1,-2) combined.
class blk(gr.sync_block):

    def __init__(self, sample_rate=24000, tolerance=0.003):

        gr.sync_block.__init__(
            self,
            name='ALS162\nSymbol Detector 2',
            in_sig=[np.float32],
            out_sig=[np.float32]
        )

        self.message_port_register_out(pmt.intern('msg_out'))

        self.sample_rate = sample_rate
        self._tolerance = self.sample_rate*tolerance

        # each subframe lasts approx. 25ms
        self._subframe = int(0.025 * self.sample_rate)
        self._subframe_lo = self._subframe - self._tolerance
        self._subframe_lo2 = self._subframe - self._tolerance*3.0

        print("subframe_lo: ", self._subframe_lo)
        print("subframe_lo2: ", self._subframe_lo2)
        print("tolerance_length: ", self._tolerance)

        # NOTE: Frequently streaming lots of very short messages
        # within extremely short time frames may lead to occasional
        # message loss and hence to subsequent decoding errors.
        # The message queue simply stores multiple successive symbols.
        # Once the queue is full, concatenated message of the stored
        # symbols is send.
        self.queue_len = 20
        self.queue = gr.msg_queue(self.queue_len)

    def work(self, input_items, output_items):
        inp = input_items[0]

        output_items[0][:] = self.extract_bits(inp)

        # transmit tagged stream
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

    def send_msg(self, val, num):
        # handles both the message ouput queue
        # and the message transmission
        _msg = ""

        if num > 0:
            for i in range(0, num):
                _msg += val

            # convert python string to message
            msg1_in = gr.message_from_string(_msg)

            # insert message into queue
            self.queue.insert_tail(msg1_in)

        msg_list = [0]*self.queue_len

        # send a combination of all messages contained in queue
        if self.queue.full_p():
            for idx in range(0, self.queue_len):
                msg_list[idx] = self.queue.delete_head().\
                                     to_string().decode("utf-8")

            msg1_out = "".join(map(str, msg_list))
            self.message_port_pub(pmt.intern("msg_out"),
                                  pmt.intern(msg1_out))

    def extract_bits(self, inp):
        global _num_ones_p1
        global _num_ones_m1
        global _num_ones_z0
        global _num_ones_p2
        global _num_ones_m2

        out = np.zeros(len(inp))

        # iterate through all five (parallel) input streams concurrently
        for idx in range(len(inp)):
            # get symbol value at index for input stream
            ch = inp[idx]

            # increment current counters of ones per
            # input stream, correspondingly
            if ch == 1:
                _num_ones_p1 += 1

            if ch == -1:
                _num_ones_m1 += 1

            if ch == 2:
                _num_ones_p2 += 1

            if ch == -2:
                _num_ones_m2 += 1

            if ch == 0:
                _num_ones_z0 += 1

            # detect symbols (+/-2, +-1, 0)
            # within tolerated time-slice when
            # slope goes back to zero again
            if (ch != 2 and
                    _num_ones_p2 >= self._subframe_lo2):

                _num = round(_num_ones_p2/self._subframe)

                key = pmt.intern("c")
                value = pmt.intern(f"+2,{_num}")
                self.add_item_tag(0,
                                  self.nitems_written(0) + idx,
                                  key,
                                  value)
                out[idx] = 2

                self.send_msg(val="+2,", num=_num)
                self.clear_counters()

            if (ch != -2 and
                    _num_ones_m2 >= self._subframe_lo2):

                _num = round(_num_ones_m2/self._subframe)

                key = pmt.intern("c")
                value = pmt.intern(f"-2,{_num}")
                self.add_item_tag(0,
                                  self.nitems_written(0) + idx,
                                  key,
                                  value)
                out[idx] = -2
                self.send_msg(val="-2,", num=_num)

                self.clear_counters()

            if (ch != 1 and
                    _num_ones_p1 >= self._subframe_lo):

                _num = round(_num_ones_p1/self._subframe)

                key = pmt.intern("c")
                value = pmt.intern(f"+1,{_num}")
                self.add_item_tag(0,
                                  self.nitems_written(0) + idx,
                                  key,
                                  value)
                out[idx] = 1
                self.send_msg(val="+1,", num=_num)

                self.clear_counters()

            if (ch == 1 and
                    _num_ones_p1 >= self._subframe):

                # will be 1 anyway...
                # _num = round(_num_ones_z0/self._subframe)
                _num = 1

                key = pmt.intern("c")
                value = pmt.intern(f"+1,{_num}")
                self.add_item_tag(0,
                                  self.nitems_written(0) + idx,
                                  key,
                                  value)

                out[idx] = 1
                self.send_msg(val="+1,", num=_num)

                self.clear_counters()

            if (ch != -1 and
                    _num_ones_m1 >= self._subframe_lo):

                _num = round(_num_ones_m1/self._subframe)

                key = pmt.intern("c")
                value = pmt.intern(f"-1,{_num}")
                self.add_item_tag(0,
                                  self.nitems_written(0) + idx,
                                  key,
                                  value)

                out[idx] = -1
                self.send_msg(val="-1,", num=_num)

                self.clear_counters()

            if (ch == -1 and
                    _num_ones_m1 >= self._subframe):

                # will be 1 anyway...
                # _num = round(_num_ones_z0/self._subframe)
                _num = 1

                key = pmt.intern("c")
                value = pmt.intern(f"-1,{_num}")
                self.add_item_tag(0,
                                  self.nitems_written(0) + idx,
                                  key,
                                  value)

                out[idx] = -1
                self.send_msg(val="-1,", num=_num)

                self.clear_counters()

            if (ch != 0 and
                    _num_ones_z0 >= self._subframe_lo2):

                _num = round(_num_ones_z0/self._subframe)

                key = pmt.intern("c")
                value = pmt.intern(f"0,{_num}")
                self.add_item_tag(0,
                                  self.nitems_written(0) + idx,
                                  key,
                                  value)

                self.send_msg(val="0,", num=_num)

                self.clear_counters()

            # In case there is a longer stream of consecutive zeros
            # it is better to split the symbol stream into manageable
            # chunks. Otherwise, successive the decoder might get too
            # many zeros during the minute marker.
            if (ch == 0 and
                    _num_ones_z0 >= self._subframe):

                # will be 1 anyway...
                # _num = round(_num_ones_z0/self._subframe)
                _num = 1

                key = pmt.intern("c")
                value = pmt.intern(f"0,{_num}")
                self.add_item_tag(0,
                                  self.nitems_written(0) + idx,
                                  key,
                                  value)

                self.send_msg(val="0,", num=_num)

                self.clear_counters()

        return out
