# -*- coding: iso-8859-1 -*-

import zmq
import numpy as np


class Class_DecodeALS162():

    def __init__(self):
        self.weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday",
                         "Friday", "Saturday", "Sunday"]

    def decode_BCD4(self, bits):
        list1 = [bits[0], bits[1], bits[2], bits[3]]
        if 3 in list1:
            return "?"

        str1 = ''.join(str(e) for e in list1)
        val = int(str1, 2)

        return val

    def decode_BCD2(self, bits):
        list1 = [bits[0], bits[1]]
        if 3 in list1:
            return "?"

        str1 = ''.join(str(e) for e in list1)
        val = int(str1, 2)

        return val

    def decode_BCD3(self, bits):
        list1 = [bits[0], bits[1], bits[2]]
        if 3 in list1:
            return "?"

        str1 = ''.join(str(e) for e in list1)
        val = int(str1, 2)

        return val

    def decode_bitstream(self, bitstream, count):
        output = ""

        if count > 60:
            output += f"Decoding error\nReceived bits: {len(bitstream)}\n"
            return output

        output += "\n"

        if bitstream[0] == 1:
            output += "00: Start-bit is 1 instead of 0!\n"
        elif bitstream[0] == 0:
            output += f"00: Start-bit is {bitstream[0]}\n"
        elif bitstream[0] == 3:
            output += "00: Start-bit is ?!\n"

        # TBD leap second
        # TBD evaluate and check correctness of Hamming weight
        # TBD check for error value 3 in the following bits

        if (bitstream[7] or bitstream[8] or bitstream[9] or
                bitstream[10] or bitstream[11] or bitstream[12] == 1):
            output += "07-12: At least one bit is 1 instead of 0!\n"
        else:
            output += "07-12: Always zero\n"

        if bitstream[13] == 1:
            output += "13: The following day is a holiday\n"

        if bitstream[14] == 1:
            output += "14: The current day is a holiday\n"

        if bitstream[16] == 1:
            output += "16: Clock change\n"
        elif bitstream[16] == 0:
            output += "16: No clock change\n"

        if bitstream[17] == 0 and bitstream[18] == 1:
            output += "17-18: CET - winter time\n"
        elif bitstream[17] == 1 and bitstream[18] == 0:
            output += "17-18: CEST - summer time\n"
        else:
            output += "17-18: Error: Neither CET nor CEST set!\n"

        if bitstream[19] == 1:
            output += "19: Is 1 instead of 0!\n"

        if bitstream[20] == 1:
            output += "20: Begin of time information\n"

        elif bitstream[20] == 0:
            output += "20: Is 0 instead of 1!\n"

        min_dec0 = self.decode_BCD4([bitstream[24], bitstream[23],
                                    bitstream[22], bitstream[21]])

        min_dec10 = self.decode_BCD3([bitstream[27], bitstream[26],
                                     bitstream[25]])

        # check parity for the minute values
        if 3 not in bitstream[21:29]:
            if (bitstream[21] ^ bitstream[22] ^ bitstream[23] ^
                    bitstream[24] ^ bitstream[25] ^ bitstream[26] ^
                    bitstream[27] ^ bitstream[28] == 0):
                output += "28: Even parity of minutes successful\n"
            else:
                output += "28: Even parity of minutes failed\n"

        else:
            output += "28: Even parity of minutes is ?\n"

        hour_dec0 = self.decode_BCD4([bitstream[32], bitstream[31],
                                      bitstream[30], bitstream[29]])

        hour_dec10 = self.decode_BCD2([bitstream[34], bitstream[33]])

        # check parity for the hour values
        if 3 not in bitstream[29:36]:
            if (bitstream[29] ^ bitstream[30] ^ bitstream[31] ^ bitstream[32] ^
                    bitstream[33] ^ bitstream[34] ^ bitstream[35] == 0):
                output += "35: Even parity of hours successful\n"
            else:
                output += "35: Even parity of hours failed\n"
        else:
            output += "35: Even parity of hours is ?\n"

        # check minute values
        if min_dec0 != "?" and min_dec10 != "?":
            if min_dec0 > 9 and min_dec10 <= 5:
                output += "Error: 1*digit of minute is > 9!\n"
                min_dec0 = "?"

            elif min_dec10 > 5 and min_dec0 <= 9:
                output += "Error: 10*digit of minute is > 5!\n"
                min_dec10 = "?"

            elif min_dec10 > 5 and min_dec0 > 9:
                output += "Error: 10*digit of minute is > 5!\n"
                output += "Error: 1*digit of minute is > 9!\n"
                min_dec0 = "?"
                min_dec10 = "?"
        else:
            output += "Error: Minute is ?\n"

        # check hour values
        if hour_dec0 != "?" and hour_dec10 != "?":
            if hour_dec10 == 2 and hour_dec0 > 3:
                output += "Error: Hours are greater than 23!\n"
                hour_dec0 = "?"
                hour_dec10 = "?"

            elif (hour_dec0 > 9 and hour_dec10 <= 2):
                output += "Error: 1*digit of hour is > 9!\n"
                hour_dec0 = "?"

            elif (hour_dec10 > 2 and hour_dec0 <= 9):
                output += "Error: 10*digit of hour is > 2!\n"
                hour_dec10 = "?"

            elif (hour_dec10 > 2 and hour_dec0 > 9):
                output += "Error: 1*digit of hour is > 9!\n"
                output += "Error: 10*digit of hour is > 2!\n"
                hour_dec0 = "?"
                hour_dec10 = "?"
        else:
            output += "Error: Hour is ?\n"

        output += f"21-27 & 29-34: Time: {hour_dec10}{hour_dec0}:" + \
                  f"{min_dec10}{min_dec0}h\n"

        weekday = self.decode_BCD3([bitstream[44], bitstream[43],
                                    bitstream[42]])

        day_dec0 = self.decode_BCD4([bitstream[39], bitstream[38],
                                     bitstream[37], bitstream[36]])
        day_dec10 = self.decode_BCD2([bitstream[41], bitstream[40]])

        month_dec0 = self.decode_BCD4([bitstream[48], bitstream[47],
                                       bitstream[46], bitstream[45]])
        month_dec10 = bitstream[49]

        year_dec0 = self.decode_BCD4([bitstream[53], bitstream[52],
                                     bitstream[51], bitstream[50]])
        year_dec10 = self.decode_BCD4([bitstream[57], bitstream[56],
                                      bitstream[55], bitstream[54]])

        # check date values day
        if day_dec0 != "?" and day_dec10 != "?":
            if day_dec0 == 0 and day_dec10 == 0:
                output += "Error: Day is 00!\n"
                day_dec0 = "?"
                day_dec10 = "?"

            elif day_dec0 > 9 and day_dec10 < 3:
                output += "Error: 1*digit of day is > 9!\n"
                day_dec0 = "?"

            elif day_dec10 == 3 and day_dec0 >= 2:
                output += "Error: Day is > 31!\n"
                day_dec0 = "?"
                day_dec10 = "?"
        else:
            output += "Error: Day is ?\n"

        # check date values month
        if month_dec0 != "?" and month_dec10 != "?":
            if month_dec0 == 0 and month_dec10 == 0:
                output += "Error: Month is 00!\n"
                month_dec0 = "?"
                month_dec10 = "?"

            elif month_dec0 > 9 and month_dec10 < 1:
                output += "Error: 1*digit of month is > 9!\n"
                month_dec0 = "?"

            elif month_dec10 == 1 and month_dec0 >= 3:
                output += "Error: Month is > 12!\n"
                month_dec0 = "?"
                month_dec10 = "?"
        else:
            output += "Error: Month is ?\n"

        # check date values year
        if year_dec0 != "?" and year_dec10 != "?":
            if year_dec0 > 9 and year_dec10 <= 9:
                output += "Error: 1*digit of year is > 9!\n"
                year_dec0 = "?"

            if year_dec10 > 9 and year_dec0 <= 1:
                output += "Error: 10*digit of year is > 9!\n"
                year_dec10 = "?"

            elif year_dec10 > 9 and year_dec0 > 9:
                output += "Error: Year is > 99!\n"
                year_dec0 = "?"
                year_dec10 = "?"
        else:
            output += "Error: Year is ?\n"

        output += f"36-41 & 45-57: Date: {day_dec10}{day_dec0}." +\
                  f"{month_dec10}{month_dec0}.{year_dec10}{year_dec0}\n"

        if weekday != "?":
            output += f"42-44: Weekday: {self.weekdays[weekday-1]}\n"
        else:
            output += "42-44: Error: Weekday is ?\n"

        # check parity for the date and weekday values
        if 3 not in bitstream[36:58]:
            if (bitstream[36] ^ bitstream[37] ^ bitstream[38] ^
                    bitstream[39] ^ bitstream[40] ^ bitstream[41] ^
                    bitstream[42] ^ bitstream[43] ^ bitstream[44] ^
                    bitstream[45] ^ bitstream[46] ^ bitstream[47] ^
                    bitstream[48] ^ bitstream[49] ^ bitstream[50] ^
                    bitstream[51] ^ bitstream[52] ^ bitstream[53] ^
                    bitstream[54] ^ bitstream[55] ^ bitstream[56] ^
                    bitstream[57] ^ bitstream[58] == 0):
                output += "58: Parity of date and weekdays successful\n"
            else:
                output += "58: Parity of date and weekdays failed\n"

        else:
            output += "58: Parity of date and weekdays is ?\n"

        # count number of errors in current bitstream
        error_list = [1 for idx, val in enumerate(bitstream) if val == 3]
        num_errors = np.sum(error_list)

        # get index of each error in curent bitstream
        error_pos = [idx for idx, val in enumerate(bitstream) if val == 3]

        if num_errors > 0:
            output += f"# Bit errors: {num_errors} =>" + \
                      f"at postions: {error_pos}\n"

        return output

    def consumer(self):
        context = zmq.Context()

        consumer_receiver = context.socket(zmq.PULL)
        consumer_receiver.connect("tcp://127.0.0.1:55555")

        bitstream = []
        count = 1

        while True:
            data = consumer_receiver.recv()
            received_msg = data.decode('ascii')[3:]

            count += 1
            print(f"decoded bit at {count:02}: {received_msg[0]} " +
                  f"at position: {received_msg[3:5]}")
            position = int(received_msg[3:5], 10)

            # fill up error symbols
            if count < position:
                print(f"{position-count} bit(s) lost before " +
                      f"position: {received_msg[3:5]}")
                for i in range(0, position-count):
                    bitstream.append(3)

            if (received_msg[0] == "0"):
                bitstream.append(0)
                count = position

            elif (received_msg[0] == "1"):
                bitstream.append(1)
                count = position

            # derive current time and date from the bitstream
            elif (received_msg[0] == "2" and count == 60):
                bitstream.append(0)

                output = self.decode_bitstream(bitstream, count)
                print(output)

                bitstream = []
                count = position
                continue

            # either too few or too many bits have
            # been received during the decoding step
            elif (received_msg[0] == "2" and count != 60):
                print("Error: Wrong number of bits at new minute")
                print(f"#Bits: {len(bitstream)}")

                bitstream = []
                count = 1
                continue

            if count > 61:
                print("Error: more than 60 bits counted: Reinit Counter.")
                bitstream = []
                count = 1
