
import sys
import unittest
from io import StringIO
import zmq
import pmt
import threading
import sys
sys.path.append('..')
from python import Class_DecodeALS162 as ALS162


class Test_Class_DecodeALS162(unittest.TestCase):

    def setUp(self):
        self.my_decoder = ALS162.Class_DecodeALS162()
        self.maxDiff = None

    def test_decode_BCD(self):
        # positive test
        bits = [0, 0, 0, 0]
        result = self.my_decoder.decode_BCD(bits, 4)
        objective = 0
        self.assertEqual(objective, result)

        # positive test
        bits = [0, 0, 0, 1]
        result = self.my_decoder.decode_BCD(bits, 4)
        objective = 1
        self.assertEqual(objective, result)

        # positive test
        bits = [1, 0, 0, 0]
        result = self.my_decoder.decode_BCD(bits, 4)
        objective = 8
        self.assertEqual(objective, result)

        # positive test
        bits = [1, 1, 1, 1]
        result = self.my_decoder.decode_BCD(bits, 4)
        objective = 15
        self.assertEqual(objective, result)

        # positive test
        bits = [0, 3, 1, 0]
        result = self.my_decoder.decode_BCD(bits, 4)
        objective = "?"
        self.assertEqual(objective, result)

        # positive test
        bits = [1, 1, 1]
        result = self.my_decoder.decode_BCD(bits, 3)
        objective = 7
        self.assertEqual(objective, result)

        # TBD negative test - too many bits
        # TBD negative test - too few bits

    def test_compute_num_errors(self):
        bitstream = [0]*6
        result = self.my_decoder.compute_num_errors(bitstream)
        objective = 0
        self.assertEqual(objective, result)

        bitstream = [1]*6
        result = self.my_decoder.compute_num_errors(bitstream)
        objective = 0
        self.assertEqual(objective, result)

        bitstream = [0]*2 + [3] + [0]*3
        result = self.my_decoder.compute_num_errors(bitstream)
        objective = 1
        self.assertEqual(objective, result)

        bitstream = [3]*2 + [0] * 4
        result = self.my_decoder.compute_num_errors(bitstream)
        objective = 2
        self.assertEqual(objective, result)

        bitstream = [3]*6
        result = self.my_decoder.compute_num_errors(bitstream)
        objective = 6
        self.assertEqual(objective, result)

    def test_compute_error_pos(self):
        bitstream = [0] * 6
        result = self.my_decoder.compute_error_pos(bitstream)
        objective = []
        self.assertEqual(objective, result)

        bitstream = [1] * 6
        result = self.my_decoder.compute_error_pos(bitstream)
        objective = []
        self.assertEqual(objective, result)

        bitstream = [0] * 2 + [3] + [0] * 3
        result = self.my_decoder.compute_error_pos(bitstream)
        objective = [2]
        self.assertEqual(objective, result)

        bitstream = [3] * 2 + [0] * 4
        result = self.my_decoder.compute_error_pos(bitstream)
        objective = [0, 1]
        self.assertEqual(objective, result)

        bitstream = [3] * 6
        result = self.my_decoder.compute_error_pos(bitstream)
        objective = [0, 1, 2, 3, 4, 5]
        self.assertEqual(objective, result)

    def test_single_error_correction(self):
        # no error
        bitstream = [0] * 6
        result = self.my_decoder.single_error_correction(bitstream)
        objective = [[0]*6, -1, -1]
        self.assertEqual(objective, result)

        # error is in first position
        bitstream = [3] + [0] * 5
        result = self.my_decoder.single_error_correction(bitstream)
        objective = [[0]*6, 0, 0]
        self.assertEqual(objective, result)

        # error is in second position
        bitstream = [0] + [3] + [0]*4
        result = self.my_decoder.single_error_correction(bitstream)
        objective = [[0]*6, 1, 0]
        self.assertEqual(objective, result)

        # error is in parity bit
        bitstream = [0]*5 + [3]
        result = self.my_decoder.single_error_correction(bitstream)
        objective = [[0]*6, 5, 0]
        self.assertEqual(objective, result)

        # two error are ignored (without error in parity bit]
        bitstream = [3]*2 + [0]*4
        result = self.my_decoder.single_error_correction(bitstream)
        objective = [[3]*2 + [0]*4, -1, -1]
        self.assertEqual(objective, result)

        # two error are ignored (with one error in parity bit]
        bitstream = [3] + [0]*4 + [3]
        result = self.my_decoder.single_error_correction(bitstream)
        objective = [[3] + [0]*4 + [3], -1, -1]
        self.assertEqual(objective, result)

    def test_decode_bitstream(self):
        # negative test - too many bits
        bitstream = [0]*61
        result = self.my_decoder.decode_bitstream(bitstream, 61)
        objective = "Decoding error\nReceived bits: 61\n"
        self.assertEqual(objective, result)

        # negative test - too few bits
        bitstream = [0]*59
        result = self.my_decoder.decode_bitstream(bitstream, 61)
        objective = "Decoding error\nReceived bits: 59\n"
        self.assertEqual(objective, result)

        # positive test - 20 is wrongly zero
        bitstream = [0]*60
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0.\n" + \
                    "0-02: No leap second.\n" + \
                    "03-06: Decoded & computed Hamming weights match for " + \
                    "bits 21-58: 0 == 0.0.\n" + \
                    "07-12: All zero.\n" + \
                    "16: No clock change\n" + \
                    "17-18: Error: Neither CET nor CEST set!\n" + \
                    "20: Is 0 instead of 1!\n" + \
                    "28: Even parity of minutes successful.\n" + \
                    "35: Even parity of hours successful.\n" + \
                    "21-27 & 29-34: Time: 00:00h.\n" + \
                    "Error: Day is 00!\n" + \
                    "Error: Month is 00!\n" + \
                    "36-41 & 45-57: Date: ??.??.00.\n" + \
                    "42-44: Weekday: Sunday.\n" + \
                    "58: Parity of date and weekdays successful.\n"
        self.assertEqual(objective, result)

        # positive test - start bit is wrongly 1
        bitstream = [1] + [0]*59
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 1 instead of 0!\n" + \
                    "0-02: No leap second.\n" + \
                    "03-06: Decoded & computed Hamming weights match for " + \
                    "bits 21-58: 0 == 0.0.\n" + \
                    "07-12: All zero.\n" + \
                    "16: No clock change\n" + \
                    "17-18: Error: Neither CET nor CEST set!\n" + \
                    "20: Is 0 instead of 1!\n" + \
                    "28: Even parity of minutes successful.\n" + \
                    "35: Even parity of hours successful.\n" + \
                    "21-27 & 29-34: Time: 00:00h.\n" + \
                    "Error: Day is 00!\n" + \
                    "Error: Month is 00!\n" + \
                    "36-41 & 45-57: Date: ??.??.00.\n" + \
                    "42-44: Weekday: Sunday.\n" + \
                    "58: Parity of date and weekdays successful.\n"
        self.assertEqual(objective, result)

        # positive test - positive leap second
        bitstream = [0] + [1] + [0] * 58
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0.\n" + \
                    "01: Positive leap second warning.\n" + \
                    "03-06: Decoded & computed Hamming weights match for " + \
                    "bits 21-58: 0 == 0.0.\n" + \
                    "07-12: All zero.\n" + \
                    "16: No clock change\n" + \
                    "17-18: Error: Neither CET nor CEST set!\n" + \
                    "20: Is 0 instead of 1!\n" + \
                    "28: Even parity of minutes successful.\n" + \
                    "35: Even parity of hours successful.\n" + \
                    "21-27 & 29-34: Time: 00:00h.\n" + \
                    "Error: Day is 00!\n" + \
                    "Error: Month is 00!\n" + \
                    "36-41 & 45-57: Date: ??.??.00.\n" + \
                    "42-44: Weekday: Sunday.\n" + \
                    "58: Parity of date and weekdays successful.\n"
        self.assertEqual(objective, result)

        # positive test - negative leap second
        bitstream = [0]*2 + [1] + [0] * 57
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0.\n" + \
                    "02: Negative leap second warning.\n" + \
                    "03-06: Decoded & computed Hamming weights match for " + \
                    "bits 21-58: 0 == 0.0.\n" + \
                    "07-12: All zero.\n" + \
                    "16: No clock change\n" + \
                    "17-18: Error: Neither CET nor CEST set!\n" + \
                    "20: Is 0 instead of 1!\n" + \
                    "28: Even parity of minutes successful.\n" + \
                    "35: Even parity of hours successful.\n" + \
                    "21-27 & 29-34: Time: 00:00h.\n" + \
                    "Error: Day is 00!\n" + \
                    "Error: Month is 00!\n" + \
                    "36-41 & 45-57: Date: ??.??.00.\n" + \
                    "42-44: Weekday: Sunday.\n" + \
                    "58: Parity of date and weekdays successful.\n"
        self.assertEqual(objective, result)

        # positive test - both leap seconds error
        bitstream = [0] + [1]*2 + [0] * 57
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0.\n" + \
                    "01-02: Error: Both leap seconds are set!\n" + \
                    "03-06: Decoded & computed Hamming weights match for " + \
                    "bits 21-58: 0 == 0.0.\n" + \
                    "07-12: All zero.\n" + \
                    "16: No clock change\n" + \
                    "17-18: Error: Neither CET nor CEST set!\n" + \
                    "20: Is 0 instead of 1!\n" + \
                    "28: Even parity of minutes successful.\n" + \
                    "35: Even parity of hours successful.\n" + \
                    "21-27 & 29-34: Time: 00:00h.\n" + \
                    "Error: Day is 00!\n" + \
                    "Error: Month is 00!\n" + \
                    "36-41 & 45-57: Date: ??.??.00.\n" + \
                    "42-44: Weekday: Sunday.\n" + \
                    "58: Parity of date and weekdays successful.\n"
        self.assertEqual(objective, result)

        # positive test - error in leap seconds
        bitstream = [0] + [3] * 2 + [0] * 57
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0.\n" + \
                    "01-02: Error: Leap second is ?.\n" + \
                    "03-06: Decoded & computed Hamming weights match for " + \
                    "bits 21-58: 0 == 0.0.\n" + \
                    "07-12: All zero.\n" + \
                    "16: No clock change\n" + \
                    "17-18: Error: Neither CET nor CEST set!\n" + \
                    "20: Is 0 instead of 1!\n" + \
                    "28: Even parity of minutes successful.\n" + \
                    "35: Even parity of hours successful.\n" + \
                    "21-27 & 29-34: Time: 00:00h.\n" + \
                    "Error: Day is 00!\n" + \
                    "Error: Month is 00!\n" + \
                    "36-41 & 45-57: Date: ??.??.00.\n" + \
                    "42-44: Weekday: Sunday.\n" + \
                    "58: Parity of date and weekdays successful.\n" + \
                    "# Bit errors: 2 => at positions: [1, 2].\n"
        self.assertEqual(objective, result)

        # positive test - a bit in 07-12 is wrongly 1
        bitstream = [0] + 6*[0] + 1*[1] + [0]*52
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0.\n" + \
                    "0-02: No leap second.\n" + \
                    "03-06: Decoded & computed Hamming weights match for " + \
                    "bits 21-58: 0 == 0.0.\n" + \
                    "07-12: At least one bit is 1 instead of 0!\n" + \
                    "16: No clock change\n" + \
                    "17-18: Error: Neither CET nor CEST set!\n" + \
                    "20: Is 0 instead of 1!\n" + \
                    "28: Even parity of minutes successful.\n" + \
                    "35: Even parity of hours successful.\n" + \
                    "21-27 & 29-34: Time: 00:00h.\n" + \
                    "Error: Day is 00!\n" + \
                    "Error: Month is 00!\n" + \
                    "36-41 & 45-57: Date: ??.??.00.\n" + \
                    "42-44: Weekday: Sunday.\n" + \
                    "58: Parity of date and weekdays successful.\n"
        self.assertEqual(objective, result)

        # positive test - following day is a holiday
        bitstream = [0] + 6*[0] + 6*[0] + [1] + [0]*47
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0.\n" + \
                    "0-02: No leap second.\n" + \
                    "03-06: Decoded & computed Hamming weights match for " + \
                    "bits 21-58: 0 == 0.0.\n" + \
                    "07-12: All zero.\n" + \
                    "13: The following day is a holiday.\n" + \
                    "16: No clock change\n" + \
                    "17-18: Error: Neither CET nor CEST set!\n" + \
                    "20: Is 0 instead of 1!\n" + \
                    "28: Even parity of minutes successful.\n" + \
                    "35: Even parity of hours successful.\n" + \
                    "21-27 & 29-34: Time: 00:00h.\n" + \
                    "Error: Day is 00!\n" + \
                    "Error: Month is 00!\n" + \
                    "36-41 & 45-57: Date: ??.??.00.\n" + \
                    "42-44: Weekday: Sunday.\n" + \
                    "58: Parity of date and weekdays successful.\n"
        self.assertEqual(objective, result)

        # positive test - current day is a holiday
        bitstream = [0] + 6*[0] + 7*[0] + [1] + [0]*46
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0.\n" + \
                    "0-02: No leap second.\n" + \
                    "03-06: Decoded & computed Hamming weights match for " + \
                    "bits 21-58: 0 == 0.0.\n" + \
                    "07-12: All zero.\n" + \
                    "14: The current day is a holiday.\n" + \
                    "16: No clock change\n" + \
                    "17-18: Error: Neither CET nor CEST set!\n" + \
                    "20: Is 0 instead of 1!\n" + \
                    "28: Even parity of minutes successful.\n" + \
                    "35: Even parity of hours successful.\n" + \
                    "21-27 & 29-34: Time: 00:00h.\n" + \
                    "Error: Day is 00!\n" + \
                    "Error: Month is 00!\n" + \
                    "36-41 & 45-57: Date: ??.??.00.\n" + \
                    "42-44: Weekday: Sunday.\n" + \
                    "58: Parity of date and weekdays successful.\n"
        self.assertEqual(objective, result)

        # positive test - clock change
        bitstream = [0] + 6*[0] + 9*[0] + [1] + [0]*44
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0.\n" + \
                    "0-02: No leap second.\n" + \
                    "03-06: Decoded & computed Hamming weights match for " + \
                    "bits 21-58: 0 == 0.0.\n" + \
                    "07-12: All zero.\n" + \
                    "16: Clock change\n" + \
                    "17-18: Error: Neither CET nor CEST set!\n" + \
                    "20: Is 0 instead of 1!\n" + \
                    "28: Even parity of minutes successful.\n" + \
                    "35: Even parity of hours successful.\n" + \
                    "21-27 & 29-34: Time: 00:00h.\n" + \
                    "Error: Day is 00!\n" + \
                    "Error: Month is 00!\n" + \
                    "36-41 & 45-57: Date: ??.??.00.\n" + \
                    "42-44: Weekday: Sunday.\n" + \
                    "58: Parity of date and weekdays successful.\n"
        self.assertEqual(objective, result)

        # positive test - summer time
        bitstream = [0] + 6*[0] + 10*[0] + [1] + [0]*43
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0.\n" + \
                    "0-02: No leap second.\n" + \
                    "03-06: Decoded & computed Hamming weights match for " + \
                    "bits 21-58: 0 == 0.0.\n" + \
                    "07-12: All zero.\n" + \
                    "16: No clock change\n" + \
                    "17-18: CEST - summer time.\n" + \
                    "20: Is 0 instead of 1!\n" + \
                    "28: Even parity of minutes successful.\n" + \
                    "35: Even parity of hours successful.\n" + \
                    "21-27 & 29-34: Time: 00:00h.\n" + \
                    "Error: Day is 00!\n" + \
                    "Error: Month is 00!\n" + \
                    "36-41 & 45-57: Date: ??.??.00.\n" + \
                    "42-44: Weekday: Sunday.\n" + \
                    "58: Parity of date and weekdays successful.\n"
        self.assertEqual(objective, result)

        # positive test - winter time
        bitstream = [0] + 6*[0] + 11*[0] + [1] + [0]*42
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0.\n" + \
                    "0-02: No leap second.\n" + \
                    "03-06: Decoded & computed Hamming weights match for " + \
                    "bits 21-58: 0 == 0.0.\n" + \
                    "07-12: All zero.\n" + \
                    "16: No clock change\n" + \
                    "17-18: CET - winter time.\n" + \
                    "20: Is 0 instead of 1!\n" + \
                    "28: Even parity of minutes successful.\n" + \
                    "35: Even parity of hours successful.\n" + \
                    "21-27 & 29-34: Time: 00:00h.\n" + \
                    "Error: Day is 00!\n" + \
                    "Error: Month is 00!\n" + \
                    "36-41 & 45-57: Date: ??.??.00.\n" + \
                    "42-44: Weekday: Sunday.\n" + \
                    "58: Parity of date and weekdays successful.\n"
        self.assertEqual(objective, result)

        # positive test - bit 19 is wrongly set to 1
        bitstream = [0] + 6*[0] + 12*[0] + [1] + [0]*41
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0.\n" + \
                    "0-02: No leap second.\n" + \
                    "03-06: Decoded & computed Hamming weights match for " + \
                    "bits 21-58: 0 == 0.0.\n" + \
                    "07-12: All zero.\n" + \
                    "16: No clock change\n" + \
                    "17-18: Error: Neither CET nor CEST set!\n" + \
                    "19: Is 1 instead of 0!\n" + \
                    "20: Is 0 instead of 1!\n" + \
                    "28: Even parity of minutes successful.\n" + \
                    "35: Even parity of hours successful.\n" + \
                    "21-27 & 29-34: Time: 00:00h.\n" + \
                    "Error: Day is 00!\n" + \
                    "Error: Month is 00!\n" + \
                    "36-41 & 45-57: Date: ??.??.00.\n" + \
                    "42-44: Weekday: Sunday.\n" + \
                    "58: Parity of date and weekdays successful.\n"
        self.assertEqual(objective, result)

        # positive test - bit 20 is wrongly set to 1
        bitstream = [0] + 6*[0] + 13*[0] + [1] + [0]*40
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0.\n" + \
                    "0-02: No leap second.\n" + \
                    "03-06: Decoded & computed Hamming weights match for " + \
                    "bits 21-58: 0 == 0.0.\n" + \
                    "07-12: All zero.\n" + \
                    "16: No clock change\n" + \
                    "17-18: Error: Neither CET nor CEST set!\n" + \
                    "20: Begin of time information.\n" + \
                    "28: Even parity of minutes successful.\n" + \
                    "35: Even parity of hours successful.\n" + \
                    "21-27 & 29-34: Time: 00:00h.\n" + \
                    "Error: Day is 00!\n" + \
                    "Error: Month is 00!\n" + \
                    "36-41 & 45-57: Date: ??.??.00.\n" + \
                    "42-44: Weekday: Sunday.\n" + \
                    "58: Parity of date and weekdays successful.\n"
        self.assertEqual(objective, result)

        # positive test - valid date and time
        bitstream = [0] + 2*[0] + 4*[1] + 6*[0] + 3*[0] + [0,1,0] + [0] + \
                    [1] + [0,1,0,0,1,0,1] + [1] + [1,0,0,0,1,0] + [0] + \
                    [1,1,0,0,1,0] + [0,1,1] + [1,0,1,0,0] + \
                    [1,1,0,0,0,1,0,0] + [0]
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0.\n" + \
                    "0-02: No leap second.\n" + \
                    "03-06: Error: Decoded & computed Hamming weights " + \
                    "missmatch for bits 21-58: 30 != 16!\n" + \
                    "07-12: All zero.\n" + \
                    "16: No clock change\n" + \
                    "17-18: CEST - summer time.\n" + \
                    "20: Begin of time information.\n" + \
                    "28: Even parity of minutes successful.\n" + \
                    "35: Even parity of hours successful.\n" + \
                    "21-27 & 29-34: Time: 11:52h.\n" + \
                    "36-41 & 45-57: Date: 13.05.23.\n" + \
                    "42-44: Weekday: Saturday.\n" + \
                    "58: Parity of date and weekdays successful.\n"
        self.assertEqual(objective, result)

        # positive test - wrong parity at minutes
        bitstream = [0] + 2*[0] + 4*[1] + 6*[0] + 3*[0] + [0,1,0] + [0] + \
                    [1] + [0,1,0,0,1,0,1] + [0] + [1,0,0,0,1,0] + [0] + \
                    [1,1,0,0,1,0] + [0,1,1] + [1,0,1,0,0] + \
                    [1,1,0,0,0,1,0,0] + [0]
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0.\n" + \
                    "0-02: No leap second.\n" + \
                    "03-06: Error: Decoded & computed Hamming weights " + \
                    "missmatch for bits 21-58: 30 != 15!\n" + \
                    "03-06: Error: Hamming weight for bits 21-58 is not " + \
                    "even!\n" + \
                    "07-12: All zero.\n" + \
                    "16: No clock change\n" + \
                    "17-18: CEST - summer time.\n" + \
                    "20: Begin of time information.\n" + \
                    "28: Even parity of minutes failed.\n" + \
                    "35: Even parity of hours successful.\n" + \
                    "21-27 & 29-34: Time: 11:52h.\n" + \
                    "36-41 & 45-57: Date: 13.05.23.\n" + \
                    "42-44: Weekday: Saturday.\n" + \
                    "58: Parity of date and weekdays successful.\n"
        self.assertEqual(objective, result)

        # positive test - wrong parity at hours
        bitstream = [0] + 2*[0] + 4*[1] + 6*[0] + 3*[0] + [0,1,0] + [0] + \
                    [1] + [0,1,0,0,1,0,1] + [1] + [1,0,0,0,1,0] + [1] + \
                    [1,1,0,0,1,0] + [0,1,1] + [1,0,1,0,0] + \
                    [1,1,0,0,0,1,0,0] + [0]
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0.\n" + \
                    "0-02: No leap second.\n" + \
                    "03-06: Error: Decoded & computed Hamming weights " + \
                    "missmatch for bits 21-58: 30 != 17!\n" + \
                    "03-06: Error: Hamming weight for bits 21-58 is " + \
                    "not even!\n" + \
                    "07-12: All zero.\n" + \
                    "16: No clock change\n" + \
                    "17-18: CEST - summer time.\n" + \
                    "20: Begin of time information.\n" + \
                    "28: Even parity of minutes successful.\n" + \
                    "35: Even parity of hours failed.\n" + \
                    "21-27 & 29-34: Time: 11:52h.\n" + \
                    "36-41 & 45-57: Date: 13.05.23.\n" + \
                    "42-44: Weekday: Saturday.\n" + \
                    "58: Parity of date and weekdays successful.\n"
        self.assertEqual(objective, result)

        # negative test - invalid hour 1*digit and 10*digit
        bitstream = [0] + 2*[0] + 4*[1] + 6*[0] + 3*[0] + [0,1,0] + [0] + \
                    [1] + [0,1,0,0,1,0,1] + [1] + [1,1,1,1,1,1] + [0] + \
                    [1,1,0,0,1,0] + [0,1,1] + [1,0,1,0,0] + \
                    [1,1,0,0,0,1,0,0] + [0]
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0.\n" + \
                    "0-02: No leap second.\n" + \
                    "03-06: Error: Decoded & computed Hamming weights " + \
                    "missmatch for bits 21-58: 30 != 20!\n" + \
                    "07-12: All zero.\n" + \
                    "16: No clock change\n" + \
                    "17-18: CEST - summer time.\n" + \
                    "20: Begin of time information.\n" + \
                    "28: Even parity of minutes successful.\n" + \
                    "35: Even parity of hours successful.\n" + \
                    "Error: 1*digit of hour is > 9!\n" + \
                    "Error: 10*digit of hour is > 2!\n" + \
                    "21-27 & 29-34: Time: ??:52h.\n" + \
                    "36-41 & 45-57: Date: 13.05.23.\n" + \
                    "42-44: Weekday: Saturday.\n" + \
                    "58: Parity of date and weekdays successful.\n"
        self.assertEqual(objective, result)

        # negative test - invalid hour 1*digit
        bitstream = [0] + 2*[0] + 4*[1] + 6*[0] + 3*[0] + [0,1,0] + [0] + \
                    [1] + [0,1,0,0,1,0,1] + [1] + [1,1,1,1,0,0] + [0] + \
                    [1,1,0,0,1,0] + [0,1,1] + [1,0,1,0,0] + \
                    [1,1,0,0,0,1,0,0] + [0]
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0.\n" + \
                    "0-02: No leap second.\n" + \
                    "03-06: Error: Decoded & computed Hamming weights " + \
                    "missmatch for bits 21-58: 30 != 18!\n" + \
                    "07-12: All zero.\n" + \
                    "16: No clock change\n" + \
                    "17-18: CEST - summer time.\n" + \
                    "20: Begin of time information.\n" + \
                    "28: Even parity of minutes successful.\n" + \
                    "35: Even parity of hours successful.\n" + \
                    "Error: 1*digit of hour is > 9!\n" + \
                    "21-27 & 29-34: Time: 0?:52h.\n" + \
                    "36-41 & 45-57: Date: 13.05.23.\n" + \
                    "42-44: Weekday: Saturday.\n" + \
                    "58: Parity of date and weekdays successful.\n"
        self.assertEqual(objective, result)

        # negative test - invalid hour 10*digit
        bitstream = [0] + 2*[0] + 4*[1] + 6*[0] + 3*[0] + [0,1,0] + [0] + \
                    [1] + [0,1,0,0,1,0,1] + [1] + [0,0,0,0,1,1] + [0] + \
                    [1,1,0,0,1,0] + [0,1,1] + [1,0,1,0,0] + \
                    [1,1,0,0,0,1,0,0] + [0]
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0.\n" + \
                    "0-02: No leap second.\n" + \
                    "03-06: Error: Decoded & computed Hamming weights " + \
                    "missmatch for bits 21-58: 30 != 16!\n" + \
                    "07-12: All zero.\n" + \
                    "16: No clock change\n" + \
                    "17-18: CEST - summer time.\n" + \
                    "20: Begin of time information.\n" + \
                    "28: Even parity of minutes successful.\n" + \
                    "35: Even parity of hours successful.\n" + \
                    "Error: 10*digit of hour is > 2!\n" + \
                    "21-27 & 29-34: Time: ?0:52h.\n" + \
                    "36-41 & 45-57: Date: 13.05.23.\n" + \
                    "42-44: Weekday: Saturday.\n" + \
                    "58: Parity of date and weekdays successful.\n"
        self.assertEqual(objective, result)

        # negative test - invalid hours above 23
        bitstream = [0] + 2*[0] + 4*[1] + 6*[0] + 3*[0] + [0,1,0] + [0] + \
                    [1] + [0,1,0,0,1,0,1] + [1] + [0,0,1,0,0,1] + [0] + \
                    [1,1,0,0,1,0] + [0,1,1] + [1,0,1,0,0] + \
                    [1,1,0,0,0,1,0,0] + [0]
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0.\n" + \
                    "0-02: No leap second.\n" + \
                    "03-06: Error: Decoded & computed Hamming weights " + \
                    "missmatch for bits 21-58: 30 != 16!\n" + \
                    "07-12: All zero.\n" + \
                    "16: No clock change\n" + \
                    "17-18: CEST - summer time.\n" + \
                    "20: Begin of time information.\n" + \
                    "28: Even parity of minutes successful.\n" + \
                    "35: Even parity of hours successful.\n" + \
                    "Error: Hours are greater than 23!\n" + \
                    "21-27 & 29-34: Time: ??:52h.\n" + \
                    "36-41 & 45-57: Date: 13.05.23.\n" + \
                    "42-44: Weekday: Saturday.\n" + \
                    "58: Parity of date and weekdays successful.\n"
        self.assertEqual(objective, result)

        # negative test: - invalid minute 1*digit
        bitstream = [0] + 2*[0] + 4*[1] + 6*[0] + 3*[0] + [0,1,0] + [0] + \
                    [1] + [1,1,1,1,0,0,0] + [0] + [0,0,0,0,0,0] + [0] + \
                    [1,1,0,0,1,0] + [0,1,1] + [1,0,1,0,0] + \
                    [1,1,0,0,0,1,0,0] + [0]
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0.\n" + \
                    "0-02: No leap second.\n" + \
                    "03-06: Error: Decoded & computed Hamming weights " + \
                    "missmatch for bits 21-58: 30 != 14!\n" + \
                    "07-12: All zero.\n" + \
                    "16: No clock change\n" + \
                    "17-18: CEST - summer time.\n" + \
                    "20: Begin of time information.\n" + \
                    "28: Even parity of minutes successful.\n" + \
                    "35: Even parity of hours successful.\n" + \
                    "Error: 1*digit of minute is > 9!\n" + \
                    "21-27 & 29-34: Time: 00:0?h.\n" + \
                    "36-41 & 45-57: Date: 13.05.23.\n" + \
                    "42-44: Weekday: Saturday.\n" + \
                    "58: Parity of date and weekdays successful.\n"
        self.assertEqual(objective, result)

        # negative test: - invalid minute 10*digit
        bitstream = [0] + 2*[0] + 4*[1] + 6*[0] + 3*[0] + [0,1,0] + [0] + \
                    [1] + [0,0,0,0,1,1,1] + [1] + [0,0,0,0,0,0] + [0] + \
                    [1,1,0,0,1,0] + [0,1,1] + [1,0,1,0,0] + \
                    [1,1,0,0,0,1,0,0] + [0]
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0.\n" + \
                    "0-02: No leap second.\n" + \
                    "03-06: Error: Decoded & computed Hamming weights " + \
                    "missmatch for bits 21-58: 30 != 14!\n" + \
                    "07-12: All zero.\n" + \
                    "16: No clock change\n" + \
                    "17-18: CEST - summer time.\n" + \
                    "20: Begin of time information.\n" + \
                    "28: Even parity of minutes successful.\n" + \
                    "35: Even parity of hours successful.\n" + \
                    "Error: 10*digit of minute is > 5!\n" + \
                    "21-27 & 29-34: Time: 00:?0h.\n" + \
                    "36-41 & 45-57: Date: 13.05.23.\n" + \
                    "42-44: Weekday: Saturday.\n" + \
                    "58: Parity of date and weekdays successful.\n"
        self.assertEqual(objective, result)

        # negative test: - invalid minute 10*digit
        bitstream = [0] + 2*[0] + 4*[1] + 6*[0] + 3*[0] + [0,1,0] + [0] + \
                    [1] + [0,1,0,1,1,1,1] + [1] + [0,0,0,0,0,0] + [0] + \
                    [1,1,0,0,1,0] + [0,1,1] + [1,0,1,0,0] + \
                    [1,1,0,0,0,1,0,0] + [0]
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0.\n" + \
                    "0-02: No leap second.\n" + \
                    "03-06: Error: Decoded & computed Hamming weights " + \
                    "missmatch for bits 21-58: 30 != 16!\n" + \
                    "07-12: All zero.\n" + \
                    "16: No clock change\n" + \
                    "17-18: CEST - summer time.\n" + \
                    "20: Begin of time information.\n" + \
                    "28: Even parity of minutes successful.\n" + \
                    "35: Even parity of hours successful.\n" + \
                    "Error: 10*digit of minute is > 5!\n" + \
                    "Error: 1*digit of minute is > 9!\n" + \
                    "21-27 & 29-34: Time: 00:??h.\n" + \
                    "36-41 & 45-57: Date: 13.05.23.\n" + \
                    "42-44: Weekday: Saturday.\n" + \
                    "58: Parity of date and weekdays successful.\n"
        self.assertEqual(objective, result)

        # negative test: - invalid weekday
        bitstream = [0] + 2*[0] + 4*[1] + 6*[0] + 3*[0] + [0,1,0] + [0] + \
                    [1] + [0,0,0,0,0,0,0] + [0] + [0,0,0,0,0,0] + [0] + \
                    [1,1,0,0,1,0] + [1,3,1] + [1,0,1,0,0] + \
                    [1,1,0,0,0,1,0,0] + [0]
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0.\n" + \
                    "0-02: No leap second.\n" + \
                    "03-06: Error: Decoded & computed Hamming weights " + \
                    "missmatch for bits 21-58: 30 != 10!\n" + \
                    "07-12: All zero.\n" + \
                    "16: No clock change\n" + \
                    "17-18: CEST - summer time.\n" + \
                    "20: Begin of time information.\n" + \
                    "28: Even parity of minutes successful.\n" + \
                    "35: Even parity of hours successful.\n" + \
                    "21-27 & 29-34: Time: 00:00h.\n" + \
                    "Corrected single error at 43.\n" + \
                    "36-41 & 45-57: Date: 13.05.23.\n" + \
                    "42-44: Weekday: Friday.\n" + \
                    "58: Parity of date and weekdays successful.\n"
        self.assertEqual(objective, result)

        # positive test: - parity of date and weekdays failed
        bitstream = [0] + 2*[0] + 4*[1] + 6*[0] + 3*[0] + [0,1,0] + [0] + \
                    [1] + [0,0,0,0,0,0,0] + [0] + [0,0,0,0,0,0] + [0] + \
                    [1,1,0,0,1,0] + [1,1,1] + [1,0,1,0,0] + \
                    [1,1,0,0,0,1,0,0] + [0]
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0.\n" + \
                    "0-02: No leap second.\n" + \
                    "03-06: Error: Decoded & computed Hamming weights " + \
                    "missmatch for bits 21-58: 30 != 11!\n" + \
                    "03-06: Error: Hamming weight for bits 21-58 " + \
                    "is not even!\n" + \
                    "07-12: All zero.\n" + \
                    "16: No clock change\n" + \
                    "17-18: CEST - summer time.\n" + \
                    "20: Begin of time information.\n" + \
                    "28: Even parity of minutes successful.\n" + \
                    "35: Even parity of hours successful.\n" + \
                    "21-27 & 29-34: Time: 00:00h.\n" + \
                    "36-41 & 45-57: Date: 13.05.23.\n" + \
                    "42-44: Weekday: Sunday.\n" + \
                    "58: Parity of date and weekdays failed.\n"
        self.assertEqual(objective, result)

        # negative test - error in hour value
        bitstream = [0] + 2*[0] + 4*[1] + 6*[0] + 3*[0] + [0,1,0] + [0] + \
                    [1] + [0,1,0,0,1,0,1] + [1] + [1,0,3,0,1,0] + [0] + \
                    [1,1,0,0,1,0] + [0,1,1] + [1,0,1,0,0] + \
                    [1,1,0,0,0,1,0,0] + [0]
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0.\n" + \
                    "0-02: No leap second.\n" + \
                    "03-06: Error: Decoded & computed Hamming weights " + \
                    "missmatch for bits 21-58: 30 != 16!\n" + \
                    "07-12: All zero.\n" + \
                    "16: No clock change\n" + \
                    "17-18: CEST - summer time.\n" + \
                    "20: Begin of time information.\n" + \
                    "28: Even parity of minutes successful.\n" + \
                    "Corrected single error at 31.\n" + \
                    "21-27 & 29-34: Time: 11:52h.\n" + \
                    "36-41 & 45-57: Date: 13.05.23.\n" + \
                    "42-44: Weekday: Saturday.\n" + \
                    "58: Parity of date and weekdays successful.\n"
        self.assertEqual(objective, result)

        # negative test - error in minute value
        bitstream = [0] + 2*[0] + 4*[1] + 6*[0] + 3*[0] + [0,1,0] + [0] + \
                    [1] + [0,1,3,0,1,0,1] + [1] + [1,0,1,0,1,0] + [1] + \
                    [1,1,0,0,1,0] + [0,1,1] + [1,0,1,0,0] + \
                    [1,1,0,0,0,1,0,0] + [0]
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0.\n" + \
                    "0-02: No leap second.\n" + \
                    "03-06: Error: Decoded & computed Hamming weights " + \
                    "missmatch for bits 21-58: 30 != 18!\n" + \
                    "07-12: All zero.\n" + \
                    "16: No clock change\n" + \
                    "17-18: CEST - summer time.\n" + \
                    "20: Begin of time information.\n" + \
                    "Corrected single error at 23.\n" + \
                    "35: Even parity of hours successful.\n" + \
                    "21-27 & 29-34: Time: 15:52h.\n" + \
                    "36-41 & 45-57: Date: 13.05.23.\n" + \
                    "42-44: Weekday: Saturday.\n" + \
                    "58: Parity of date and weekdays successful.\n"
        self.assertEqual(objective, result)

        # negative test - error in start-bit
        bitstream = [3] + 2*[0] + 4*[1] + 6*[0] + 3*[0] + [0,1,0] + [0] + \
                    [1] + [0,1,3,0,1,0,1] + [1] + [1,0,1,0,1,0] + [1] + \
                    [1,1,0,0,1,0] + [0,1,1] + [1,0,1,0,0] + \
                    [1,1,0,0,0,1,0,0] + [0]
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is ?.\n" + \
                    "0-02: No leap second.\n" + \
                    "03-06: Error: Decoded & computed Hamming weights " + \
                    "missmatch for bits 21-58: 30 != 18!\n" + \
                    "07-12: All zero.\n" + \
                    "16: No clock change\n" + \
                    "17-18: CEST - summer time.\n" + \
                    "20: Begin of time information.\n" + \
                    "Corrected single error at 23.\n" + \
                    "35: Even parity of hours successful.\n" + \
                    "21-27 & 29-34: Time: 15:52h.\n" + \
                    "36-41 & 45-57: Date: 13.05.23.\n" + \
                    "42-44: Weekday: Saturday.\n" + \
                    "58: Parity of date and weekdays successful.\n" + \
                    "# Bit errors: 1 => at positions: [0].\n"
        self.assertEqual(objective, result)

        # negative test: - invalid day 1*digit
        bitstream = [0] + 2*[0] + 4*[1] + 6*[0] + 3*[0] + [0,1,0] + [0] + \
                    [1] + [0,0,0,0,0,0,0] + [0] + [0,0,0,0,0,0] + [0] + \
                    [1,1,1,1,0,0] + [0,1,1] + [1,0,1,0,0] + \
                    [1,1,0,0,0,1,0,0] + [1]
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0.\n" + \
                    "0-02: No leap second.\n" + \
                    "03-06: Error: Decoded & computed Hamming weights " + \
                    "missmatch for bits 21-58: 30 != 12!\n" + \
                    "07-12: All zero.\n" + \
                    "16: No clock change\n" + \
                    "17-18: CEST - summer time.\n" + \
                    "20: Begin of time information.\n" + \
                    "28: Even parity of minutes successful.\n" + \
                    "35: Even parity of hours successful.\n" + \
                    "21-27 & 29-34: Time: 00:00h.\n" + \
                    "Error: 1*digit of day is > 9!\n" + \
                    "36-41 & 45-57: Date: 0?.05.23.\n" + \
                    "42-44: Weekday: Saturday.\n" + \
                    "58: Parity of date and weekdays successful.\n"
        self.assertEqual(objective, result)

        # negative test: - invalid day > 33
        bitstream = [0] + 2*[0] + 4*[1] + 6*[0] + 3*[0] + [0,1,0] + [0] + \
                    [1] + [0,0,0,0,0,0,0] + [0] + [0,0,0,0,0,0] + [0] + \
                    [1,1,1,1,1,1] + [0,1,1] + [1,0,1,0,0] + \
                    [1,1,0,0,0,1,0,0] + [1]
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0.\n" + \
                    "0-02: No leap second.\n" + \
                    "03-06: Error: Decoded & computed Hamming weights " + \
                    "missmatch for bits 21-58: 30 != 14!\n" + \
                    "07-12: All zero.\n" + \
                    "16: No clock change\n" + \
                    "17-18: CEST - summer time.\n" + \
                    "20: Begin of time information.\n" + \
                    "28: Even parity of minutes successful.\n" + \
                    "35: Even parity of hours successful.\n" + \
                    "21-27 & 29-34: Time: 00:00h.\n" + \
                    "Error: Day is > 31!\n" + \
                    "36-41 & 45-57: Date: ??.05.23.\n" + \
                    "42-44: Weekday: Saturday.\n" + \
                    "58: Parity of date and weekdays successful.\n"
        self.assertEqual(objective, result)

        # negative test: - invalid month 1*digit
        bitstream = [0] + 2*[0] + 4*[1] + 6*[0] + 3*[0] + [0,1,0] + [0] + \
                    [1] + [0,0,0,0,0,0,0] + [0] + [0,0,0,0,0,0] + [0] + \
                    [1,0,0,0,0,0] + [0,1,1] + [1,1,1,1,0] + \
                    [1,1,0,0,0,1,0,0] + [0]
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0.\n" + \
                    "0-02: No leap second.\n" + \
                    "03-06: Error: Decoded & computed Hamming weights " + \
                    "missmatch for bits 21-58: 30 != 10!\n" + \
                    "07-12: All zero.\n" + \
                    "16: No clock change\n" + \
                    "17-18: CEST - summer time.\n" + \
                    "20: Begin of time information.\n" + \
                    "28: Even parity of minutes successful.\n" + \
                    "35: Even parity of hours successful.\n" + \
                    "21-27 & 29-34: Time: 00:00h.\n" + \
                    "Error: 1*digit of month is > 9!\n" + \
                    "36-41 & 45-57: Date: 01.0?.23.\n" + \
                    "42-44: Weekday: Saturday.\n" + \
                    "58: Parity of date and weekdays successful.\n"
        self.assertEqual(objective, result)

        # negative test: - invalid month > 12
        bitstream = [0] + 2*[0] + 4*[1] + 6*[0] + 3*[0] + [0,1,0] + [0] + \
                    [1] + [0,0,0,0,0,0,0] + [0] + [0,0,0,0,0,0] + [0] + \
                    [1,0,0,0,0,0] + [0,1,1] + [1,1,1,1,1] + \
                    [1,1,0,0,0,1,0,0] + [1]
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0.\n" + \
                    "0-02: No leap second.\n" + \
                    "03-06: Error: Decoded & computed Hamming weights " + \
                    "missmatch for bits 21-58: 30 != 12!\n" + \
                    "07-12: All zero.\n" + \
                    "16: No clock change\n" + \
                    "17-18: CEST - summer time.\n" + \
                    "20: Begin of time information.\n" + \
                    "28: Even parity of minutes successful.\n" + \
                    "35: Even parity of hours successful.\n" + \
                    "21-27 & 29-34: Time: 00:00h.\n" + \
                    "Error: Month is > 12!\n" + \
                    "36-41 & 45-57: Date: 01.??.23.\n" + \
                    "42-44: Weekday: Saturday.\n" + \
                    "58: Parity of date and weekdays successful.\n"
        self.assertEqual(objective, result)

        # negative test: - invalid year 1*digit
        bitstream = [0] + 2*[0] + 4*[1] + 6*[0] + 3*[0] + [0,1,0] + [0] + \
                    [1] + [0,0,0,0,0,0,0] + [0] + [0,0,0,0,0,0] + [0] + \
                    [1,0,0,0,0,0] + [0,1,1] + [1,0,0,0,0] + \
                    [1,1,1,1,0,0,0,0] + [0]
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0.\n" + \
                    "0-02: No leap second.\n" + \
                    "03-06: Error: Decoded & computed Hamming weights " + \
                    "missmatch for bits 21-58: 30 != 8!\n" + \
                    "07-12: All zero.\n" + \
                    "16: No clock change\n" + \
                    "17-18: CEST - summer time.\n" + \
                    "20: Begin of time information.\n" + \
                    "28: Even parity of minutes successful.\n" + \
                    "35: Even parity of hours successful.\n" + \
                    "21-27 & 29-34: Time: 00:00h.\n" + \
                    "Error: 1*digit of year is > 9!\n" + \
                    "36-41 & 45-57: Date: 01.01.0?.\n" + \
                    "42-44: Weekday: Saturday.\n" + \
                    "58: Parity of date and weekdays successful.\n"
        self.assertEqual(objective, result)

        # negative test: - invalid year 10*digit
        bitstream = [0] + 2*[0] + 4*[1] + 6*[0] + 3*[0] + [0,1,0] + [0] + \
                    [1] + [0,0,0,0,0,0,0] + [0] + [0,0,0,0,0,0] + [0] + \
                    [1,0,0,0,0,0] + [0,1,1] + [1,0,0,0,0] + \
                    [0,0,0,0,1,1,1,1] + [0]
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0.\n" + \
                    "0-02: No leap second.\n" + \
                    "03-06: Error: Decoded & computed Hamming weights " + \
                    "missmatch for bits 21-58: 30 != 8!\n" + \
                    "07-12: All zero.\n" + \
                    "16: No clock change\n" + \
                    "17-18: CEST - summer time.\n" + \
                    "20: Begin of time information.\n" + \
                    "28: Even parity of minutes successful.\n" + \
                    "35: Even parity of hours successful.\n" + \
                    "21-27 & 29-34: Time: 00:00h.\n" + \
                    "Error: 10*digit of year is > 9!\n" + \
                    "36-41 & 45-57: Date: 01.01.?0.\n" + \
                    "42-44: Weekday: Saturday.\n" + \
                    "58: Parity of date and weekdays successful.\n"
        self.assertEqual(objective, result)

        # negative test: - invalid year 10*digit
        bitstream = [0] + 2*[0] + 4*[1] + 6*[0] + 3*[0] + [0,1,0] + [0] + \
                    [1] + [0,0,0,0,0,0,0] + [0] + [0,0,0,0,0,0] + [0] + \
                    [1,0,0,0,0,0] + [0,1,1] + [1,0,0,0,0] + \
                    [1,1,1,1,1,1,1,1] + [0]
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0.\n" + \
                    "0-02: No leap second.\n" + \
                    "03-06: Error: Decoded & computed Hamming weights " + \
                    "missmatch for bits 21-58: 30 != 12!\n" + \
                    "07-12: All zero.\n" + \
                    "16: No clock change\n" + \
                    "17-18: CEST - summer time.\n" + \
                    "20: Begin of time information.\n" + \
                    "28: Even parity of minutes successful.\n" + \
                    "35: Even parity of hours successful.\n" + \
                    "21-27 & 29-34: Time: 00:00h.\n" + \
                    "Error: Year is > 99!\n" + \
                    "36-41 & 45-57: Date: 01.01.??.\n" + \
                    "42-44: Weekday: Saturday.\n" + \
                    "58: Parity of date and weekdays successful.\n"
        self.assertEqual(objective, result)

    def _mock_send_msg(self, msg):
        context = zmq.Context()
        self.socket_sender = context.socket(zmq.PUSH)
        self.socket_sender.bind("tcp://127.0.0.1:55555")
        output = pmt.serialize_str(pmt.to_pmt(msg))
        self.socket_sender.send(output)
        self.socket_sender.close()
        context.term()

    def _mock_send_stream(self, stream, offset=0):
        for i in range(len(stream)):
            out_msg = f"{stream[i]}, {i+offset}"
            self._mock_send_msg(out_msg)

    def test_consumer(self):
        # positive test - ordinary 0 and 1 at beginning
        # Create StringIO object to capture any print-outputs on stdout
        result = StringIO()
        sys.stdout = result

        # run ALS162 decoder in a separate thread and start it
        t_decoder = threading.Thread(target=self.my_decoder.consumer, name='Thread-consumer')
        t_decoder.start()

        # send desired messages and exit-signal
        self._mock_send_msg("0, 00")
        self._mock_send_msg("1, 01")
        self._mock_send_msg("___EOT")

        # wait for decoder-thread to be completed
        t_decoder.join()

        objective = "decoded bit at 00: 0 at position: 00\n" + \
                    "decoded bit at 01: 1 at position: 01\n"
        self.assertEqual(objective, result.getvalue())

        # full clean up decoder
        del t_decoder

        # positive test - ordinary 0 and 1 but later than beginning
        # Create StringIO object to capture any print-outputs on stdout
        result = StringIO()
        sys.stdout = result

        # run ALS162 decoder in a separate thread and start it
        t_decoder = threading.Thread(target=self.my_decoder.consumer, name='Thread-consumer')
        t_decoder.start()

        # send desired messages and exit-signal
        self._mock_send_msg("0, 20")
        self._mock_send_msg("1, 21")
        self._mock_send_msg("___EOT")

        # wait for decoder-thread to be completed
        t_decoder.join()

        objective = "decoded bit at 00: 0 at position: 20\n" + \
                    "20 bit(s) lost before position: 20\n" + \
                    "decoded bit at 21: 1 at position: 21\n"
        self.assertEqual(objective, result.getvalue())

        # full clean up decoder
        del t_decoder

        # positive test - end of minute too early
        # Create StringIO object to capture any print-outputs on stdout
        result = StringIO()
        sys.stdout = result

        # run ALS162 decoder in a separate thread and start it
        t_decoder = threading.Thread(target=self.my_decoder.consumer, name='Thread-consumer')
        t_decoder.start()

        # send desired messages and exit-signal
        self._mock_send_msg("1, 00")
        self._mock_send_msg("0, 01")
        self._mock_send_msg("2, 02")
        self._mock_send_msg("___EOT")

        # wait for decoder-thread to be completed
        t_decoder.join()

        objective = "decoded bit at 00: 1 at position: 00\n" + \
                    "decoded bit at 01: 0 at position: 01\n" + \
                    "decoded bit at 02: 2 at position: 02\n" + \
                    "Error: Wrong number of bits at new minute!\n" + \
                    "#Bits: 2\n"
        self.assertEqual(objective, result.getvalue())

        # full clean up decoder
        del t_decoder

        # positive test - received forbidden symbols
        # Create StringIO object to capture any print-outputs on stdout
        result = StringIO()
        sys.stdout = result

        # run ALS162 decoder in a separate thread and start it
        t_decoder = threading.Thread(target=self.my_decoder.consumer, name='Thread-consumer')
        t_decoder.start()

        # send desired messages and exit-signal
        self._mock_send_msg("1, 00")
        self._mock_send_msg("Q, 01")
        self._mock_send_msg("0, 0K")
        self._mock_send_msg("___EOT")

        # wait for decoder-thread to be completed
        t_decoder.join()

        objective = "decoded bit at 00: 1 at position: 00\n" + \
                    "decoded bit at 01: Q at position: 01\n" + \
                    "Error: received message \"Q\" for time codeword is not permitted!\n" + \
                    "decoded bit at 02: 0 at position: 0K\n" + \
                    "Error: received message \"0K\" for position codeword is not permitted!\n"
        self.assertEqual(objective, result.getvalue())

        # full clean up decoder
        del t_decoder
        """
        # positive test - received new minute at right time
        # Create StringIO object to capture any print-outputs on stdout
        result = StringIO()
        sys.stdout = result

        # run ALS162 decoder in a separate thread and start it
        t_decoder = threading.Thread(target=self.my_decoder.consumer, name='Thread-consumer')
        t_decoder.start()

        # send desired messages and exit-signal
        for i in range(60):
            self._mock_send_msg(f"0, {i:02d}")
        self._mock_send_msg("2, 00")
        self._mock_send_msg("___EOT")

        # wait for decoder-thread to be completed
        t_decoder.join()

        objective = ""
        for i in range(60):
            objective += f"decoded bit at {i:02d}: 0 at position: {i:02d}\n"
        objective += "decoded bit at 60: 2 at position: 00\n" + \
                     "\n00: Start-bit is 0.\n" + \
                     "0-02: No leap second.\n" + \
                     "03-06: Decoded & computed Hamming weights match for " + \
                     "bits 21-58: 0 == 0.0.\n" + \
                     "07-12: All zero.\n" + \
                     "16: No clock change\n" + \
                     "17-18: Error: Neither CET nor CEST set!\n" + \
                     "20: Is 0 instead of 1!\n" + \
                     "28: Even parity of minutes successful.\n" + \
                     "35: Even parity of hours successful.\n" + \
                     "21-27 & 29-34: Time: 00:00h.\n" + \
                     "Error: Day is 00!\n" + \
                     "Error: Month is 00!\n" + \
                     "36-41 & 45-57: Date: ??.??.00.\n" + \
                     "42-44: Weekday: Sunday.\n" + \
                     "58: Parity of date and weekdays successful.\n\n"
        self.assertEqual(objective, result.getvalue())

        # full clean up decoder
        del t_decoder
        """
        # positive test - decoding with some lost bits at begin of minute
        # Create StringIO object to capture any print-outputs on stdout
        result = StringIO()
        sys.stdout = result

        # run ALS162 decoder in a separate thread and start it
        t_decoder = threading.Thread(target=self.my_decoder.consumer, name='Thread-consumer')
        t_decoder.start()
        stream = [0,0,0,0,0,1,0,0,1,0,0,1,0,1,0,0,0,1,0,0,1,0,0,0,1,
                  0,0,1,0,0,1,0,1,1,0,0,1,0,1,0,0,1,1,0,0,0,1,0,0,1]
        offset = 10
        self._mock_send_stream(stream=stream, offset=offset)
        self._mock_send_msg("2, 00")
        self._mock_send_msg("___EOT")

        # wait for decoder-thread to be completed
        t_decoder.join()

        objective = ""
        objective += f"decoded bit at 00: {stream[0]} at position: {offset:02d}\n" + \
                     f"10 bit(s) lost before position: {offset:02d}\n"
        for i in range(offset+1, 60, 1):
            objective += f"decoded bit at {i:02d}: {stream[i-offset]} at position: {i:02d}\n"
        objective += "decoded bit at 60: 2 at position: 00\n" + \
                     "\n00: Start-bit is ?.\n" + \
                     "01-02: Error: Leap second is ?.\n" + \
                     "03-06: Error: Hamming weight is ?.\n" + \
                     "07-12: Contains errors.\n" + \
                     "14: The current day is a holiday.\n" + \
                     "16: No clock change\n" + \
                     "17-18: CEST - summer time.\n" + \
                     "20: Begin of time information.\n" + \
                     "28: Even parity of minutes successful.\n" + \
                     "35: Even parity of hours successful.\n" + \
                     "21-27 & 29-34: Time: 11:22h.\n" + \
                     "36-41 & 45-57: Date: 29.05.23.\n" + \
                     "42-44: Weekday: Monday.\n" + \
                     "58: Parity of date and weekdays successful.\n" + \
                     "# Bit errors: 9 => at positions: [0, 1, 2, 3, 4, 5, 6, 7, 8].\n\n"
        self.assertEqual(objective, result.getvalue())

        # full clean up decoder
        del t_decoder


if __name__ == '__main__':
    testInstance = Test_Class_DecodeALS162()
    unittest.main()
