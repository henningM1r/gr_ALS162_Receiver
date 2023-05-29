# -*- coding: iso-8859-1 -*-

import zmq
import numpy as np
import re


class Class_DecodeALS162():

    def __init__(self):
        self.weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday",
                         "Friday", "Saturday", "Sunday"]

    def decode_BCD(self, bits, length):
        list1 = [bits[i] for i in range(0, length)]
        if 3 in list1:
            return "?"

        str1 = ''.join(str(e) for e in list1)
        val = int(str1, 2)

        return val

    def compute_num_errors(self, bitstream):
        error_list = [1 for idx, val in enumerate(bitstream) if val == 3]
        num_errors = np.sum(error_list)

        return num_errors

    def compute_error_pos(self, bitstream):
        error_pos = [idx for idx, val in enumerate(bitstream) if val == 3]

        return error_pos

    def single_error_correction(self, bitstream):
        num_errors = self.compute_num_errors(bitstream)

        if num_errors == 1:
            rel_error_pos = self.compute_error_pos(bitstream)

            # no correction on default
            corr_val = 3

            if rel_error_pos[0] <= len(bitstream)-1:
                # binary addition of all bits except for the error
                sum = np.sum(bitstream) - bitstream[rel_error_pos[0]]

                # corrected value must yield an even parity in total
                corr_val = sum % 2
                bitstream[rel_error_pos[0]] = corr_val

            return [bitstream, rel_error_pos[0], corr_val]

        return [bitstream, -1, -1]

    def decode_bitstream(self, bitstream, count):
        output = ""

        if count > 60:
            output += f"Decoding error\nReceived bits: {len(bitstream)}\n"
            return output

        output += "\n"

        if bitstream[0] == 1:
            output += "00: Start-bit is 1 instead of 0!\n"
        elif bitstream[0] == 0:
            output += f"00: Start-bit is 0.\n"
        elif bitstream[0] == 3:
            output += "00: Start-bit is ?.\n"

        # leap second
        if bitstream[1] == 1 and bitstream[2] == 0:
            output += "01: Positive leap second warning.\n"
        elif bitstream[2] == 1 and bitstream[1] == 0:
            output += "02: Negative leap second warning.\n"
        elif bitstream[2] == 1 and bitstream[2] == 1:
            output += "01-02: Error: Both leap seconds are set!\n"
        elif bitstream[2] == 0 and bitstream[2] == 0:
            output += "0-02: No leap second.\n"
        else:
            output += "01-02: Error: Leap second is ?.\n"

        # evaluate and check correctness of Hamming weight
        if 3 not in bitstream[3:7]:
            decoded_hamming_weight = bitstream[3] * 2 + bitstream[4] * 4 + \
                                     bitstream[5] * 8 + bitstream[6] * 16

            num_ones = [1 for idx, val in enumerate(bitstream[21:59]) \
                        if val == 1]
            hamming_weight = np.sum(num_ones)

            if hamming_weight == decoded_hamming_weight:
                output += "03-06: Decoded & computed Hamming weights " + \
                         f"match for bits 21-58: " + \
                         f"{decoded_hamming_weight} == " + \
                         f"{hamming_weight}.\n"
            else:
                output += "03-06: Error: Decoded & computed Hamming " + \
                         f"weights missmatch for bits 21-58: " + \
                         f"{decoded_hamming_weight} != " + \
                         f"{hamming_weight}!\n"

            if hamming_weight % 2 != 0:
                output += "03-06: Error: Hamming weight for bits " + \
                          "21-58 is not even!\n"

        else:
            output += "03-06: Error: Hamming weight is ?.\n"

        if (bitstream[7] == 1 or bitstream[8] == 1 or bitstream[9] == 1 or
                bitstream[10] == 1 or bitstream[11] or bitstream[12] == 1):
            output += "07-12: At least one bit is 1 instead of 0!\n"
        elif (bitstream[7] == 0 and bitstream[8] == 0 and bitstream[9] == 0 and
                bitstream[10] == 0 and bitstream[11] == 0 and bitstream[12] == 0):
            output += "07-12: All zero.\n"
        elif 3 in bitstream[7:13]:
            output += "07-12: Contains errors\n"

        if bitstream[13] == 1:
            output += "13: The following day is a holiday.\n"
        elif bitstream[13] == 3:
            output += "13: Contains an error.\n"

        if bitstream[14] == 1:
            output += "14: The current day is a holiday.\n"
        elif bitstream[14] == 3:
            output += "14: Contains an error.\n"

        if bitstream[16] == 1:
            output += "16: Clock change\n"
        elif bitstream[16] == 0:
            output += "16: No clock change\n"
        elif bitstream[16] == 3:
            output += "16: Contains an error.\n"

        # TBD check for error value 3 in the following bits
        if bitstream[17] == 0 and bitstream[18] == 1:
            output += "17-18: CET - winter time.\n"
        elif bitstream[17] == 1 and bitstream[18] == 0:
            output += "17-18: CEST - summer time.\n"
        elif ((bitstream[17] == 0 and bitstream[18] == 0) or
             (bitstream[17] == 1 and bitstream[18] == 1)):
            output += "17-18: Error: Neither CET nor CEST set!\n"
        else:
            output += "17-18: Contains errors\n"

        if bitstream[19] == 1:
            output += "19: Is 1 instead of 0!\n"
        elif bitstream[19] == 3:
            output += "19: Contains an error.\n"

        if bitstream[20] == 1:
            output += "20: Begin of time information.\n"
        elif bitstream[20] == 0:
            output += "20: Is 0 instead of 1!\n"

        # check parity for the minute values
        if 3 not in bitstream[21:29]:
            if (bitstream[21] ^ bitstream[22] ^ bitstream[23] ^
                    bitstream[24] ^ bitstream[25] ^ bitstream[26] ^
                    bitstream[27] ^ bitstream[28] == 0):
                output += "28: Even parity of minutes successful.\n"
            else:
                output += "28: Even parity of minutes failed.\n"
        else:
            num_errors = self.compute_num_errors(bitstream[21:29])

            if num_errors == 1:
                [bitstream[21:29], rel_err_pos, corr_val] = self.single_error_correction(bitstream=bitstream[21:29])
                output += f"Corrected single error at {21 + rel_err_pos}.\n"
            else:
                output += "28: Even parity of minutes is ?.\n"

        min_dec0 = self.decode_BCD([bitstream[24], bitstream[23],
                                    bitstream[22], bitstream[21]], 4)

        min_dec10 = self.decode_BCD([bitstream[27], bitstream[26],
                                     bitstream[25]], 3)

        # check parity for the hour values
        if 3 not in bitstream[29:36]:
            if (bitstream[29] ^ bitstream[30] ^ bitstream[31] ^ bitstream[32] ^
                    bitstream[33] ^ bitstream[34] ^ bitstream[35] == 0):
                output += "35: Even parity of hours successful.\n"
            else:
                output += "35: Even parity of hours failed.\n"
        else:
            num_errors = self.compute_num_errors(bitstream[29:36])

            if num_errors == 1:
                [bitstream[29:36], rel_err_pos, corr_val] = self.single_error_correction(bitstream=bitstream[29:36])
                output += f"Corrected single error at {29 + rel_err_pos}.\n"
            else:
                output += "35: Even parity of hours is ?.\n"

        hour_dec0 = self.decode_BCD([bitstream[32], bitstream[31],
                                     bitstream[30], bitstream[29]], 4)

        hour_dec10 = self.decode_BCD([bitstream[34], bitstream[33]], 2)

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
            output += "Error: Minute is ?.\n"

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
            output += "Error: Hour is ?.\n"

        output += f"21-27 & 29-34: Time: {hour_dec10}{hour_dec0}:" + \
                  f"{min_dec10}{min_dec0}h.\n"

        # single bit error correction over bits 36-57 for date and weekday
        num_errors = self.compute_num_errors(bitstream[36:59])
        [bitstream[36:59], rel_err_pos, corr_val] = self.single_error_correction(bitstream=bitstream[36:59])
        if corr_val != -1:
            output += f"Corrected single error at {36 + rel_err_pos}.\n"
        elif corr_val == -1:
            pass
        else:
            output += "58: Even parity of of date and weekdays is ?.\n"

        weekday = self.decode_BCD([bitstream[44], bitstream[43],
                                   bitstream[42]], 3)

        day_dec0 = self.decode_BCD([bitstream[39], bitstream[38],
                                    bitstream[37], bitstream[36]], 4)
        day_dec10 = self.decode_BCD([bitstream[41], bitstream[40]], 2)

        month_dec0 = self.decode_BCD([bitstream[48], bitstream[47],
                                      bitstream[46], bitstream[45]], 4)
        month_dec10 = bitstream[49]

        year_dec0 = self.decode_BCD([bitstream[53], bitstream[52],
                                     bitstream[51], bitstream[50]], 4)
        year_dec10 = self.decode_BCD([bitstream[57], bitstream[56],
                                      bitstream[55], bitstream[54]], 4)

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
            output += "Error: Day is ?.\n"

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
            output += "Error: Month is ?.\n"

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
            output += "Error: Year is ?.\n"

        output += f"36-41 & 45-57: Date: {day_dec10}{day_dec0}." +\
                  f"{month_dec10}{month_dec0}.{year_dec10}{year_dec0}.\n"

        if weekday != "?":
            output += f"42-44: Weekday: {self.weekdays[weekday-1]}.\n"
        else:
            output += "42-44: Error: Weekday is ?.\n"

        # check parity for the date and weekday values
        if 3 not in bitstream[36:59]:
            if (bitstream[36] ^ bitstream[37] ^ bitstream[38] ^
                    bitstream[39] ^ bitstream[40] ^ bitstream[41] ^
                    bitstream[42] ^ bitstream[43] ^ bitstream[44] ^
                    bitstream[45] ^ bitstream[46] ^ bitstream[47] ^
                    bitstream[48] ^ bitstream[49] ^ bitstream[50] ^
                    bitstream[51] ^ bitstream[52] ^ bitstream[53] ^
                    bitstream[54] ^ bitstream[55] ^ bitstream[56] ^
                    bitstream[57] ^ bitstream[58] == 0):
                output += "58: Parity of date and weekdays successful.\n"
            else:
                output += "58: Parity of date and weekdays failed.\n"
        else:
            output += "58: Parity of date and weekdays is ?.\n"

        # count number of errors in current bitstream
        num_errors = self.compute_num_errors(bitstream)

        # get indices of each error in current bitstream
        error_pos = self.compute_error_pos(bitstream)
        #error_pos = [idx for idx, val in enumerate(bitstream) if val == 3]

        if num_errors > 0:
            output += f"# Bit errors: {num_errors} => " + \
                      f"at positions: {error_pos}.\n"

        return output

    def consumer(self):
        context = zmq.Context()

        consumer_receiver = context.socket(zmq.PULL)
        consumer_receiver.connect("tcp://127.0.0.1:55555")

        bitstream = []
        count = -1

        while True:
            data = consumer_receiver.recv()
            received_msg = data.decode('ascii')[3:]

            # for testing only
            if received_msg == "___EOT":
                consumer_receiver.close()
                context.term()
                return

            count += 1
            print(f"decoded bit at {count:02}: {received_msg[0]} " +
                  f"at position: {received_msg[3:5]}")

            if (not (received_msg[0] == "0" or
                     received_msg[0] == "1" or
                     received_msg[0] == "2" or
                     received_msg[0] == "3")):
                print(f"Error: received message \"{received_msg[0]}\" for time codeword is not permitted!")
                continue

            regex = "\d{2}"
            match = re.findall(regex, received_msg[3:5])
            if (not match):
                print(f"Error: received message \"{received_msg[3:5]}\" for position codeword is not permitted!")
                continue

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
                print("Error: Wrong number of bits at new minute!")
                print(f"#Bits: {len(bitstream)}")

                bitstream = []
                count = 1
                continue

            # NOTE this case should not occur anyway
            if count > 61:
                print("Error: more than 60 bits counted: Reinit Counter.")
                bitstream = []
                count = 1
