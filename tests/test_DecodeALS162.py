
import sys
sys.path.append('..')
from python import Class_DecodeALS162 as ALS162
import unittest
from io import StringIO
import zmq
import pmt
import threading
import sys


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

        # negative test - too many bits
        bits = [1, 1, 1]
        result = self.my_decoder.decode_BCD(bits, 2)
        objective = "?"
        self.assertEqual(objective, result)

        # negative test - too few bits
        bits = [1, 1, 1]
        result = self.my_decoder.decode_BCD(bits, 4)
        objective = "?"
        self.assertEqual(objective, result)

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

        # two errors are ignored (without error in parity bit]
        bitstream = [3]*2 + [0]*4
        result = self.my_decoder.single_error_correction(bitstream)
        objective = [[3]*2 + [0]*4, -1, -1]
        self.assertEqual(objective, result)

        # two errors are ignored (with one error in parity bit]
        bitstream = [3] + [0]*4 + [3]
        result = self.my_decoder.single_error_correction(bitstream)
        objective = [[3] + [0]*4 + [3], -1, -1]
        self.assertEqual(objective, result)

    def test_decode_startbit(self):
        bit = 1
        result = self.my_decoder.decode_startbit(bit)
        objective = "00: ERROR: Start-bit is 1 instead of 0!\n"
        self.assertEqual(objective, result)

        bit = 0
        result = self.my_decoder.decode_startbit(bit)
        objective = "00: Start-bit is 0.\n"
        self.assertEqual(objective, result)

        bit = 3
        result = self.my_decoder.decode_startbit(bit)
        objective = "00: ERROR: Start-bit is ?.\n"
        self.assertEqual(objective, result)

    def test_decode_check_hamming_weight(self):
        bits = 60*[0]
        result = self.my_decoder.check_hamming_weight(bits)
        objective = "03-06: Decoded & computed Hamming weights " + \
                    "match for bits 21-58: 0 == 0.0.\n"
        self.assertEqual(objective, result)

        bits = 50*[0] + [1] + 9*[0]
        result = self.my_decoder.check_hamming_weight(bits)
        objective = "03-06: ERROR: Decoded & computed Hamming weights " + \
                    "missmatch for bits 21-58: 0 != 1!\n" + \
                    "03-06: ERROR: Hamming weight for bits " + \
                    "21-58 is not even!\n"
        self.assertEqual(objective, result)

        bits = 3*[0] + [3] + 56*[0]
        result = self.my_decoder.check_hamming_weight(bits)
        objective = "03-06: ERROR: Hamming weight contains erroneous bits.\n"
        self.assertEqual(objective, result)

        bits = 50*[0] + [3] + 9*[0]
        result = self.my_decoder.check_hamming_weight(bits)
        objective = "03-06: ERROR: Bits 21-58 contain erroneous bits.\n"
        self.assertEqual(objective, result)

    def test_decode_unused_zeros(self):
        bits = 60*[0]
        result = self.my_decoder.decode_unused_zeros(bits)
        objective = "07-12: All zero.\n"
        self.assertEqual(objective, result)

        bits = 7*[0] + [1] + 42*[0]
        result = self.my_decoder.decode_unused_zeros(bits)
        objective = "07-12: ERROR: At least one bit is 1 instead of 0!\n"
        self.assertEqual(objective, result)

        bits = 8*[0] + [3] + 41*[0]
        result = self.my_decoder.decode_unused_zeros(bits)
        objective = "07-12: ERROR: Contains errors.\n"
        self.assertEqual(objective, result)

        bits = 15*[0] + [1] + 34*[0]
        result = self.my_decoder.decode_unused_zeros(bits)
        objective = "07-12: All zero.\n" + \
                    "15: ERROR: Is 1 instead of 0!\n"
        self.assertEqual(objective, result)

        bits = 15 * [0] + [3] + 34 * [0]
        result = self.my_decoder.decode_unused_zeros(bits)
        objective = "07-12: All zero.\n" + \
                    "15: ERROR: Contains an error.\n"
        self.assertEqual(objective, result)

        bits = 19 * [0] + [1] + 31 * [0]
        result = self.my_decoder.decode_unused_zeros(bits)
        objective = "07-12: All zero.\n" + \
                    "19: ERROR: Is 1 instead of 0!\n"
        self.assertEqual(objective, result)

        bits = 19 * [0] + [3] + 31 * [0]
        result = self.my_decoder.decode_unused_zeros(bits)
        objective = "07-12: All zero.\n" + \
                    "19: ERROR: Contains an error.\n"
        self.assertEqual(objective, result)

    def test_decode_leap_second(self):
        bits = [0, 0]
        result = self.my_decoder.decode_leap_second(bits)
        objective = "01-02: No leap second.\n"
        self.assertEqual(objective, result)

        bits = [0, 1]
        result = self.my_decoder.decode_leap_second(bits)
        objective = "02: Negative leap second warning.\n"
        self.assertEqual(objective, result)

        bits = [1, 0]
        result = self.my_decoder.decode_leap_second(bits)
        objective = "01: Positive leap second warning.\n"
        self.assertEqual(objective, result)

        bits = [1, 1]
        result = self.my_decoder.decode_leap_second(bits)
        objective = "01-02: ERROR: Both leap seconds are set!\n"
        self.assertEqual(objective, result)

        bits = [0, 3]
        result = self.my_decoder.decode_leap_second(bits)
        objective = "01-02: ERROR: Leap second is ?.\n"
        self.assertEqual(objective, result)

    def test_decode_holidays(self):
        bits = [0, 0]
        result = self.my_decoder.decode_holidays(bits)
        objective = ""
        self.assertEqual(objective, result)

        bits = [0, 1]
        result = self.my_decoder.decode_holidays(bits)
        objective = "14: The current day is a holiday.\n"
        self.assertEqual(objective, result)

        bits = [1, 0]
        result = self.my_decoder.decode_holidays(bits)
        objective = "13: The following day is a holiday.\n"
        self.assertEqual(objective, result)

        bits = [1, 1]
        result = self.my_decoder.decode_holidays(bits)
        objective = "13: The following day is a holiday.\n" + \
                    "14: The current day is a holiday.\n"
        self.assertEqual(objective, result)

        bits = [3, 3]
        result = self.my_decoder.decode_holidays(bits)
        objective = "13: ERROR: Following holiday contains an error.\n" + \
                    "14: ERROR: Current holiday contains an error.\n"
        self.assertEqual(objective, result)

    def test_decode_clock_change(self):
        bits = 0
        result = self.my_decoder.decode_clock_change(bits)
        objective = "16: No clock change\n"
        self.assertEqual(objective, result)

        bits = 1
        result = self.my_decoder.decode_clock_change(bits)
        objective = "16: Clock change\n"
        self.assertEqual(objective, result)

        bits = 3
        result = self.my_decoder.decode_clock_change(bits)
        objective = "16: ERROR: Clock change contains an error.\n"
        self.assertEqual(objective, result)

    def test_decode_time_info_bit(self):
        bit = 0
        result = self.my_decoder.decode_time_info_bit(bit)
        objective = "20: ERROR: Time-info-bit is 0 instead of 1!\n"
        self.assertEqual(objective, result)

        bit = 1
        result = self.my_decoder.decode_time_info_bit(bit)
        objective = "20: Begin of time information.\n"
        self.assertEqual(objective, result)

    def test_decode_summertime(self):
        bits = [0, 0]
        result = self.my_decoder.decode_summertime(bits)
        objective = "17-18: ERROR: Both CET and CEST are equal!\n"
        self.assertEqual(objective, result)

        bits = [0, 1]
        result = self.my_decoder.decode_summertime(bits)
        objective = "17-18: CET - winter time.\n"
        self.assertEqual(objective, result)

        bits = [1, 0]
        result = self.my_decoder.decode_summertime(bits)
        objective = "17-18: CEST - summer time.\n"
        self.assertEqual(objective, result)

        bits = [1, 1]
        result = self.my_decoder.decode_summertime(bits)
        objective = "17-18: ERROR: Both CET and CEST are equal!\n"
        self.assertEqual(objective, result)

        bits = [3, 0]
        result = self.my_decoder.decode_summertime(bits)
        objective = "17-18: ERROR: CET/CEST contains errors\n"
        self.assertEqual(objective, result)

    def test_decode_bitstream(self):
        # negative test - too many bits
        bitstream = [0]*60
        result = self.my_decoder.decode_bitstream(bitstream)
        objective = "Decoding error\nReceived bits: 60\n"
        self.assertEqual(objective, result)

        # negative test - too few bits
        bitstream = [0]*58
        result = self.my_decoder.decode_bitstream(bitstream)
        objective = "Decoding error\nReceived bits: 58\n"
        self.assertEqual(objective, result)

    def test_decode_day(self):
        bits = [0, 0, 0, 0, 0, 0]
        [result, day_1, day_10] = self.my_decoder.decode_day(bits)
        objective = "ERROR: Day is 00!\n"
        self.assertEqual(objective, result)
        objective = "?"
        self.assertEqual(objective, day_1)
        self.assertEqual(objective, day_10)

        bits = [1, 0, 0, 0, 0, 0]
        [result, day_1, day_10] = self.my_decoder.decode_day(bits)
        objective = ""
        self.assertEqual(objective, result)
        objective = 1
        self.assertEqual(objective, day_1)
        objective = 0
        self.assertEqual(objective, day_10)

        bits = [0, 0, 0, 0, 1, 0]
        [result, day_1, day_10] = self.my_decoder.decode_day(bits)
        objective = ""
        self.assertEqual(objective, result)
        objective = 0
        self.assertEqual(objective, day_1)
        objective = 1
        self.assertEqual(objective, day_10)

        bits = [0, 1, 0, 1, 0, 0]
        [result, day_1, day_10] = self.my_decoder.decode_day(bits)
        objective = "ERROR: 1*digit of day is > 9!\n"
        self.assertEqual(objective, result)
        objective = "?"
        self.assertEqual(objective, day_1)
        objective = 0
        self.assertEqual(objective, day_10)

        bits = [0, 1, 0, 0, 1, 1]
        [result, day_1, day_10] = self.my_decoder.decode_day(bits)
        objective = "ERROR: Day is > 31!\n"
        self.assertEqual(objective, result)
        objective = "?"
        self.assertEqual(objective, day_1)
        objective = "?"
        self.assertEqual(objective, day_10)

        bits = [0, 0, 3, 0, 0, 0]
        [result, day_1, day_10] = self.my_decoder.decode_day(bits)
        objective = "ERROR: Day is ?.\n"
        self.assertEqual(objective, result)
        objective = "?"
        self.assertEqual(objective, day_1)
        objective = "?"
        self.assertEqual(objective, day_10)

    def test_decode_month(self):
        bits = [0, 0, 0, 0, 0]
        [result, month_1, month_10] = self.my_decoder.decode_month(bits)
        objective = "ERROR: Month is 00!\n"
        self.assertEqual(objective, result)
        objective = "?"
        self.assertEqual(objective, month_1)
        self.assertEqual(objective, month_10)

        bits = [1, 0, 0, 0, 0]
        [result, month_1, month_10] = self.my_decoder.decode_month(bits)
        objective = ""
        self.assertEqual(objective, result)
        objective = 1
        self.assertEqual(objective, month_1)
        objective = 0
        self.assertEqual(objective, month_10)

        bits = [0, 1, 0, 1, 0]
        [result, month_1, month_10] = self.my_decoder.decode_month(bits)
        objective = "ERROR: 1*digit of month is > 9!\n"
        self.assertEqual(objective, result)
        objective = "?"
        self.assertEqual(objective, month_1)
        objective = 0
        self.assertEqual(objective, month_10)

        bits = [1, 1, 0, 0, 1]
        [result, month_1, month_10] = self.my_decoder.decode_month(bits)
        objective = "ERROR: Month is > 12!\n"
        self.assertEqual(objective, result)
        objective = "?"
        self.assertEqual(objective, month_1)
        objective = "?"
        self.assertEqual(objective, month_10)

        bits = [3, 1, 0, 0, 0]
        [result, month_1, month_10] = self.my_decoder.decode_month(bits)
        objective = "ERROR: Month is ?.\n"
        self.assertEqual(objective, result)
        objective = "?"
        self.assertEqual(objective, month_1)
        objective = "?"
        self.assertEqual(objective, month_10)

        bits = [0, 1, 0, 0, 3]
        [result, month_1, month_10] = self.my_decoder.decode_month(bits)
        objective = "ERROR: Month is ?.\n"
        self.assertEqual(objective, result)
        objective = "?"
        self.assertEqual(objective, month_1)
        objective = "?"
        self.assertEqual(objective, month_10)

    def test_decode_year(self):
        bits = [0, 0, 0, 0, 0, 0, 0, 0]
        [result, year_1, year_10] = self.my_decoder.decode_year(bits)
        objective = ""
        self.assertEqual(objective, result)
        objective = 0
        self.assertEqual(objective, year_1)
        objective = 0
        self.assertEqual(objective, year_10)

        bits = [3, 0, 0, 0, 0, 0, 0, 0]
        [result, year_1, year_10] = self.my_decoder.decode_year(bits)
        objective = "ERROR: Year is ?.\n"
        self.assertEqual(objective, result)
        objective = "?"
        self.assertEqual(objective, year_1)
        objective = "?"
        self.assertEqual(objective, year_10)

        bits = [0, 0, 0, 0, 0, 0, 0, 3]
        [result, year_1, year_10] = self.my_decoder.decode_year(bits)
        objective = "ERROR: Year is ?.\n"
        self.assertEqual(objective, result)
        objective = "?"
        self.assertEqual(objective, year_1)
        objective = "?"
        self.assertEqual(objective, year_10)

        bits = [0, 1, 0, 1, 0, 1, 0, 1]
        [result, year_1, year_10] = self.my_decoder.decode_year(bits)
        objective = "ERROR: Year is > 99!\n"
        self.assertEqual(objective, result)
        objective = "?"
        self.assertEqual(objective, year_1)
        objective = "?"
        self.assertEqual(objective, year_10)

        bits = [0, 1, 0, 1, 0, 0, 0, 0]
        [result, year_1, year_10] = self.my_decoder.decode_year(bits)
        objective = "ERROR: 1*digit of year is > 9!\n"
        self.assertEqual(objective, result)
        objective = "?"
        self.assertEqual(objective, year_1)
        objective = 0
        self.assertEqual(objective, year_10)

        bits = [0, 0, 0, 0, 0, 1, 0, 1]
        [result, year_1, year_10] = self.my_decoder.decode_year(bits)
        objective = "ERROR: 10*digit of year is > 9!\n"
        self.assertEqual(objective, result)
        objective = 0
        self.assertEqual(objective, year_1)
        objective = "?"
        self.assertEqual(objective, year_10)

    def test_decode_weekday(self):
        bits = [0, 0, 0]
        result = self.my_decoder.decode_weekday(bits)
        objective = "42-44: ERROR: Weekday is 0.\n"
        self.assertEqual(objective, result)

        bits = [1, 0, 0]
        result = self.my_decoder.decode_weekday(bits)
        objective = "42-44: Weekday: Monday.\n"
        self.assertEqual(objective, result)

        bits = [1, 1, 1]
        result = self.my_decoder.decode_weekday(bits)
        objective = "42-44: Weekday: Sunday.\n"
        self.assertEqual(objective, result)

        bits = [1, 3, 0]
        result = self.my_decoder.decode_weekday(bits)
        objective = "42-44: ERROR: Weekday is ?.\n"
        self.assertEqual(objective, result)

    def test_decode_minutes(self):
        bits = [0, 0, 0, 0, 0, 0, 0, 0]
        [result, min_1, min_10] = self.my_decoder.decode_minutes(bits)
        objective = "28: Even parity of minutes successful.\n"
        self.assertEqual(objective, result)
        objective = 0
        self.assertEqual(objective, min_1)
        objective = 0
        self.assertEqual(objective, min_10)

        bits = [0, 0, 0, 0, 0, 0, 0, 1]
        [result, min_1, min_10] = self.my_decoder.decode_minutes(bits)
        objective = "28: Even parity of minutes failed.\n"
        self.assertEqual(objective, result)
        objective = 0
        self.assertEqual(objective, min_1)
        objective = 0
        self.assertEqual(objective, min_10)

        bits = [1, 0, 0, 0, 0, 0, 0, 1]
        [result, min_1, min_10] = self.my_decoder.decode_minutes(bits)
        objective = "28: Even parity of minutes successful.\n"
        self.assertEqual(objective, result)
        objective = 1
        self.assertEqual(objective, min_1)
        objective = 0
        self.assertEqual(objective, min_10)

        bits = [0, 0, 0, 0, 0, 1, 1, 0]
        [result, min_1, min_10] = self.my_decoder.decode_minutes(bits)
        objective = "28: Even parity of minutes successful.\n" + \
                    "ERROR: 10*digit of minute is > 5!\n"
        self.assertEqual(objective, result)
        objective = 0
        self.assertEqual(objective, min_1)
        objective = "?"
        self.assertEqual(objective, min_10)

        bits = [0, 1, 0, 1, 0, 0, 0, 0]
        [result, min_1, min_10] = self.my_decoder.decode_minutes(bits)
        objective = "28: Even parity of minutes successful.\n" + \
                    "ERROR: 1*digit of minute is > 9!\n"
        self.assertEqual(objective, result)
        objective = "?"
        self.assertEqual(objective, min_1)
        objective = 0
        self.assertEqual(objective, min_10)

        bits = [0, 1, 0, 1, 0, 1, 1, 0]
        [result, min_1, min_10] = self.my_decoder.decode_minutes(bits)
        objective = "28: Even parity of minutes successful.\n" + \
                    "ERROR: 10*digit of minute is > 5!\n" + \
                    "ERROR: 1*digit of minute is > 9!\n"
        self.assertEqual(objective, result)
        objective = "?"
        self.assertEqual(objective, min_1)
        objective = "?"
        self.assertEqual(objective, min_10)

        bits = [3, 0, 0, 0, 0, 0, 0, 0]
        [result, min_1, min_10] = self.my_decoder.decode_minutes(bits)
        objective = "Corrected single error at 21.\n"
        self.assertEqual(objective, result)
        objective = 0
        self.assertEqual(objective, min_1)
        objective = 0
        self.assertEqual(objective, min_10)

        bits = [3, 0, 0, 0, 0, 0, 0, 3]
        [result, min_1, min_10] = self.my_decoder.decode_minutes(bits)
        objective = "28: Even parity of minutes is ?.\n" + \
                    "ERROR: Minute is ?.\n"
        self.assertEqual(objective, result)
        objective = "?"
        self.assertEqual(objective, min_1)
        objective = 0
        self.assertEqual(objective, min_10)

    def test_decode_hours(self):
        bits = [0, 0, 0, 0, 0, 0, 0]
        [result, min_1, min_10] = self.my_decoder.decode_hours(bits)
        objective = "35: Even parity of hours successful.\n"
        self.assertEqual(objective, result)
        objective = 0
        self.assertEqual(objective, min_1)
        objective = 0
        self.assertEqual(objective, min_10)

        bits = [0, 0, 0, 0, 0, 0, 1]
        [result, min_1, min_10] = self.my_decoder.decode_hours(bits)
        objective = "35: Even parity of hours failed.\n"
        self.assertEqual(objective, result)
        objective = 0
        self.assertEqual(objective, min_1)
        objective = 0
        self.assertEqual(objective, min_10)

        bits = [1, 0, 0, 0, 0, 0, 1]
        [result, min_1, min_10] = self.my_decoder.decode_hours(bits)
        objective = "35: Even parity of hours successful.\n"
        self.assertEqual(objective, result)
        objective = 1
        self.assertEqual(objective, min_1)
        objective = 0
        self.assertEqual(objective, min_10)

        bits = [0, 1, 0, 1, 1, 1, 0]
        [result, min_1, min_10] = self.my_decoder.decode_hours(bits)
        objective = "35: Even parity of hours successful.\n" + \
                    "ERROR: 1*digit of hour is > 9!\n" + \
                    "ERROR: 10*digit of hour is > 2!\n"
        self.assertEqual(objective, result)
        objective = "?"
        self.assertEqual(objective, min_1)
        objective = "?"
        self.assertEqual(objective, min_10)

        bits = [0, 0, 1, 0, 0, 1, 0]
        [result, min_1, min_10] = self.my_decoder.decode_hours(bits)
        objective = "35: Even parity of hours successful.\n" + \
                    "ERROR: Hours are greater than 23!\n"
        self.assertEqual(objective, result)
        objective = "?"
        self.assertEqual(objective, min_1)
        objective = "?"
        self.assertEqual(objective, min_10)

        bits = [0, 1, 0, 1, 0, 0, 0]
        [result, min_1, min_10] = self.my_decoder.decode_hours(bits)
        objective = "35: Even parity of hours successful.\n" + \
                    "ERROR: 1*digit of hour is > 9!\n"
        self.assertEqual(objective, result)
        objective = "?"
        self.assertEqual(objective, min_1)
        objective = 0
        self.assertEqual(objective, min_10)

        bits = [0, 0, 0, 0, 1, 1, 0]
        [result, min_1, min_10] = self.my_decoder.decode_hours(bits)
        objective = "35: Even parity of hours successful.\n" + \
                    "ERROR: 10*digit of hour is > 2!\n"
        self.assertEqual(objective, result)
        objective = 0
        self.assertEqual(objective, min_1)
        objective = "?"
        self.assertEqual(objective, min_10)

        bits = [3, 0, 0, 0, 0, 0, 1]
        [result, min_1, min_10] = self.my_decoder.decode_hours(bits)
        objective = "Corrected single error at 30.\n"
        self.assertEqual(objective, result)
        objective = 1
        self.assertEqual(objective, min_1)
        objective = 0
        self.assertEqual(objective, min_10)

        bits = [3, 3, 0, 0, 0, 0, 0]
        [result, min_1, min_10] = self.my_decoder.decode_hours(bits)
        objective = "35: Even parity of hours is ?.\n" + \
                    "ERROR: Hour is ?.\n"
        self.assertEqual(objective, result)
        objective = "?"
        self.assertEqual(objective, min_1)
        objective = 0
        self.assertEqual(objective, min_10)

    def test_decode_date_weekday(self):
        bits = [1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
        result = self.my_decoder.decode_date_weekday(bits)
        objective = "36-41 & 45-57: Date: 01.01.00.\n" + \
                    "42-44: Weekday: Monday.\n" + \
                    "58: Parity of date and weekdays successful.\n"
        self.assertEqual(objective, result)

        bits = [1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        result = self.my_decoder.decode_date_weekday(bits)
        objective = "36-41 & 45-57: Date: 01.01.00.\n" + \
                    "42-44: Weekday: Monday.\n" + \
                    "58: ERROR: Parity of date and weekdays failed.\n"
        self.assertEqual(objective, result)

        bits = [3, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
        result = self.my_decoder.decode_date_weekday(bits)
        objective = "Corrected single error at 37.\n" + \
                    "36-41 & 45-57: Date: 01.01.00.\n" + \
                    "42-44: Weekday: Monday.\n" + \
                    "58: Parity of date and weekdays successful.\n"
        self.assertEqual(objective, result)

        bits = [3, 3, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
        result = self.my_decoder.decode_date_weekday(bits)
        objective = "ERROR: Day is ?.\n" + \
                    "36-41 & 45-57: Date: ??.01.00.\n" + \
                    "42-44: Weekday: Monday.\n" + \
                    "58: ERROR: Parity of date and weekdays is ?.\n"
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
        for i in range(1, len(stream)):
            out_msg = f"{stream[i]}, {i+offset:02d}"
            self._mock_send_msg(out_msg)

    def test_consumer(self):
        # positive test - ordinary 0 and 1 at beginning
        # Create StringIO object to capture any print-outputs on stdout
        result = StringIO()
        sys.stdout = result

        # run ALS162 decoder in a separate thread and start it
        t_decoder = threading.Thread(target=self.my_decoder.consumer,
                                     name='Thread-consumer')
        t_decoder.start()

        # send desired messages and exit-signal
        self._mock_send_msg("0, 01")
        self._mock_send_msg("1, 02")
        self._mock_send_msg("___EOT")

        # wait for decoder-thread to be completed
        t_decoder.join()

        objective = "decoded bit at 01: 0 at position: 01\n" + \
                    "decoded bit at 02: 1 at position: 02\n"
        self.assertEqual(objective, result.getvalue())

        # full clean-up of decoder
        del t_decoder

        # positive test - ordinary 0 and 1 but later than beginning
        # Create StringIO object to capture any print-outputs on stdout
        result = StringIO()
        sys.stdout = result

        # run ALS162 decoder in a separate thread and start it
        t_decoder = threading.Thread(target=self.my_decoder.consumer,
                                     name='Thread-consumer')
        t_decoder.start()

        # send desired messages and exit-signal
        self._mock_send_msg("0, 20")
        self._mock_send_msg("1, 21")
        self._mock_send_msg("___EOT")

        # wait for decoder-thread to be completed
        t_decoder.join()

        objective = "decoded bit at 01: 0 at position: 20\n" + \
                    "19 bit(s) lost before position: 20\n" + \
                    "decoded bit at 21: 1 at position: 21\n"
        self.assertEqual(objective, result.getvalue())

        # full clean-up of decoder
        del t_decoder

        # positive test - end of minute too early
        # Create StringIO object to capture any print-outputs on stdout
        result = StringIO()
        sys.stdout = result

        # run ALS162 decoder in a separate thread and start it
        t_decoder = threading.Thread(target=self.my_decoder.consumer,
                                     name='Thread-consumer')
        t_decoder.start()

        # send desired messages and exit-signal
        self._mock_send_msg("1, 01")
        self._mock_send_msg("0, 02")
        self._mock_send_msg("2, 03")
        self._mock_send_msg("___EOT")

        # wait for decoder-thread to be completed
        t_decoder.join()

        objective = "decoded bit at 01: 1 at position: 01\n" + \
                    "decoded bit at 02: 0 at position: 02\n" + \
                    "decoded bit at 03: 2 at position: 03\n" + \
                    "ERROR: Wrong number of bits at new minute!\n" + \
                    "#Bits: 2\n"
        self.assertEqual(objective, result.getvalue())

        # full clean-up of decoder
        del t_decoder

        # positive test - received forbidden symbols
        # Create StringIO object to capture any print-outputs on stdout
        result = StringIO()
        sys.stdout = result

        # run ALS162 decoder in a separate thread and start it
        t_decoder = threading.Thread(target=self.my_decoder.consumer,
                                     name='Thread-consumer')
        t_decoder.start()

        # send desired messages and exit-signal
        self._mock_send_msg("1, 01")
        self._mock_send_msg("Q, 02")
        self._mock_send_msg("0, 0K")
        self._mock_send_msg("___EOT")

        # wait for decoder-thread to be completed
        t_decoder.join()

        objective = "decoded bit at 01: 1 at position: 01\n" + \
                    "decoded bit at 02: Q at position: 02\n" + \
                    "ERROR: received message \"Q\" for time codeword " + \
                    "is not permitted!\n" + \
                    "decoded bit at 03: 0 at position: 0K\n" + \
                    "ERROR: received message \"0K\" for position " + \
                    "codeword is not permitted!\n"
        self.assertEqual(objective, result.getvalue())

        # full clean-up of decoder
        del t_decoder

        # positive test - received new minute at right time
        # Create StringIO object to capture any print-outputs on stdout
        result = StringIO()
        sys.stdout = result

        # run ALS162 decoder in a separate thread and start it
        t_decoder = threading.Thread(target=self.my_decoder.consumer,
                                     name='Thread-consumer')
        t_decoder.start()

        # send desired messages and exit-signal
        for i in range(1, 60):
            self._mock_send_msg(f"0, {i:02d}")
        self._mock_send_msg("2, 00")
        self._mock_send_msg("___EOT")

        # wait for decoder-thread to be completed
        t_decoder.join()

        objective = ""
        for i in range(1, 60):
            objective += f"decoded bit at {i:02d}: 0 at position: {i:02d}\n"
        objective += "decoded bit at 60: 2 at position: 00\n" + \
                     "\n00: Start-bit is 0.\n" + \
                     "01-02: No leap second.\n" + \
                     "03-06: Decoded & computed Hamming weights match for " + \
                     "bits 21-58: 0 == 0.0.\n" + \
                     "07-12: All zero.\n" + \
                     "16: No clock change\n" + \
                     "17-18: ERROR: Both CET and CEST are equal!\n" + \
                     "20: ERROR: Time-info-bit is 0 instead of 1!\n" + \
                     "28: Even parity of minutes successful.\n" + \
                     "35: Even parity of hours successful.\n" + \
                     "21-27 & 29-34: Time: 00:00h.\n" + \
                     "ERROR: Day is 00!\n" + \
                     "ERROR: Month is 00!\n" + \
                     "36-41 & 45-57: Date: ??.??.00.\n" + \
                     "42-44: ERROR: Weekday is 0.\n" + \
                     "58: Parity of date and weekdays successful.\n\n"
        self.assertEqual(objective, result.getvalue())

        # full clean-up of decoder
        del t_decoder

        # positive test - decoding with some lost bits at begin of minute
        # Create StringIO object to capture any print-outputs on stdout
        result = StringIO()
        sys.stdout = result

        # run ALS162 decoder in a separate thread and start it
        t_decoder = threading.Thread(target=self.my_decoder.consumer,
                                     name='Thread-consumer')
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
        objective += f"decoded bit at 01: {stream[0]} at position: " + \
                     f"{offset+1:02d}\n" + \
                     f"10 bit(s) lost before position: {offset+1:02d}\n"
        for i in range(offset+2, 60, 1):
            objective += f"decoded bit at {i:02d}: {stream[i-offset]} " + \
                         f"at position: {i}\n"
        objective += "decoded bit at 60: 2 at position: 00\n" + \
                     "\n00: ERROR: Start-bit is ?.\n" + \
                     "01-02: ERROR: Leap second is ?.\n" + \
                     "03-06: ERROR: Hamming weight contains " +\
                     "erroneous bits.\n" + \
                     "07-12: ERROR: Contains errors.\n" + \
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
                     "# Bit errors: 10 => at positions: " + \
                     "[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].\n\n"
        self.assertEqual(objective, result.getvalue())

        # full clean-up of decoder
        del t_decoder

        # negative test - decoding with additional bits
        # Create StringIO object to capture any print-outputs on stdout
        result = StringIO()
        sys.stdout = result

        # run ALS162 decoder in a separate thread and start it
        t_decoder = threading.Thread(target=self.my_decoder.consumer,
                                     name='Thread-consumer')
        t_decoder.start()
        stream = [0]*62
        self._mock_send_stream(stream=stream, offset=0)
        self._mock_send_msg("___EOT")

        # wait for decoder-thread to be completed
        t_decoder.join()

        objective = ""
        for i in range(1, 61, 1):
            objective += f"decoded bit at {i:02d}: {stream[i]} " + \
                         f"at position: {i:02d}\n"
        objective += "ERROR: more than 60 bits counted: Reinit Counter.\n"
        self.assertEqual(objective, result.getvalue())

        # full clean-up of decoder
        del t_decoder

        # positive test - received errors in time-symbol
        # Create StringIO object to capture any print-outputs on stdout
        result = StringIO()
        sys.stdout = result

        # run ALS162 decoder in a separate thread and start it
        t_decoder = threading.Thread(target=self.my_decoder.consumer,
                                     name='Thread-consumer')
        t_decoder.start()

        # send desired messages and exit-signal
        self._mock_send_msg("E, 01")
        self._mock_send_msg("___EOT")

        # wait for decoder-thread to be completed
        t_decoder.join()

        objective = "decoded bit at 01: E at position: 01\n"
        self.assertEqual(objective, result.getvalue())

        # full clean-up of decoder
        del t_decoder

        # positive test - received errors in position symbols
        # Create StringIO object to capture any print-outputs on stdout
        result = StringIO()
        sys.stdout = result

        # run ALS162 decoder in a separate thread and start it
        t_decoder = threading.Thread(target=self.my_decoder.consumer,
                                     name='Thread-consumer')
        t_decoder.start()

        # send desired messages and exit-signal
        self._mock_send_msg("0, 01")
        self._mock_send_msg("1, EE")
        self._mock_send_msg("0, 03")
        self._mock_send_msg("___EOT")

        # wait for decoder-thread to be completed
        t_decoder.join()

        objective = "decoded bit at 01: 0 at position: 01\n" + \
                    "decoded bit at 02: 1 at position: EE\n" + \
                    "decoded bit at 03: 0 at position: 03\n"
        self.assertEqual(objective, result.getvalue())

        # full clean-up of decoder
        del t_decoder


if __name__ == '__main__':
    testInstance = Test_Class_DecodeALS162()
    unittest.main()
