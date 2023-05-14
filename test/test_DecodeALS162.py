
import sys
import unittest
sys.path.append('..')
from python import Class_DecodeALS162 as ALS162


class Test_Class_DecodeALS162(unittest.TestCase):

    def setUp(self):
        self.my_decoder = ALS162.Class_DecodeALS162()
        self.maxDiff = None

    def test_decode_BCD4(self):
        # positive test
        bits = [0, 0, 0, 0]
        result = self.my_decoder.decode_BCD4(bits)
        objective = 0
        self.assertEqual(objective, result)

        # positive test
        bits = [0, 0, 0, 1]
        result = self.my_decoder.decode_BCD4(bits)
        objective = 1
        self.assertEqual(objective, result)

        # positive test
        bits = [1, 0, 0, 0]
        result = self.my_decoder.decode_BCD4(bits)
        objective = 8
        self.assertEqual(objective, result)

        # positive test
        bits = [1, 1, 1, 1]
        result = self.my_decoder.decode_BCD4(bits)
        objective = 15
        self.assertEqual(objective, result)

        # positive test
        bits = [0, 3, 1, 0]
        result = self.my_decoder.decode_BCD4(bits)
        objective = "?"
        self.assertEqual(objective, result)

        # TBD negative test - too many bits
        # TBD negative test - too few bits

    def test_decode_BCD2(self):
        # positive test
        bits = [0, 0]
        result = self.my_decoder.decode_BCD2(bits)
        objective = 0
        self.assertEqual(objective, result)

        # positive test
        bits = [0, 1]
        result = self.my_decoder.decode_BCD2(bits)
        objective = 1
        self.assertEqual(objective, result)

        # positive test
        bits = [1, 0]
        result = self.my_decoder.decode_BCD2(bits)
        objective = 2
        self.assertEqual(objective, result)

        # positive test
        bits = [1, 1]
        result = self.my_decoder.decode_BCD2(bits)
        objective = 3
        self.assertEqual(objective, result)

        # positive test
        bits = [0, 3]
        result = self.my_decoder.decode_BCD2(bits)
        objective = "?"
        self.assertEqual(objective, result)

        # TBD negative test - too many bits
        # TBD negative test - too few bits

    def test_decode_BCD3(self):
        # positive test
        bits = [0, 0, 0]
        result = self.my_decoder.decode_BCD3(bits)
        objective = 0
        self.assertEqual(objective, result)

        # positive test
        bits = [0, 0, 1]
        result = self.my_decoder.decode_BCD3(bits)
        objective = 1
        self.assertEqual(objective, result)

        # positive test
        bits = [1, 0, 0]
        result = self.my_decoder.decode_BCD3(bits)
        objective = 4
        self.assertEqual(objective, result)

        # positive test
        bits = [0, 0, 3]
        result = self.my_decoder.decode_BCD3(bits)
        objective = "?"
        self.assertEqual(objective, result)

        # TBD negative test - too many bits
        # TBD negative test - too few bits

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
        objective = "\n00: Start-bit is 0\n" + \
                    "07-12: Always zero\n" + \
                    "16: No clock change\n" + \
                    "17-18: Error: Neither CET nor CEST set!\n" + \
                    "20: Is 0 instead of 1!\n" + \
                    "28: Even parity of minutes successful\n" + \
                    "35: Even parity of hours successful\n" + \
                    "21-27 & 29-34: Time: 00:00h\n" + \
                    "Error: Day is 00!\n" + \
                    "Error: Month is 00!\n" + \
                    "36-41 & 45-57: Date: ??.??.00\n" + \
                    "42-44: Weekday: Sunday\n" + \
                    "58: Parity of date and weekdays successful\n"
        self.assertEqual(objective, result)

        # positive test - start bit is wrongly 1
        bitstream = [1] + [0]*59
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 1 instead of 0!\n" + \
                    "07-12: Always zero\n" + \
                    "16: No clock change\n" + \
                    "17-18: Error: Neither CET nor CEST set!\n" + \
                    "20: Is 0 instead of 1!\n" + \
                    "28: Even parity of minutes successful\n" + \
                    "35: Even parity of hours successful\n" + \
                    "21-27 & 29-34: Time: 00:00h\n" + \
                    "Error: Day is 00!\n" + \
                    "Error: Month is 00!\n" + \
                    "36-41 & 45-57: Date: ??.??.00\n" + \
                    "42-44: Weekday: Sunday\n" + \
                    "58: Parity of date and weekdays successful\n"
        self.assertEqual(objective, result)

        # positive test - a bit in 07-12 is wrongly 1
        bitstream = [0] + 6*[0] + 1*[1] + [0]*52
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0\n" + \
                    "07-12: At least one bit is 1 instead of 0!\n" + \
                    "16: No clock change\n" + \
                    "17-18: Error: Neither CET nor CEST set!\n" + \
                    "20: Is 0 instead of 1!\n" + \
                    "28: Even parity of minutes successful\n" + \
                    "35: Even parity of hours successful\n" + \
                    "21-27 & 29-34: Time: 00:00h\n" + \
                    "Error: Day is 00!\n" + \
                    "Error: Month is 00!\n" + \
                    "36-41 & 45-57: Date: ??.??.00\n" + \
                    "42-44: Weekday: Sunday\n" + \
                    "58: Parity of date and weekdays successful\n"
        self.assertEqual(objective, result)

        # positive test - following day is a holiday
        bitstream = [0] + 6*[0] + 6*[0] + [1] + [0]*47
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0\n" + \
                    "07-12: Always zero\n" + \
                    "13: The following day is a holiday\n" + \
                    "16: No clock change\n" + \
                    "17-18: Error: Neither CET nor CEST set!\n" + \
                    "20: Is 0 instead of 1!\n" + \
                    "28: Even parity of minutes successful\n" + \
                    "35: Even parity of hours successful\n" + \
                    "21-27 & 29-34: Time: 00:00h\n" + \
                    "Error: Day is 00!\n" + \
                    "Error: Month is 00!\n" + \
                    "36-41 & 45-57: Date: ??.??.00\n" + \
                    "42-44: Weekday: Sunday\n" + \
                    "58: Parity of date and weekdays successful\n"
        self.assertEqual(objective, result)

        # positive test - current day is a holiday
        bitstream = [0] + 6*[0] + 7*[0] + [1] + [0]*46
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0\n" + \
                    "07-12: Always zero\n" + \
                    "14: The current day is a holiday\n" + \
                    "16: No clock change\n" + \
                    "17-18: Error: Neither CET nor CEST set!\n" + \
                    "20: Is 0 instead of 1!\n" + \
                    "28: Even parity of minutes successful\n" + \
                    "35: Even parity of hours successful\n" + \
                    "21-27 & 29-34: Time: 00:00h\n" + \
                    "Error: Day is 00!\n" + \
                    "Error: Month is 00!\n" + \
                    "36-41 & 45-57: Date: ??.??.00\n" + \
                    "42-44: Weekday: Sunday\n" + \
                    "58: Parity of date and weekdays successful\n"
        self.assertEqual(objective, result)

        # positive test - clock change
        bitstream = [0] + 6*[0] + 9*[0] + [1] + [0]*44
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0\n" + \
                    "07-12: Always zero\n" + \
                    "16: Clock change\n" + \
                    "17-18: Error: Neither CET nor CEST set!\n" + \
                    "20: Is 0 instead of 1!\n" + \
                    "28: Even parity of minutes successful\n" + \
                    "35: Even parity of hours successful\n" + \
                    "21-27 & 29-34: Time: 00:00h\n" + \
                    "Error: Day is 00!\n" + \
                    "Error: Month is 00!\n" + \
                    "36-41 & 45-57: Date: ??.??.00\n" + \
                    "42-44: Weekday: Sunday\n" + \
                    "58: Parity of date and weekdays successful\n"
        self.assertEqual(objective, result)

        # positive test - summer time
        bitstream = [0] + 6*[0] + 10*[0] + [1] + [0]*43
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0\n" + \
                    "07-12: Always zero\n" + \
                    "16: No clock change\n" + \
                    "17-18: CEST - summer time\n" + \
                    "20: Is 0 instead of 1!\n" + \
                    "28: Even parity of minutes successful\n" + \
                    "35: Even parity of hours successful\n" + \
                    "21-27 & 29-34: Time: 00:00h\n" + \
                    "Error: Day is 00!\n" + \
                    "Error: Month is 00!\n" + \
                    "36-41 & 45-57: Date: ??.??.00\n" + \
                    "42-44: Weekday: Sunday\n" + \
                    "58: Parity of date and weekdays successful\n"
        self.assertEqual(objective, result)

        # positive test - winter time
        bitstream = [0] + 6*[0] + 11*[0] + [1] + [0]*42
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0\n" + \
                    "07-12: Always zero\n" + \
                    "16: No clock change\n" + \
                    "17-18: CET - winter time\n" + \
                    "20: Is 0 instead of 1!\n" + \
                    "28: Even parity of minutes successful\n" + \
                    "35: Even parity of hours successful\n" + \
                    "21-27 & 29-34: Time: 00:00h\n" + \
                    "Error: Day is 00!\n" + \
                    "Error: Month is 00!\n" + \
                    "36-41 & 45-57: Date: ??.??.00\n" + \
                    "42-44: Weekday: Sunday\n" + \
                    "58: Parity of date and weekdays successful\n"
        self.assertEqual(objective, result)

        # positive test - bit 19 is wrongly set to 1
        bitstream = [0] + 6*[0] + 12*[0] + [1] + [0]*41
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0\n" + \
                    "07-12: Always zero\n" + \
                    "16: No clock change\n" + \
                    "17-18: Error: Neither CET nor CEST set!\n" + \
                    "19: Is 1 instead of 0!\n" + \
                    "20: Is 0 instead of 1!\n" + \
                    "28: Even parity of minutes successful\n" + \
                    "35: Even parity of hours successful\n" + \
                    "21-27 & 29-34: Time: 00:00h\n" + \
                    "Error: Day is 00!\n" + \
                    "Error: Month is 00!\n" + \
                    "36-41 & 45-57: Date: ??.??.00\n" + \
                    "42-44: Weekday: Sunday\n" + \
                    "58: Parity of date and weekdays successful\n"
        self.assertEqual(objective, result)

        # positive test - bit 20 is wrongly set to 1
        bitstream = [0] + 6*[0] + 13*[0] + [1] + [0]*40
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0\n" + \
                    "07-12: Always zero\n" + \
                    "16: No clock change\n" + \
                    "17-18: Error: Neither CET nor CEST set!\n" + \
                    "20: Beginn of time information\n" + \
                    "28: Even parity of minutes successful\n" + \
                    "35: Even parity of hours successful\n" + \
                    "21-27 & 29-34: Time: 00:00h\n" + \
                    "Error: Day is 00!\n" + \
                    "Error: Month is 00!\n" + \
                    "36-41 & 45-57: Date: ??.??.00\n" + \
                    "42-44: Weekday: Sunday\n" + \
                    "58: Parity of date and weekdays successful\n"
        self.assertEqual(objective, result)

        # positive test - valid date and time
        bitstream = [0] + 2*[0] + 4*[1] + 6*[0] + 3*[0] + [0,1,0] + [0] + \
                    [1] + [0,1,0,0,1,0,1] + [1] + [1,0,0,0,1,0] + [0] + \
                    [1,1,0,0,1,0] + [0,1,1] + [1,0,1,0,0] + \
                    [1,1,0,0,0,1,0,0] + [0]
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0\n" + \
                    "07-12: Always zero\n" + \
                    "16: No clock change\n" + \
                    "17-18: CEST - summer time\n" + \
                    "20: Beginn of time information\n" + \
                    "28: Even parity of minutes successful\n" + \
                    "35: Even parity of hours successful\n" + \
                    "21-27 & 29-34: Time: 11:52h\n" + \
                    "36-41 & 45-57: Date: 13.05.23\n" + \
                    "42-44: Weekday: Saturday\n" + \
                    "58: Parity of date and weekdays successful\n"
        self.assertEqual(objective, result)

        # positive test - wrong parity at minutes
        bitstream = [0] + 2*[0] + 4*[1] + 6*[0] + 3*[0] + [0,1,0] + [0] + \
                    [1] + [0,1,0,0,1,0,1] + [0] + [1,0,0,0,1,0] + [0] + \
                    [1,1,0,0,1,0] + [0,1,1] + [1,0,1,0,0] + \
                    [1,1,0,0,0,1,0,0] + [0]
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0\n" + \
                    "07-12: Always zero\n" + \
                    "16: No clock change\n" + \
                    "17-18: CEST - summer time\n" + \
                    "20: Beginn of time information\n" + \
                    "28: Even parity of minutes failed\n" + \
                    "35: Even parity of hours successful\n" + \
                    "21-27 & 29-34: Time: 11:52h\n" + \
                    "36-41 & 45-57: Date: 13.05.23\n" + \
                    "42-44: Weekday: Saturday\n" + \
                    "58: Parity of date and weekdays successful\n"
        self.assertEqual(objective, result)

        # positive test - wrong parity at hours
        bitstream = [0] + 2*[0] + 4*[1] + 6*[0] + 3*[0] + [0,1,0] + [0] + \
                    [1] + [0,1,0,0,1,0,1] + [1] + [1,0,0,0,1,0] + [1] + \
                    [1,1,0,0,1,0] + [0,1,1] + [1,0,1,0,0] + \
                    [1,1,0,0,0,1,0,0] + [0]
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0\n" + \
                    "07-12: Always zero\n" + \
                    "16: No clock change\n" + \
                    "17-18: CEST - summer time\n" + \
                    "20: Beginn of time information\n" + \
                    "28: Even parity of minutes successful\n" + \
                    "35: Even parity of hours failed\n" + \
                    "21-27 & 29-34: Time: 11:52h\n" + \
                    "36-41 & 45-57: Date: 13.05.23\n" + \
                    "42-44: Weekday: Saturday\n" + \
                    "58: Parity of date and weekdays successful\n"
        self.assertEqual(objective, result)

        # negative test - invalid hour 1*digit and 10*digit
        bitstream = [0] + 2*[0] + 4*[1] + 6*[0] + 3*[0] + [0,1,0] + [0] + \
                    [1] + [0,1,0,0,1,0,1] + [1] + [1,1,1,1,1,1] + [0] + \
                    [1,1,0,0,1,0] + [0,1,1] + [1,0,1,0,0] + \
                    [1,1,0,0,0,1,0,0] + [0]
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0\n" + \
                    "07-12: Always zero\n" + \
                    "16: No clock change\n" + \
                    "17-18: CEST - summer time\n" + \
                    "20: Beginn of time information\n" + \
                    "28: Even parity of minutes successful\n" + \
                    "35: Even parity of hours successful\n" + \
                    "Error: 1*digit of hour is > 9!\n" + \
                    "Error: 10*digit of hour is > 2!\n" + \
                    "21-27 & 29-34: Time: ??:52h\n" + \
                    "36-41 & 45-57: Date: 13.05.23\n" + \
                    "42-44: Weekday: Saturday\n" + \
                    "58: Parity of date and weekdays successful\n"
        self.assertEqual(objective, result)

        # negative test - invalid hour 1*digit
        bitstream = [0] + 2*[0] + 4*[1] + 6*[0] + 3*[0] + [0,1,0] + [0] + \
                    [1] + [0,1,0,0,1,0,1] + [1] + [1,1,1,1,0,0] + [0] + \
                    [1,1,0,0,1,0] + [0,1,1] + [1,0,1,0,0] + \
                    [1,1,0,0,0,1,0,0] + [0]
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0\n" + \
                    "07-12: Always zero\n" + \
                    "16: No clock change\n" + \
                    "17-18: CEST - summer time\n" + \
                    "20: Beginn of time information\n" + \
                    "28: Even parity of minutes successful\n" + \
                    "35: Even parity of hours successful\n" + \
                    "Error: 1*digit of hour is > 9!\n" + \
                    "21-27 & 29-34: Time: 0?:52h\n" + \
                    "36-41 & 45-57: Date: 13.05.23\n" + \
                    "42-44: Weekday: Saturday\n" + \
                    "58: Parity of date and weekdays successful\n"
        self.assertEqual(objective, result)

        # negative test - invalid hour 10*digit
        bitstream = [0] + 2*[0] + 4*[1] + 6*[0] + 3*[0] + [0,1,0] + [0] + \
                    [1] + [0,1,0,0,1,0,1] + [1] + [0,0,0,0,1,1] + [0] + \
                    [1,1,0,0,1,0] + [0,1,1] + [1,0,1,0,0] + \
                    [1,1,0,0,0,1,0,0] + [0]
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0\n" + \
                    "07-12: Always zero\n" + \
                    "16: No clock change\n" + \
                    "17-18: CEST - summer time\n" + \
                    "20: Beginn of time information\n" + \
                    "28: Even parity of minutes successful\n" + \
                    "35: Even parity of hours successful\n" + \
                    "Error: 10*digit of hour is > 2!\n" + \
                    "21-27 & 29-34: Time: ?0:52h\n" + \
                    "36-41 & 45-57: Date: 13.05.23\n" + \
                    "42-44: Weekday: Saturday\n" + \
                    "58: Parity of date and weekdays successful\n"
        self.assertEqual(objective, result)

        # negative test - invalid hours above 23
        bitstream = [0] + 2*[0] + 4*[1] + 6*[0] + 3*[0] + [0,1,0] + [0] + \
                    [1] + [0,1,0,0,1,0,1] + [1] + [0,0,1,0,0,1] + [0] + \
                    [1,1,0,0,1,0] + [0,1,1] + [1,0,1,0,0] + \
                    [1,1,0,0,0,1,0,0] + [0]
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0\n" + \
                    "07-12: Always zero\n" + \
                    "16: No clock change\n" + \
                    "17-18: CEST - summer time\n" + \
                    "20: Beginn of time information\n" + \
                    "28: Even parity of minutes successful\n" + \
                    "35: Even parity of hours successful\n" + \
                    "Error: Hours are greater than 23!\n" + \
                    "21-27 & 29-34: Time: ??:52h\n" + \
                    "36-41 & 45-57: Date: 13.05.23\n" + \
                    "42-44: Weekday: Saturday\n" + \
                    "58: Parity of date and weekdays successful\n"
        self.assertEqual(objective, result)

        # negative test: - invalid minute 1*digit
        bitstream = [0] + 2*[0] + 4*[1] + 6*[0] + 3*[0] + [0,1,0] + [0] + \
                    [1] + [1,1,1,1,0,0,0] + [0] + [0,0,0,0,0,0] + [0] + \
                    [1,1,0,0,1,0] + [0,1,1] + [1,0,1,0,0] + \
                    [1,1,0,0,0,1,0,0] + [0]
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0\n" + \
                    "07-12: Always zero\n" + \
                    "16: No clock change\n" + \
                    "17-18: CEST - summer time\n" + \
                    "20: Beginn of time information\n" + \
                    "28: Even parity of minutes successful\n" + \
                    "35: Even parity of hours successful\n" + \
                    "Error: 1*digit of minute is > 9!\n" + \
                    "21-27 & 29-34: Time: 00:0?h\n" + \
                    "36-41 & 45-57: Date: 13.05.23\n" + \
                    "42-44: Weekday: Saturday\n" + \
                    "58: Parity of date and weekdays successful\n"
        self.assertEqual(objective, result)

        # negative test: - invalid minute 10*digit
        bitstream = [0] + 2*[0] + 4*[1] + 6*[0] + 3*[0] + [0,1,0] + [0] + \
                    [1] + [0,0,0,0,1,1,1] + [1] + [0,0,0,0,0,0] + [0] + \
                    [1,1,0,0,1,0] + [0,1,1] + [1,0,1,0,0] + \
                    [1,1,0,0,0,1,0,0] + [0]
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0\n" + \
                    "07-12: Always zero\n" + \
                    "16: No clock change\n" + \
                    "17-18: CEST - summer time\n" + \
                    "20: Beginn of time information\n" + \
                    "28: Even parity of minutes successful\n" + \
                    "35: Even parity of hours successful\n" + \
                    "Error: 10*digit of minute is > 5!\n" + \
                    "21-27 & 29-34: Time: 00:?0h\n" + \
                    "36-41 & 45-57: Date: 13.05.23\n" + \
                    "42-44: Weekday: Saturday\n" + \
                    "58: Parity of date and weekdays successful\n"
        self.assertEqual(objective, result)

        # negative test: - invalid minute 10*digit
        bitstream = [0] + 2*[0] + 4*[1] + 6*[0] + 3*[0] + [0,1,0] + [0] + \
                    [1] + [0,1,0,1,1,1,1] + [1] + [0,0,0,0,0,0] + [0] + \
                    [1,1,0,0,1,0] + [0,1,1] + [1,0,1,0,0] + \
                    [1,1,0,0,0,1,0,0] + [0]
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0\n" + \
                    "07-12: Always zero\n" + \
                    "16: No clock change\n" + \
                    "17-18: CEST - summer time\n" + \
                    "20: Beginn of time information\n" + \
                    "28: Even parity of minutes successful\n" + \
                    "35: Even parity of hours successful\n" + \
                    "Error: 10*digit of minute is > 5!\n" + \
                    "Error: 1*digit of minute is > 9!\n" + \
                    "21-27 & 29-34: Time: 00:??h\n" + \
                    "36-41 & 45-57: Date: 13.05.23\n" + \
                    "42-44: Weekday: Saturday\n" + \
                    "58: Parity of date and weekdays successful\n"
        self.assertEqual(objective, result)

        # negative test: - invalid weekday
        bitstream = [0] + 2*[0] + 4*[1] + 6*[0] + 3*[0] + [0,1,0] + [0] + \
                    [1] + [0,0,0,0,0,0,0] + [0] + [0,0,0,0,0,0] + [0] + \
                    [1,1,0,0,1,0] + [1,3,1] + [1,0,1,0,0] + \
                    [1,1,0,0,0,1,0,0] + [0]
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0\n" + \
                    "07-12: Always zero\n" + \
                    "16: No clock change\n" + \
                    "17-18: CEST - summer time\n" + \
                    "20: Beginn of time information\n" + \
                    "28: Even parity of minutes successful\n" + \
                    "35: Even parity of hours successful\n" + \
                    "21-27 & 29-34: Time: 00:00h\n" + \
                    "36-41 & 45-57: Date: 13.05.23\n" + \
                    "42-44: Error: Weekday is ?\n" + \
                    "58: Parity of date and weekdays is ?\n"
        self.assertEqual(objective, result)

        # positive test: - parity of date and weekdays failed
        bitstream = [0] + 2*[0] + 4*[1] + 6*[0] + 3*[0] + [0,1,0] + [0] + \
                    [1] + [0,0,0,0,0,0,0] + [0] + [0,0,0,0,0,0] + [0] + \
                    [1,1,0,0,1,0] + [1,1,1] + [1,0,1,0,0] + \
                    [1,1,0,0,0,1,0,0] + [0]
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0\n" + \
                    "07-12: Always zero\n" + \
                    "16: No clock change\n" + \
                    "17-18: CEST - summer time\n" + \
                    "20: Beginn of time information\n" + \
                    "28: Even parity of minutes successful\n" + \
                    "35: Even parity of hours successful\n" + \
                    "21-27 & 29-34: Time: 00:00h\n" + \
                    "36-41 & 45-57: Date: 13.05.23\n" + \
                    "42-44: Weekday: Sunday\n" + \
                    "58: Parity of date and weekdays failed\n"
        self.assertEqual(objective, result)

        # negative test - error in hour value
        bitstream = [0] + 2*[0] + 4*[1] + 6*[0] + 3*[0] + [0,1,0] + [0] + \
                    [1] + [0,1,0,0,1,0,1] + [1] + [1,0,3,0,1,0] + [0] + \
                    [1,1,0,0,1,0] + [0,1,1] + [1,0,1,0,0] + \
                    [1,1,0,0,0,1,0,0] + [0]
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0\n" + \
                    "07-12: Always zero\n" + \
                    "16: No clock change\n" + \
                    "17-18: CEST - summer time\n" + \
                    "20: Beginn of time information\n" + \
                    "28: Even parity of minutes successful\n" + \
                    "35: Even parity of hours is ?\n" + \
                    "21-27 & 29-34: Time: 1?:52h\n" + \
                    "36-41 & 45-57: Date: 13.05.23\n" + \
                    "42-44: Weekday: Saturday\n" + \
                    "58: Parity of date and weekdays successful\n"
        self.assertEqual(objective, result)

        # negative test - error in minute value
        bitstream = [0] + 2*[0] + 4*[1] + 6*[0] + 3*[0] + [0,1,0] + [0] + \
                    [1] + [0,1,3,0,1,0,1] + [1] + [1,0,1,0,1,0] + [1] + \
                    [1,1,0,0,1,0] + [0,1,1] + [1,0,1,0,0] + \
                    [1,1,0,0,0,1,0,0] + [0]
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0\n" + \
                    "07-12: Always zero\n" + \
                    "16: No clock change\n" + \
                    "17-18: CEST - summer time\n" + \
                    "20: Beginn of time information\n" + \
                    "28: Even parity of minutes is ?\n" + \
                    "35: Even parity of hours successful\n" + \
                    "21-27 & 29-34: Time: 15:5?h\n" + \
                    "36-41 & 45-57: Date: 13.05.23\n" + \
                    "42-44: Weekday: Saturday\n" + \
                    "58: Parity of date and weekdays successful\n"
        self.assertEqual(objective, result)

        # negative test - error in start-bit
        bitstream = [3] + 2*[0] + 4*[1] + 6*[0] + 3*[0] + [0,1,0] + [0] + \
                    [1] + [0,1,3,0,1,0,1] + [1] + [1,0,1,0,1,0] + [1] + \
                    [1,1,0,0,1,0] + [0,1,1] + [1,0,1,0,0] + \
                    [1,1,0,0,0,1,0,0] + [0]
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is ?!\n" + \
                    "07-12: Always zero\n" + \
                    "16: No clock change\n" + \
                    "17-18: CEST - summer time\n" + \
                    "20: Beginn of time information\n" + \
                    "28: Even parity of minutes is ?\n" + \
                    "35: Even parity of hours successful\n" + \
                    "21-27 & 29-34: Time: 15:5?h\n" + \
                    "36-41 & 45-57: Date: 13.05.23\n" + \
                    "42-44: Weekday: Saturday\n" + \
                    "58: Parity of date and weekdays successful\n"
        self.assertEqual(objective, result)

        # negative test: - invalid day 1*digit
        bitstream = [0] + 2*[0] + 4*[1] + 6*[0] + 3*[0] + [0,1,0] + [0] + \
                    [1] + [0,0,0,0,0,0,0] + [0] + [0,0,0,0,0,0] + [0] + \
                    [1,1,1,1,0,0] + [0,1,1] + [1,0,1,0,0] + \
                    [1,1,0,0,0,1,0,0] + [1]
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0\n" + \
                    "07-12: Always zero\n" + \
                    "16: No clock change\n" + \
                    "17-18: CEST - summer time\n" + \
                    "20: Beginn of time information\n" + \
                    "28: Even parity of minutes successful\n" + \
                    "35: Even parity of hours successful\n" + \
                    "21-27 & 29-34: Time: 00:00h\n" + \
                    "Error: 1*digit of day is > 9!\n" + \
                    "36-41 & 45-57: Date: 0?.05.23\n" + \
                    "42-44: Weekday: Saturday\n" + \
                    "58: Parity of date and weekdays successful\n"
        self.assertEqual(objective, result)

        # negative test: - invalid day > 33
        bitstream = [0] + 2*[0] + 4*[1] + 6*[0] + 3*[0] + [0,1,0] + [0] + \
                    [1] + [0,0,0,0,0,0,0] + [0] + [0,0,0,0,0,0] + [0] + \
                    [1,1,1,1,1,1] + [0,1,1] + [1,0,1,0,0] + \
                    [1,1,0,0,0,1,0,0] + [1]
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0\n" + \
                    "07-12: Always zero\n" + \
                    "16: No clock change\n" + \
                    "17-18: CEST - summer time\n" + \
                    "20: Beginn of time information\n" + \
                    "28: Even parity of minutes successful\n" + \
                    "35: Even parity of hours successful\n" + \
                    "21-27 & 29-34: Time: 00:00h\n" + \
                    "Error: Day is > 31!\n" + \
                    "36-41 & 45-57: Date: ??.05.23\n" + \
                    "42-44: Weekday: Saturday\n" + \
                    "58: Parity of date and weekdays successful\n"
        self.assertEqual(objective, result)

        # negative test: - invalid month 1*digit
        bitstream = [0] + 2*[0] + 4*[1] + 6*[0] + 3*[0] + [0,1,0] + [0] + \
                    [1] + [0,0,0,0,0,0,0] + [0] + [0,0,0,0,0,0] + [0] + \
                    [1,0,0,0,0,0] + [0,1,1] + [1,1,1,1,0] + \
                    [1,1,0,0,0,1,0,0] + [0]
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0\n" + \
                    "07-12: Always zero\n" + \
                    "16: No clock change\n" + \
                    "17-18: CEST - summer time\n" + \
                    "20: Beginn of time information\n" + \
                    "28: Even parity of minutes successful\n" + \
                    "35: Even parity of hours successful\n" + \
                    "21-27 & 29-34: Time: 00:00h\n" + \
                    "Error: 1*digit of month is > 9!\n" + \
                    "36-41 & 45-57: Date: 01.0?.23\n" + \
                    "42-44: Weekday: Saturday\n" + \
                    "58: Parity of date and weekdays successful\n"
        self.assertEqual(objective, result)

        # negative test: - invalid month > 12
        bitstream = [0] + 2*[0] + 4*[1] + 6*[0] + 3*[0] + [0,1,0] + [0] + \
                    [1] + [0,0,0,0,0,0,0] + [0] + [0,0,0,0,0,0] + [0] + \
                    [1,0,0,0,0,0] + [0,1,1] + [1,1,1,1,1] + \
                    [1,1,0,0,0,1,0,0] + [1]
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0\n" + \
                    "07-12: Always zero\n" + \
                    "16: No clock change\n" + \
                    "17-18: CEST - summer time\n" + \
                    "20: Beginn of time information\n" + \
                    "28: Even parity of minutes successful\n" + \
                    "35: Even parity of hours successful\n" + \
                    "21-27 & 29-34: Time: 00:00h\n" + \
                    "Error: Month is > 12!\n" + \
                    "36-41 & 45-57: Date: 01.??.23\n" + \
                    "42-44: Weekday: Saturday\n" + \
                    "58: Parity of date and weekdays successful\n"
        self.assertEqual(objective, result)

        # negative test: - invalid year 1*digit
        bitstream = [0] + 2*[0] + 4*[1] + 6*[0] + 3*[0] + [0,1,0] + [0] + \
                    [1] + [0,0,0,0,0,0,0] + [0] + [0,0,0,0,0,0] + [0] + \
                    [1,0,0,0,0,0] + [0,1,1] + [1,0,0,0,0] + \
                    [1,1,1,1,0,0,0,0] + [0]
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0\n" + \
                    "07-12: Always zero\n" + \
                    "16: No clock change\n" + \
                    "17-18: CEST - summer time\n" + \
                    "20: Beginn of time information\n" + \
                    "28: Even parity of minutes successful\n" + \
                    "35: Even parity of hours successful\n" + \
                    "21-27 & 29-34: Time: 00:00h\n" + \
                    "Error: 1*digit of year is > 9!\n" + \
                    "36-41 & 45-57: Date: 01.01.0?\n" + \
                    "42-44: Weekday: Saturday\n" + \
                    "58: Parity of date and weekdays successful\n"
        self.assertEqual(objective, result)

        # negative test: - invalid year 10*digit
        bitstream = [0] + 2*[0] + 4*[1] + 6*[0] + 3*[0] + [0,1,0] + [0] + \
                    [1] + [0,0,0,0,0,0,0] + [0] + [0,0,0,0,0,0] + [0] + \
                    [1,0,0,0,0,0] + [0,1,1] + [1,0,0,0,0] + \
                    [0,0,0,0,1,1,1,1] + [0]
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0\n" + \
                    "07-12: Always zero\n" + \
                    "16: No clock change\n" + \
                    "17-18: CEST - summer time\n" + \
                    "20: Beginn of time information\n" + \
                    "28: Even parity of minutes successful\n" + \
                    "35: Even parity of hours successful\n" + \
                    "21-27 & 29-34: Time: 00:00h\n" + \
                    "Error: 10*digit of year is > 9!\n" + \
                    "36-41 & 45-57: Date: 01.01.?0\n" + \
                    "42-44: Weekday: Saturday\n" + \
                    "58: Parity of date and weekdays successful\n"
        self.assertEqual(objective, result)

        # negative test: - invalid year 10*digit
        bitstream = [0] + 2*[0] + 4*[1] + 6*[0] + 3*[0] + [0,1,0] + [0] + \
                    [1] + [0,0,0,0,0,0,0] + [0] + [0,0,0,0,0,0] + [0] + \
                    [1,0,0,0,0,0] + [0,1,1] + [1,0,0,0,0] + \
                    [1,1,1,1,1,1,1,1] + [0]
        result = self.my_decoder.decode_bitstream(bitstream, 60)
        objective = "\n00: Start-bit is 0\n" + \
                    "07-12: Always zero\n" + \
                    "16: No clock change\n" + \
                    "17-18: CEST - summer time\n" + \
                    "20: Beginn of time information\n" + \
                    "28: Even parity of minutes successful\n" + \
                    "35: Even parity of hours successful\n" + \
                    "21-27 & 29-34: Time: 00:00h\n" + \
                    "Error: Year is > 99!\n" + \
                    "36-41 & 45-57: Date: 01.01.??\n" + \
                    "42-44: Weekday: Saturday\n" + \
                    "58: Parity of date and weekdays successful\n"
        self.assertEqual(objective, result)


if __name__ == '__main__':
    testInstance = Test_Class_DecodeALS162()
    unittest.main()
