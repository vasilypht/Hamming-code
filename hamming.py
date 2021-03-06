import numpy as np
import math


def wrap(string: str, number: int) -> tuple[str]:
    """Function for splitting a string into substrings of n characters each

    Args:
        string (str): The string to be split.
        number (int): Number of characters in a substring.

    Returns:
        tuple[str]: A tuple that contains substrings of n characters.
    """
    wrap_str = tuple(string[i:i+number] for i in range(0, len(string), number))

    return wrap_str


def get_control_bits(block_length: int) -> tuple[int]:
    """Check bit calculation.

    Args:
        block_length (int): Block length based on which control bits will be
        determined.

    Returns:
        tuple[int]: A tuple that contains control bits.
    """
    k = 0
    while k < math.log2(block_length + k + 1):
        k = math.ceil(math.log2(k + block_length + 1))

    control_bits = tuple(2 ** i for i in range(k))

    return control_bits


def get_matrix_transform(block_length: int, k: int) -> np.ndarray:
    """Transition matrix for determining control bit and syndrome values.

    Args:
        block_length (int): The length of the block on the basis of which the
        matrix is built.
        k (int): Number of control bits.

    Returns:
        np.ndarray: Two-dimensional array (numpy)
    """
    matrix_transform = np.zeros((block_length + k, k), dtype=np.uint8)

    for index in range(1, block_length + k + 1):
        bin_value = bin(index)[2::].zfill(k)
        bin_value = list(map(int, bin_value))[::-1]
        matrix_transform[index - 1] = bin_value

    return matrix_transform.transpose()


def hamming_decode(string: str, block_length: int = 8) -> str:
    """Hamming decoding.

    Args:
        string (str): Encoded string.
        block_length (int, optional): Coding block length. Defaults to 8.

    Returns:
        str: Decoded string.
    """
    control_bits = get_control_bits(block_length)
    k = len(control_bits)

    matrix_transform = get_matrix_transform(block_length, k)

    decoded_str = ""

    for i, code in enumerate(wrap(string, block_length+k)):
        code = np.array(list(code), dtype=np.uint8)
        syndrome = np.dot(matrix_transform, code) % 2

        # Convert Syndrome to Decimal Number System
        index = int(''.join(map(str, syndrome[::-1])), 2)

        # Error correction
        if index == 0:
            print(f"No errors found in {i+1} block.")
        elif 0 < index < block_length + k:
            print(f"Found error in {i+1} block on position {index}.")
            code[index - 1] ^= 1
        else:
            print(f"Found an error that cannot be corrected ({i+1} block).")

        # Removing check bits
        code = list(code)
        for index in control_bits[::-1]:
            code.pop(index-1)

        code = ''.join(map(str, code))

        for bin_char in wrap(code, 8):
            decoded_str += chr(int(bin_char, 2))

    return decoded_str


def hamming_encode(string: str, block_length: int = 8) -> str:
    """Hamming encoding.

    Args:
        string (str): The string to be encoded.
        block_length (int, optional): Coding block length. Defaults to 8.

    Returns:
        str: Encoded string.
    """
    control_bits = get_control_bits(block_length)
    k = len(control_bits)

    matrix_transform = get_matrix_transform(block_length, k)

    encoded_str = ""
    delta = block_length // 8

    for chars in wrap(string, delta):
        # Binary character conversion
        bin_char = ""
        for char in chars:
            bin_char += bin(ord(char))[2::].zfill(8)

        # If the string length is less than the block length,
        # we supplement the string to the required block length.
        if len(bin_char) != block_length:
            bin_char = bin_char.zfill(block_length)

        # add control bits
        for bit in control_bits:
            bin_char = f"{bin_char[:bit - 1:]}0{bin_char[bit - 1::]}"

        bin_char = np.array(list(bin_char), dtype=np.int8)

        # find r0, ..., r(k)
        r_coffs = np.dot(matrix_transform, bin_char) % 2

        # Set the found control bits
        for bit, coff in zip(control_bits, r_coffs):
            bin_char[bit-1] = coff

        encoded_str += ''.join(map(str, bin_char))

    return encoded_str
