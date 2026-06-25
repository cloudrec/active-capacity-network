#!/usr/bin/env python3
"""Pure-Python Keccak-256 (Ethereum/Besu variant) — stdlib only, no dependencies.

Ethereum uses the ORIGINAL Keccak padding (0x01 .. 0x80), which differs from the
later NIST SHA3-256 padding (0x06). Python's hashlib only ships sha3_256, so this
module supplies the keccak_256 that Ethereum addresses require, with NO third-party
package. Correctness is pinned by known-answer vectors in selftest().
"""

_RC = [
    0x0000000000000001, 0x0000000000008082, 0x800000000000808A, 0x8000000080008000,
    0x000000000000808B, 0x0000000080000001, 0x8000000080008081, 0x8000000000008009,
    0x000000000000008A, 0x0000000000000088, 0x0000000080008009, 0x000000008000000A,
    0x000000008000808B, 0x800000000000008B, 0x8000000000008089, 0x8000000000008003,
    0x8000000000008002, 0x8000000000000080, 0x000000000000800A, 0x800000008000000A,
    0x8000000080008081, 0x8000000000008080, 0x0000000080000001, 0x8000000080008008,
]
_R = [
    [0, 36, 3, 41, 18],
    [1, 44, 10, 45, 2],
    [62, 6, 43, 15, 61],
    [28, 55, 25, 21, 56],
    [27, 20, 39, 8, 14],
]
_MASK = (1 << 64) - 1


def _rotl(x, n):
    return ((x << n) | (x >> (64 - n))) & _MASK


def _keccak_f(st):
    for rc in _RC:
        # theta
        c = [st[x][0] ^ st[x][1] ^ st[x][2] ^ st[x][3] ^ st[x][4] for x in range(5)]
        d = [c[(x - 1) % 5] ^ _rotl(c[(x + 1) % 5], 1) for x in range(5)]
        for x in range(5):
            for y in range(5):
                st[x][y] ^= d[x]
        # rho + pi
        b = [[0] * 5 for _ in range(5)]
        for x in range(5):
            for y in range(5):
                b[y][(2 * x + 3 * y) % 5] = _rotl(st[x][y], _R[x][y])
        # chi
        for x in range(5):
            for y in range(5):
                st[x][y] = b[x][y] ^ ((~b[(x + 1) % 5][y]) & b[(x + 2) % 5][y])
        # iota
        st[0][0] ^= rc
    return st


def keccak256(data: bytes) -> bytes:
    rate = 136  # bytes (1088 bits) for 256-bit output
    st = [[0] * 5 for _ in range(5)]
    # absorb with Keccak (0x01) padding + 0x80 final
    msg = bytearray(data)
    msg.append(0x01)
    while len(msg) % rate != 0:
        msg.append(0x00)
    msg[-1] ^= 0x80
    for off in range(0, len(msg), rate):
        block = msg[off:off + rate]
        for i in range(rate // 8):
            lane = int.from_bytes(block[i * 8:i * 8 + 8], "little")
            st[i % 5][i // 5] ^= lane
        _keccak_f(st)
    # squeeze 32 bytes
    out = bytearray()
    while len(out) < 32:
        for i in range(rate // 8):
            out += st[i % 5][i // 5].to_bytes(8, "little")
            if len(out) >= 32:
                break
        if len(out) < 32:
            _keccak_f(st)
    return bytes(out[:32])


def selftest() -> int:
    fails = 0

    def check(name, got, exp):
        nonlocal fails
        ok = got == exp
        print(("  PASS: " if ok else "  FAIL: ") + name + ("" if ok else f"  got={got} exp={exp}"))
        if not ok:
            fails += 1

    # Ethereum keccak256("") known answer
    check("keccak256('')", keccak256(b"").hex(),
          "c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470")
    # keccak256("abc")
    check("keccak256('abc')", keccak256(b"abc").hex(),
          "4e03657aea45a94fc7d47ba826c8d667c0d1e6e33a64a036ec44f58fa12d6c45")
    # keccak256 of the 0x prefix-less "The quick brown fox..."
    check("keccak256(fox)", keccak256(b"The quick brown fox jumps over the lazy dog").hex(),
          "4d741b6f1eb29cb2a9b9911c82f56fa8d73b04959d3d9d222895df6c0b28aa15")
    print("KECCAK SELFTEST OK" if fails == 0 else f"KECCAK SELFTEST FAILED ({fails})")
    return 1 if fails else 0


if __name__ == "__main__":
    import sys
    sys.exit(selftest())
