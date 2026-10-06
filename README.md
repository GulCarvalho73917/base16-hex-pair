# base16_hex_pair

Encodes bytes to a lowercase hexadecimal string and decodes hex pairs back to
bytes, skipping ASCII whitespace and rejecting any character outside
`[0-9a-fA-F]`.

## Usage

```python
from base16_hex_pair import encode, decode, DecodeError

hexed = encode(b"hello")          # '68656c6c6f'
back = decode("68 65 6c 6c 6f")   # b'hello' — whitespace is skipped

try:
    decode("6g")
except DecodeError as exc:
    print(exc)  # invalid hex character 'g' at position 1
```

The library exports exactly three names: `encode`, `decode`, and
`DecodeError`.

## Why

Hex round-tripping is a frequent source of tiny bugs: off-by-one on odd-length
strings, silent acceptance of non-hex characters through `bytes.fromhex`, or
overly strict rejection of formatted dumps. `base16_hex_pair` does one thing:
encode with `binascii.hexlify` for a predictable lowercase canonical form, and
decode with explicit per-character validation plus optional whitespace
stripping.

The deliberate trade-off is that `decode` accepts only ASCII hex characters and
ASCII whitespace. Anything else — Unicode full-width digits, a stray `0x`
prefix, colons between bytes — raises `DecodeError`. If your input has a
prefix, strip it before calling `decode`.

## Edge cases

- `decode("abc")` raises `DecodeError` because after whitespace removal the
  length is odd. Whitespace is not counted toward length, so `decode("ab c")`
  also raises for the same reason.
- `decode("   ")` returns `b""` — a string consisting entirely of whitespace
  is treated as empty input, not an error.
- `encode` only accepts `bytes` or `bytearray`; passing `str` raises
  `TypeError`. This is intentional: converting a string to bytes requires a
  character encoding choice, and the caller should make that choice explicit.

## Running the tests

```
PYTHONPATH=src python -m unittest discover -s tests
```

## Performance

The window keeps a bounded buffer, so `push` is constant time and memory does not
grow with the length of the stream. `peak` and `trough` are linear in the window
size, which is the trade that keeps `push` cheap.

