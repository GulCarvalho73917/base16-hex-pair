import binascii


class DecodeError(ValueError):
    """Raised when a hex string cannot be decoded into bytes.

    We subclass ValueError rather than reusing it directly so callers can
    catch decode failures specifically without also catching unrelated
    ValueError raises from other parts of their code.
    """


def encode(data: bytes) -> str:
    """Encode bytes to a lowercase hexadecimal string.

    Returns a plain hex string with no separators — each input byte becomes
    exactly two output characters in the range 0-9a-f. We choose lowercase
    because it is the dominant convention in protocol specs and because
    round-tripping through decode() is case-insensitive, so encoding to
    lowercase is a deliberate, predictable canonical form.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError(f"encode() expects bytes, got {type(data).__name__}")
    return binascii.hexlify(data).decode("ascii")


def decode(text: str) -> bytes:
    """Decode a hexadecimal string into bytes.

    All ASCII whitespace (space, tab, newline, carriage return, form feed,
    vertical tab) is silently skipped, which makes the function tolerant of
    hex dumps formatted with line breaks or column separators. Upper and
    lower case hex digits are both accepted. After whitespace removal, the
    remaining string must have even length and consist only of characters in
    [0-9a-fA-F]; any other input raises DecodeError.

    We strip whitespace ourselves rather than delegating to
    binascii.unhexlify because that function's rejection of whitespace is
    version-dependent and its error messages are opaque; doing it here gives
    a single, predictable validation path.
    """
    if not isinstance(text, str):
        raise TypeError(f"decode() expects str, got {type(text).__name__}")

    cleaned = []
    for ch in text:
        if ch in " \t\n\r\f\v":
            continue
        if ch not in "0123456789abcdefABCDEF":
            raise DecodeError(
                f"invalid hex character {ch!r} at position {len(cleaned)}"
            )
        cleaned.append(ch)

    if len(cleaned) % 2 != 0:
        raise DecodeError("odd-length hex string after whitespace removal")

    return binascii.unhexlify("".join(cleaned))
