import unittest

from base16_hex_pair import encode, decode, DecodeError


class TestEncode(unittest.TestCase):
    def test_empty_bytes(self):
        self.assertEqual(encode(b""), "")

    def test_single_byte(self):
        self.assertEqual(encode(b"\x00"), "00")
        self.assertEqual(encode(b"\xff"), "ff")
        self.assertEqual(encode(b"\x0f"), "0f")

    def test_known_vector(self):
        self.assertEqual(encode(b"hello"), "68656c6c6f")

    def test_lowercased_output(self):
        # Every output character must be 0-9 or a-f, never A-F.
        out = encode(bytes(range(256)))
        self.assertEqual(out, out.lower())
        self.assertEqual(len(out), 512)

    def test_rejects_non_bytes(self):
        with self.assertRaises(TypeError):
            encode("hello")  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            encode(123)  # type: ignore[arg-type]

    def test_accepts_bytearray(self):
        self.assertEqual(encode(bytearray(b"abc")), "616263")


class TestDecode(unittest.TestCase):
    def test_empty_string(self):
        self.assertEqual(decode(""), b"")

    def test_known_vector(self):
        self.assertEqual(decode("68656c6c6f"), b"hello")

    def test_uppercase(self):
        self.assertEqual(decode("FF"), b"\xff")
        self.assertEqual(decode("48656C6C6F"), b"Hello")

    def test_mixed_case(self):
        self.assertEqual(decode("aF"), b"\xaf")

    def test_round_trip_full_byte_range(self):
        data = bytes(range(256))
        self.assertEqual(decode(encode(data)), data)

    def test_ignores_whitespace(self):
        self.assertEqual(decode("68 65 6c 6c 6f"), b"hello")
        self.assertEqual(decode("68\n65\n6c\n6c\n6f"), b"hello")
        self.assertEqual(
            decode("  68\t65\r6c\f6c\v6f  "),
            b"hello",
        )

    def test_rejects_non_hex_char(self):
        with self.assertRaises(DecodeError):
            decode("6g")
        with self.assertRaises(DecodeError):
            decode("zz")

    def test_rejects_odd_length_after_whitespace_strip(self):
        # "abc" is 3 hex chars — odd, even though no whitespace.
        with self.assertRaises(DecodeError):
            decode("abc")
        # whitespace does not count toward length
        with self.assertRaises(DecodeError):
            decode("ab c")

    def test_rejects_non_string(self):
        with self.assertRaises(TypeError):
            decode(b"68")  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            decode(123)  # type: ignore[arg-type]

    def test_all_whitespace_decodes_to_empty(self):
        self.assertEqual(decode("   \n\t  "), b"")


class TestRoundTrip(unittest.TestCase):
    def test_idempotent_through_ascii(self):
        payload = "The quick brown fox jumps over the lazy dog".encode("utf-8")
        hexed = encode(payload)
        self.assertEqual(decode(hexed), payload)


class TestDecodeErrorType(unittest.TestCase):
    def test_decode_error_is_value_error(self):
        # Callers using `except ValueError` must still catch it.
        try:
            decode("x")
        except ValueError:
            return
        self.fail("DecodeError did not derive from ValueError")


if __name__ == "__main__":
    unittest.main()
