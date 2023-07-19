# -*- coding: iso-8859-1 -*-

import zmq
import numpy as np
import re


class Class_DecodeALS162():

    def __init__(self):
        self.weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday",
                         "Friday", "Saturday", "Sunday"]

    def decode_BCD(self, bits, length):
        if length != len(bits):
            # lengths missmatch
            return "?"

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
        out_bitstream = bitstream.copy()
        num_errors = self.compute_num_errors(out_bitstream)

        if num_errors == 1:
            rel_error_pos = self.compute_error_pos(out_bitstream)

            # no correction on default
            corr_val = 3

            if rel_error_pos[0] <= len(out_bitstream)-1:
                # binary addition of all bits except for the error
                sum_val = np.sum(out_bitstream) - \
                          out_bitstream[rel_error_pos[0]]

                # corrected value must yield an even parity in total
                corr_val = sum_val % 2
                out_bitstream[rel_error_pos[0]] = corr_val

            return [out_bitstream, rel_error_pos[0], corr_val]

        return [out_bitstream, -1, -1]

    def decode_startbit(self, bit):
        output = ""

        if bit == 1:
            output += "00: ERROR: Start-bit is 1 instead of 0!\n"
        elif bit == 0:
            output += "00: Start-bit is 0.\n"
        elif bit == 3:
            output += "00: ERROR: Start-bit is ?.\n"

        return output

    def decode_leap_second(self, bits):
        output = ""

        if bits[0] == 1 and bits[1] == 0:
            output += "01: Positive leap second warning.\n"
        elif bits[1] == 1 and bits[0] == 0:
            output += "02: Negative leap second warning.\n"
        elif bits[0] == 1 and bits[1] == 1:
            output += "01-02: ERROR: Both leap seconds are set!\n"
        elif bits[0] == 0 and bits[1] == 0:
            output += "01-02: No leap second.\n"
        else:
            output += "01-02: ERROR: Leap second is ?.\n"

        return output

    def check_hamming_weight(self, bitstream):
        output = ""

        if 3 in bitstream[21:59]:
            output += "03-06: ERROR: Bits 21-58 contain erroneous bits.\n"
            return output

        if 3 not in bitstream[3:7]:
            decoded_hamming_weight = bitstream[3] * 2 + bitstream[4] * 4 + \
                                     bitstream[5] * 8 + bitstream[6] * 16

            num_ones = [1 for idx, val in enumerate(bitstream[21:59])
                        if val == 1]
            hamming_weight = np.sum(num_ones)

            if hamming_weight == decoded_hamming_weight:
                output += "03-06: Decoded & computed Hamming weights " + \
                          "match for bits 21-58: " + \
                          f"{decoded_hamming_weight} == " + \
                          f"{hamming_weight}.\n"
            else:
                output += "03-06: ERROR: Decoded & computed Hamming " + \
                          "weights missmatch for bits 21-58: " + \
                          f"{decoded_hamming_weight} != " + \
                          f"{hamming_weight}!\n"

            if hamming_weight % 2 != 0:
                output += "03-06: ERROR: Hamming weight for bits " + \
                          "21-58 is not even!\n"

        else:
            output += "03-06: ERROR: Hamming weight contains erroneous bits.\n"

        return output

    def decode_holidays(self, bits):
        output = ""

        if bits[0] == 1:
            output += "13: The following day is a holiday.\n"
        elif bits[0] == 3:
            output += "13: ERROR: Following holiday contains an error.\n"

        if bits[1] == 1:
            output += "14: The current day is a holiday.\n"
        elif bits[1] == 3:
            output += "14: ERROR: Current holiday contains an error.\n"

        # otherwise there is no holiday today or tomorrow

        return output

    def decode_clock_change(self, bit):
        output = ""

        if bit == 1:
            output += "16: Clock change\n"
        elif bit == 0:
            output += "16: No clock change\n"
        elif bit == 3:
            output += "16: ERROR: Clock change contains an error.\n"

        return output

    def decode_summertime(self, bits):
        output = ""

        # TBD check for error value 3 in the following bits
        if bits[0] == 0 and bits[1] == 1:
            output += "17-18: CET - winter time.\n"
        elif bits[0] == 1 and bits[1] == 0:
            output += "17-18: CEST - summer time.\n"
        elif ((bits[0] == 0 and bits[1] == 0) or
              (bits[0] == 1 and bits[1] == 1)):
            output += "17-18: ERROR: Both CET and CEST are equal!\n"
        else:
            output += "17-18: ERROR: CET/CEST contains errors\n"

        return output

    def decode_unused_zeros(self, bits):
        output = ""

        if (bits[7] == 1 or bits[8] == 1 or bits[9] == 1 or
                bits[10] == 1 or bits[11] or bits[12] == 1):
            output += "07-12: ERROR: At least one bit is 1 instead of 0!\n"
        elif (bits[7] == 0 and bits[8] == 0 and bits[9] == 0 and
              bits[10] == 0 and bits[11] == 0 and bits[12] == 0):
            output += "07-12: All zero.\n"
        elif 3 in bits[7:13]:
            output += "07-12: ERROR: Contains errors.\n"

        if bits[15] == 1:
            output += "15: ERROR: Is 1 instead of 0!\n"
        elif bits[15] == 3:
            output += "15: ERROR: Contains an error.\n"

        if bits[19] == 1:
            output += "19: ERROR: Is 1 instead of 0!\n"
        elif bits[19] == 3:
            output += "19: ERROR: Contains an error.\n"

        return output

    def decode_time_info_bit(self, bit):
        output = ""

        if bit == 1:
            output += "20: Begin of time information.\n"
        elif bit == 0:
            output += "20: ERROR: Time-info-bit is 0 instead of 1!\n"

        return output

    def decode_minutes(self, bitstream):
        output = ""

        if 3 not in bitstream:
            if (bitstream[0] ^ bitstream[1] ^ bitstream[2] ^
                    bitstream[3] ^ bitstream[4] ^ bitstream[5] ^
                    bitstream[6] ^ bitstream[7] == 0):
                output += "28: Even parity of minutes successful.\n"
            else:
                output += "28: Even parity of minutes failed.\n"
        else:
            num_errors = self.compute_num_errors(bitstream)

            if num_errors == 1:
                [bitstream, rel_err_pos, _] = \
                    self.single_error_correction(bitstream=bitstream)
                output += f"Corrected single error at {21 + rel_err_pos}.\n"
            else:
                output += "28: Even parity of minutes is ?.\n"

        min_dec0 = self.decode_BCD([bitstream[3], bitstream[2],
                                    bitstream[1], bitstream[0]], 4)

        min_dec10 = self.decode_BCD([bitstream[6], bitstream[5],
                                     bitstream[4]], 3)

        if min_dec0 != "?" and min_dec10 != "?":
            if min_dec0 > 9 and min_dec10 <= 5:
                output += "ERROR: 1*digit of minute is > 9!\n"
                min_dec0 = "?"
            elif min_dec10 > 5 and min_dec0 <= 9:
                output += "ERROR: 10*digit of minute is > 5!\n"
                min_dec10 = "?"
            elif min_dec10 > 5 and min_dec0 > 9:
                output += "ERROR: 10*digit of minute is > 5!\n"
                output += "ERROR: 1*digit of minute is > 9!\n"
                min_dec0 = "?"
                min_dec10 = "?"
        else:
            output += "ERROR: Minute is ?.\n"

        return [output, min_dec0, min_dec10]

    def decode_hours(self, bitstream):
        output = ""

        # check parity for the hour values
        if 3 not in bitstream:
            if (bitstream[0] ^ bitstream[1] ^ bitstream[2] ^ bitstream[3] ^
                    bitstream[4] ^ bitstream[5] ^ bitstream[6] == 0):
                output += "35: Even parity of hours successful.\n"
            else:
                output += "35: Even parity of hours failed.\n"
        else:
            num_errors = self.compute_num_errors(bitstream)

            if num_errors == 1:
                [bitstream, rel_err_pos, _] = \
                    self.single_error_correction(bitstream=bitstream)
                output += "Corrected single error at " + \
                          f"{29 + rel_err_pos + 1}.\n"
            else:
                output += "35: Even parity of hours is ?.\n"

        hour_dec0 = self.decode_BCD([bitstream[3], bitstream[2],
                                     bitstream[1], bitstream[0]], 4)

        hour_dec10 = self.decode_BCD([bitstream[5], bitstream[4]], 2)

        # check hour values
        if hour_dec0 != "?" and hour_dec10 != "?":
            if hour_dec10 == 2 and hour_dec0 > 3:
                output += "ERROR: Hours are greater than 23!\n"
                hour_dec0 = "?"
                hour_dec10 = "?"
            elif hour_dec0 > 9 and hour_dec10 <= 2:
                output += "ERROR: 1*digit of hour is > 9!\n"
                hour_dec0 = "?"
            elif hour_dec10 > 2 and hour_dec0 <= 9:
                output += "ERROR: 10*digit of hour is > 2!\n"
                hour_dec10 = "?"
            elif hour_dec10 > 2 and hour_dec0 > 9:
                output += "ERROR: 1*digit of hour is > 9!\n"
                output += "ERROR: 10*digit of hour is > 2!\n"
                hour_dec0 = "?"
                hour_dec10 = "?"
        else:
            output += "ERROR: Hour is ?.\n"

        return [output, hour_dec0, hour_dec10]

    def decode_clock_time(self, bitstream):
        output = ""

        [output_m, min_dec0, min_dec10] = self.decode_minutes(bitstream[21:29])
        [output_h, hour_dec0, hour_dec10] = self.decode_hours(bitstream[29:36])

        output += output_m + output_h

        output += f"21-27 & 29-34: Time: {hour_dec10}{hour_dec0}:" + \
                  f"{min_dec10}{min_dec0}h.\n"

        return output

    def decode_weekday(self, bitstream):
        output = ""

        if 3 not in bitstream:
            weekday = self.decode_BCD([bitstream[2], bitstream[1],
                                      bitstream[0]], 3)
        else:
            output += "42-44: ERROR: Weekday is ?.\n"
            return output

        if weekday == 0:
            output += "42-44: ERROR: Weekday is 0.\n"
        elif 1 <= weekday <= 7:
            output += f"42-44: Weekday: {self.weekdays[weekday - 1]}.\n"

        return output

    def decode_day(self, bitstream):
        output = ""

        day_dec0 = self.decode_BCD([bitstream[3], bitstream[2],
                                    bitstream[1], bitstream[0]], 4)
        day_dec10 = self.decode_BCD([bitstream[5], bitstream[4]], 2)

        # check date values day
        if day_dec0 != "?" and day_dec10 != "?":
            if day_dec0 == 0 and day_dec10 == 0:
                output += "ERROR: Day is 00!\n"
                day_dec0 = "?"
                day_dec10 = "?"
            elif day_dec0 > 9 and day_dec10 < 3:
                output += "ERROR: 1*digit of day is > 9!\n"
                day_dec0 = "?"
            elif day_dec10 == 3 and day_dec0 >= 2:
                output += "ERROR: Day is > 31!\n"
                day_dec0 = "?"
                day_dec10 = "?"
        else:
            output += "ERROR: Day is ?.\n"
            day_dec0 = "?"
            day_dec10 = "?"

        return [output, day_dec0, day_dec10]

    def decode_month(self, bitstream):
        output = ""

        month_dec0 = self.decode_BCD([bitstream[3], bitstream[2],
                                      bitstream[1], bitstream[0]], 4)
        month_dec10 = bitstream[4]

        if month_dec10 == 3:
            month_dec10 = "?"

        # check date values month
        if month_dec0 != "?" and month_dec10 != "?":
            if month_dec0 == 0 and month_dec10 == 0:
                output += "ERROR: Month is 00!\n"
                month_dec0 = "?"
                month_dec10 = "?"
            elif month_dec0 > 9 and month_dec10 < 1:
                output += "ERROR: 1*digit of month is > 9!\n"
                month_dec0 = "?"
            elif month_dec10 == 1 and month_dec0 >= 3:
                output += "ERROR: Month is > 12!\n"
                month_dec0 = "?"
                month_dec10 = "?"
        else:
            output += "ERROR: Month is ?.\n"
            month_dec0 = "?"
            month_dec10 = "?"

        return [output, month_dec0, month_dec10]

    def decode_year(self, bitstream):
        output = ""

        year_dec0 = self.decode_BCD([bitstream[3], bitstream[2],
                                     bitstream[1], bitstream[0]], 4)
        year_dec10 = self.decode_BCD([bitstream[7], bitstream[6],
                                      bitstream[5], bitstream[4]], 4)

        # check date values year
        if year_dec0 != "?" and year_dec10 != "?":
            if year_dec0 > 9 and year_dec10 <= 9:
                output += "ERROR: 1*digit of year is > 9!\n"
                year_dec0 = "?"
            if year_dec10 > 9 and year_dec0 <= 1:
                output += "ERROR: 10*digit of year is > 9!\n"
                year_dec10 = "?"
            elif year_dec10 > 9 and year_dec0 > 9:
                output += "ERROR: Year is > 99!\n"
                year_dec0 = "?"
                year_dec10 = "?"
        else:
            output += "ERROR: Year is ?.\n"
            year_dec0 = "?"
            year_dec10 = "?"

        return [output, year_dec0, year_dec10]

    def decode_date_weekday(self, bitstream):
        output = ""

        # single bit error correction over bits 36-57 for date and weekday
        num_errors = self.compute_num_errors(bitstream)
        if num_errors == 1:
            [bitstream, rel_err_pos, corr_val] = \
                self.single_error_correction(bitstream=bitstream)
            if corr_val != -1:
                output += "Corrected single error at " + \
                          f"{36 + rel_err_pos + 1}.\n"

        [output_d, day_dec0, day_dec10] = \
            self.decode_day(bitstream[0:6])
        [output_m, month_dec0, month_dec10] = \
            self.decode_month(bitstream[9:14])
        [output_y, year_dec0, year_dec10] = \
            self.decode_year(bitstream[14:22])

        output += output_d + output_m + output_y

        output += f"36-41 & 45-57: Date: {day_dec10}{day_dec0}." + \
                  f"{month_dec10}{month_dec0}.{year_dec10}{year_dec0}.\n"

        output_w = self.decode_weekday(bitstream[6:9])
        output += output_w

        # check even parity for the date and weekday values
        if 3 not in bitstream:
            if (bitstream[0] ^ bitstream[1] ^ bitstream[2] ^
                    bitstream[3] ^ bitstream[4] ^ bitstream[5] ^
                    bitstream[6] ^ bitstream[7] ^ bitstream[8] ^
                    bitstream[9] ^ bitstream[10] ^ bitstream[11] ^
                    bitstream[12] ^ bitstream[13] ^ bitstream[14] ^
                    bitstream[15] ^ bitstream[16] ^ bitstream[17] ^
                    bitstream[18] ^ bitstream[19] ^ bitstream[20] ^
                    bitstream[21] ^ bitstream[22] == 0):
                output += "58: Parity of date and weekdays successful.\n"
            else:
                output += "58: ERROR: Parity of date and weekdays failed.\n"
        else:
            output += "58: ERROR: Parity of date and weekdays is ?.\n"

        return output

    def decode_bitstream(self, bitstream):
        output = ""

        if len(bitstream) > 59:
            output += f"Decoding error\nReceived bits: {len(bitstream)}\n"
            return output
        elif len(bitstream) < 59:
            output += f"Decoding error\nReceived bits: {len(bitstream)}\n"
            return output

        output += "\n"

        output += self.decode_startbit(bitstream[0])

        output += self.decode_leap_second(bitstream[1:3])

        output += self.check_hamming_weight(bitstream)

        output += self.decode_unused_zeros(bitstream)

        output += self.decode_holidays(bitstream[13:15])

        output += self.decode_clock_change(bitstream[16])

        output += self.decode_summertime(bitstream[17:19])

        output += self.decode_time_info_bit(bitstream[20])

        output += self.decode_clock_time(bitstream)

        output += self.decode_date_weekday(bitstream[36:59])

        # count total number of errors in current bitstream
        num_errors = self.compute_num_errors(bitstream)

        # get indices of each error in current bitstream
        error_pos = self.compute_error_pos(bitstream)

        # to compensate for the shifted index
        error_pos = [val+1 for val in error_pos]

        if num_errors > 0:
            output += f"# Bit errors: {num_errors} => " + \
                      f"at positions: {error_pos}.\n"

        return output

    def consumer(self):
        context = zmq.Context()

        consumer_receiver = context.socket(zmq.PULL)
        consumer_receiver.connect("tcp://127.0.0.1:55555")

        bitstream = []
        count = 0

        while True:
            data = consumer_receiver.recv()
            received_msg = data.decode('ascii')[3:]

            # exit-loop statement: for testing only
            if received_msg == "___EOT":
                consumer_receiver.close()
                context.term()
                break

            if count >= 60:
                print("ERROR: more than 60 bits counted: Reinit Counter.")
                # just drop previous bitstream
                bitstream = []
                count = 0
                continue

            count += 1
            print(f"decoded bit at {count:02d}: {received_msg[0]} " +
                  f"at position: {received_msg[3:5]}")

            if (not (received_msg[0] == "0" or
                     received_msg[0] == "1" or
                     received_msg[0] == "2" or
                     received_msg[0] == "3" or
                     received_msg[0] == "E")):
                print(f"ERROR: received message \"{received_msg[0]}\" " +
                      "for time codeword is not permitted!")
                continue

            regex = "\d{2}"
            match = re.findall(regex, received_msg[3:5])
            if (not match) and (not received_msg[3:5] == "EE"):
                print(f"ERROR: received message \"{received_msg[3:5]}\" " +
                      "for position codeword is not permitted!")
                continue

            if match:
                position = int(received_msg[3:5], 10)
            elif received_msg[3:5] == "EE":
                # TODO as soon as multiple bits are lost this position might
                #      be false. The decoder should include this knowledge.
                position = count

            # fill up error symbols
            if count < position:
                print(f"{position-count} bit(s) lost before " +
                      f"position: {received_msg[3:5]}")
                for i in range(0, position-count):
                    bitstream.append(3)

            if received_msg[0] == "0":
                bitstream.append(0)
                count = position

            elif received_msg[0] == "1":
                bitstream.append(1)
                count = position

            elif received_msg[0] == "E":
                bitstream.append(3)
                count = position

            # derive current time and date from the bitstream
            elif received_msg[0] == "2" and count == 60:
                output = self.decode_bitstream(bitstream)
                print(output)

                bitstream = []
                count = position
                continue

            # either too few or too many bits have
            # been received during the decoding step
            elif received_msg[0] == "2" and count != 60:
                print("ERROR: Wrong number of bits at new minute!")
                print(f"#Bits: {len(bitstream)}")

                bitstream = []
                count = 0
                continue
