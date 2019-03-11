import numpy as np
import math
import time

def normalized_correlation(haystack, needle):
    # math source: https://anomaly.io/understand-auto-cross-correlation-normalized-shift/#/normalized_cross_correlation

    # let us see how fast we can process this
    time1 = time.time()

    # numerator, a simple numpy correlation
    corr_hay_nee = np.correlate(haystack, needle, "valid")

    # denominator, that what is missing in the numpy correlation function.
    normed_corr_denominator_hay = np.multiply(haystack, haystack)
    normed_corr_denominator_hay = np.convolve(normed_corr_denominator_hay, np.ones(len(needle), dtype=int), "valid")

    normed_corr_denominator_nee = np.multiply(needle, needle)
    normed_corr_denominator_nee = np.convolve(normed_corr_denominator_nee, np.ones(len(needle), dtype=int), "valid")

    normed_corr_denominator = np.multiply(normed_corr_denominator_hay, normed_corr_denominator_nee)
    normed_corr_denominator = np.sqrt(normed_corr_denominator)

    # final normalized correlation
    normed_corr = np.divide(corr_hay_nee, normed_corr_denominator)

    # it took us this long. could be faster....
    print("normalized correlation was done in", time.time() - time1, "seconds")

    return normed_corr


def hex2bin(hexstr):
    ''' Convert a hexdecimal string to binary string, with zero fillings. '''
    scale = 16
    num_of_bits = len(hexstr) * math.log(scale, 2)
    binstr = bin(int(hexstr, scale))[2:].zfill(int(num_of_bits))
    return binstr


def np2bin(binarynp):
    ''' Convert a binary numpy array to string. '''
    return np.array2string(binarynp, separator='')[1:-1]


def bin2np(binarystr):
    ''' Convert binary string to numpy array. '''
    return np.array([int(i) for i in binarystr])


def crc(msg, encoding=False):
    ''' Mode-S Cyclic Redundancy Check
    Detect if bit error occurs in the Mode-S message
    Args:
        msg (string): 28 bytes hexadecimal message string
        encoding (bool): True to encode the date only and return the checksum
    Returns:
        string: message checksum, or parity bits (encoder)
    '''

    # the polynominal generattor code for CRC [1111111111111010000001001]
    generator_poly = np.array([1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,0,0,0,0,0,0,1,0,0,1])
    generatornumber = len(generator_poly)

    msgnpbin = bin2np(hex2bin(msg))

    if encoding:
        msgnpbin[-24:] = [0] * 24

    # loop all bits, except last 24 parity bits
    for i in range(len(msgnpbin) - 24):
        if msgnpbin[i] == 0:
            continue

        # perform XOR logic operation, when 1
        msgnpbin[i : i+generatornumber] = np.bitwise_xor(msgnpbin[i : i+generatornumber], generator_poly)

    # last 24 parity bits
    rest = np2bin(msgnpbin[-24:])
    return rest


def fix_msg_1bit(msg_bin, pos):

    msg_list = list(msg_bin)

    msg_bin_corrected = ""

    parity_length = 24
    for c in range(len(msg_bin) - parity_length):

        # bit flipping
        if msg_list[c] == "1":
            msg_list[c] = "0"
        else:
            msg_list[c] = "1"


        if int(crc(hex(int(''.join(msg_list), 2))[2:2 + 14]), 2) == 0:
            #print(pos, "corrected at", c,  ''.join(msg_list))
            msg_bin_corrected = ''.join(msg_list)
            break

        # bit back flipping
        if msg_list[c] == "1":
            msg_list[c] = "0"
        else:
            msg_list[c] = "1"

    return msg_bin_corrected


def flip_bit(msg_bin, position):
    '''
    flipping bits, the old way.
    when the 1 bit error was detected before, the bit position is used here to flipt the bit accordingly.
    the corrected binary message is returned

    :param msg_bin:
    :param position:
    :return msg_bin_corrected:
    '''

    msg_bin_corrected = list(msg_bin)
    if msg_bin_corrected[position[0][0]] == "0":
        msg_bin_corrected[position[0][0]] = "1"
    else:
        msg_bin_corrected[position[0][0]] = "0"

    msg_bin_corrected = ''.join(msg_bin_corrected)

    return msg_bin_corrected


def create_crc_lut_056bit():
    '''
    creating the lookup-table that we will need to find the position of a 1bit error in the 56bit long string.

    calculating the reminder for the full sequence of bits that was transmitted perfectly.
    then one bit is flipped and the reminder is calculated. it was checked, that the reminder, that is not zero anymore
    is the same for any correctly transferred bit sequence.
    this is repeated for each index position and the reminders are calculated and stored.

    :aim: if the reminder of any message can be found in this lookup table,
    then it is a 1 bit error,
    and then the location is located.
    the last step is to flip this one bit and it should be repaired.

    :premise: the message should not be so bit scrambled, that the checksum is correct for the wrong messages.
    should be unlikely.

    :return: list of crc24 reminders for each 1bit error.
    '''


    msg_bin = "01011101010011001010010110110111101111110111010001101101"

    crc_lut_056bit = []
    msg_tmp = list(msg_bin)
    for c in range(len(msg_tmp)):
        # bit flipping
        if msg_tmp[c] == "1":
            msg_tmp[c] = "0"
        else:
            msg_tmp[c] = "1"

        # print(c, ''.join(msg_tmp))
        # print(c, hex(int(crc(hex(int(''.join(msg_tmp), 2))[2:]), 2)))
        crc_lut_056bit.append(hex(int(crc(hex(int(''.join(msg_tmp), 2))[2:]), 2)))

        # bit back flipping
        if msg_tmp[c] == "1":
            msg_tmp[c] = "0"
        else:
            msg_tmp[c] = "1"

    return crc_lut_056bit


def create_crc_lut_112bit():
    '''
        creating the lookup-table that we will need to find the position of a 1bit error in the 112bit long string.

        calculating the reminder for the full sequence of bits that was transmitted perfectly.
        then one bit is flipped and the reminder is calculated. it was checked, that the reminder, that is not zero anymore
        is the same for any correctly transferred bit sequence.
        this is repeated for each index position and the reminders are calculated and stored.

        :aim: if the reminder of any message can be found in this lookup table,
        then it is a 1 bit error,
        and then the location is located.
        the last step is to flip this one bit and it should be repaired.

        :premise: the message should not be so bit scrambled, that the checksum is correct for the wrong messages.
        should be unlikely.

        :return: list of crc24 reminders for each 1bit error.
        '''


    msg_bin = "1000110100111100010010001001000110011001000000001001111010110101101000000000011100001100101000111111011000001010"

    crc_lut_112bit = []
    msg_tmp = list(msg_bin)
    for c in range(len(msg_tmp)):
        # bit flipping
        if msg_tmp[c] == "1":
            msg_tmp[c] = "0"
        else:
            msg_tmp[c] = "1"

        # print(c, ''.join(msg_tmp))
        # print(c, hex(int(crc(hex(int(''.join(msg_tmp), 2))[2:]), 2)))
        crc_lut_112bit.append(hex(int(crc(hex(int(''.join(msg_tmp), 2))[2:]), 2)))

        # bit back flipping
        if msg_tmp[c] == "1":
            msg_tmp[c] = "0"
        else:
            msg_tmp[c] = "1"

    return crc_lut_112bit



def main():
    print("Hello World!")
    time_start = time.time()

    # creating the lookup tables that we will need for the 1bit fixes.
    # both message length, 56 bit and 112 bit, each.
    crc_lut_056bit = create_crc_lut_056bit()
    crc_lut_112bit = create_crc_lut_112bit()


    # loading the iq data from your sdr receiver
    filename = "20190216_horn_1550327401.dat"
    # you can find some testing files here https://drive.google.com/open?id=1bfNvpZB5iFl3IsOAKPTupaH1KkH1CNB-
    # make sure you use a Python3 with 64 bit due to memory usage!


    data = np.memmap(filename, offset = 0)
    # offset = 0 for rtlsdr iq rcordings in 8bit binar form
    # offset = 44 for sdrsharp iq recordings in 8bit binary form


    # rtlsdr is recording binary unsigned. so making it signed and just using the amplitude of the iq data
    data = -127 + data[:]
    samples = np.sqrt(np.square(data[0::2]) + np.square(data[1::2]))

    # the adsb preamble is 1010000101000000
    # 1 =
    # full signal
    # 0 = 0.1
    # Not totally "zero" because there is always noise on the receiver.
    # A each sample would be multiplied with zero and so "bad" samples would be ignored too much.
    # With a low multiplicant, it would be still recognized and included into the correlation sum.

    needle = [1.0, 0.1, 1.0, 0.1, 0.1, 0.1, 0.1, 1.0, 0.1, 1.0, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]
    needle = np.array(needle) # converting it to a numpy array, because numpy doesn't like a normal python list.

    steps = 50000000
    count = 0
    for s in range(0, len(samples), steps):
        samples_chunk = samples[s : s + steps]
        corr = normalized_correlation(samples_chunk, needle)

        # finding the best starts of the preambles and putting the sample indexes to a list.
        # here we use > 0.86 because it worked good.
        preamble_start = np.where(corr > 0.86)

        # iterating through all the possible message starts
        for msg_index in range(len(preamble_start[0])):
            msg_start = preamble_start[0][msg_index]

            msg = samples_chunk[msg_start + 16: msg_start + 120 * 2]

            # putting the raw adsb mode-s message into a binary string
            msg_bin = ""

            # just a check for when the message is too close at the edge of the next sample chunk.
            # adsb modes can be 112 and 56 bits long. we always take 112 and due to manchaster coding, it is doubled.
            if len(msg) == 224:
                for i in range(0, len(msg), 2):

                    # manchester coding
                    # https://en.wikipedia.org/wiki/Manchester_code
                    if msg[i] > msg[i + 1]:
                        msg_bin += "1"
                    else:
                        msg_bin += "0"


                # maybe there is a better way to distingish between short and extended squitter, but at least this works
                if int(crc(hex(int(msg_bin, 2))[2:]), 2) == 0:
                    #print(msg_bin)
                    print("112", count, hex(int(msg_bin, 2))[2:], s + msg_start, (s + msg_start) / len(samples))
                    count += 1
                    continue

                else:
                    # finding where the 1 bit error most likely occured for a 112 bit message
                    position = np.argwhere(np.array(crc_lut_112bit) == hex(int(crc(hex(int(msg_bin, 2))[2:]), 2)))

                    if len(position) > 0:
                        # correcting the msg here
                        msg_bin_corrected = flip_bit(msg_bin, position)

                        if int(crc(hex(int(msg_bin_corrected, 2))[2:]), 2) == 0:
                            # print(msg_bin)
                            print("112_c", count, hex(int(msg_bin_corrected, 2))[2:], s + msg_start, (s + msg_start) / len(samples))
                            count += 1
                            continue


                if int(crc(hex(int(msg_bin, 2))[2:2 + 14]), 2) == 0:
                    print("056", count, hex(int(msg_bin, 2))[2:2 + 14], s + msg_start, (s + msg_start) / len(samples))
                    count += 1
                    continue

                else:
                    # finding where the 1 bit error most likely occured for a 56 bit message
                    position = np.argwhere(np.array(crc_lut_056bit)==hex(int(crc(hex(int(msg_bin, 2))[2:2 + 14]), 2)))

                    if len(position) > 0:
                        # correcting the msg here
                        msg_bin_corrected = flip_bit(msg_bin, position)

                        if int(crc(hex(int(msg_bin_corrected, 2))[2:2 + 14]), 2) == 0:
                            # print(msg_bin)
                            print("056_c", count, hex(int(msg_bin_corrected, 2))[2: 2 + 14], s + msg_start, (s + msg_start) / len(samples))
                            count += 1
                            continue

    print("total time", time.time() - time_start)

if __name__ == "__main__":
    main()