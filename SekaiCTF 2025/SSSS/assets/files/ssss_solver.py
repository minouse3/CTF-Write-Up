#!/usr/bin/env python3
from pwn import remote, context
from math import gcd
from random import randrange

context.log_level = "info"

HOST = "ssss.chals.sekai.team"
PORT = 1337

# From chall: p is prime, two rounds share the same secret
p = (1 << 256) - 189
P_MINUS_1 = p - 1

def inv(x): return pow(x, p - 2, p)

def factors_small(n):
    f, d, m = {}, 2, n
    while d * d <= m:
        while m % d == 0:
            f[d] = f.get(d, 0) + 1
            m //= d
        d += 1
    if m > 1: f[m] = f.get(m, 0) + 1
    return f

def find_good_t():
    # Service expects 20 <= t <= 50 :contentReference[oaicite:1]{index=1}; pick a divisor of p-1
    for t in range(50, 19, -1):
        if P_MINUS_1 % t == 0:
            return t
    return 29

def order_is_exact(g, t, tf):
    if pow(g, t, p) != 1: return False
    for q in tf:
        if pow(g, t // q, p) == 1: return False
    return True

def gen_root_of_unity(t):
    tf = factors_small(t)
    for h in range(2, 300):
        g = pow(h, P_MINUS_1 // t, p)
        if g != 1 and order_is_exact(g, t, tf):
            return g
    raise RuntimeError("no t-th root of unity found")

def dft_coeffs_from_samples(y, g, t):
    inv_g, inv_t = inv(g), inv(t)
    S0 = sum(yj % p for yj in y) % p
    coeffs = {}
    for k in range(1, t):
        base = pow(inv_g, k, p)
        r, Sk = 1, 0
        for j in range(t):
            Sk = (Sk + (y[j] % p) * r) % p
            r = (r * base) % p
        coeffs[k] = (Sk * inv_t) % p
    return coeffs, S0

def read_int_line(io):
    """Read lines until one parses as base-10 int (skips ':<' and any noise)."""
    while True:
        line = io.recvline(timeout=10)
        if not line:
            raise EOFError("Connection closed.")
        s = line.strip()
        try:
            return int(s)
        except ValueError:
            # swallow lines like b':<' (wrong-guess marker) or blanks
            continue

def one_round(io, t, xs):
    io.sendline(str(t).encode())
    ys = []
    for x in xs:
        io.sendline(str(x).encode())
        y = read_int_line(io)
        ys.append(y)
    return ys

def consume_wrong_marker(io):
    """After sending a wrong guess, the server prints ':<' once. Eat it."""
    try:
        line = io.recvline(timeout=5)
        # don't care what it is; just clear it if present
    except EOFError:
        pass

def solve():
    t = find_good_t()
    print(f"[i] Using t = {t} (since t | p-1)")

    g = gen_root_of_unity(t)
    xs = [1]
    for _ in range(1, t):
        xs.append((xs[-1] * g) % p)

    # Connect with TLS; service runs two rounds with same secret :contentReference[oaicite:2]{index=2}
    io = remote(HOST, PORT, ssl=True, sni=HOST)

    # -------- Round 1 --------
    y1 = one_round(io, t, xs)
    coeffs1, S01 = dft_coeffs_from_samples(y1, g, t)

    # Force round 2: intentionally wrong guess (any number ≠ secret)
    io.sendline(b"0")
    # The server prints ':<' on wrong guess — we must consume it :contentReference[oaicite:3]{index=3}
    consume_wrong_marker(io)

    # -------- Round 2 --------
    y2 = one_round(io, t, xs)
    coeffs2, S02 = dft_coeffs_from_samples(y2, g, t)

    cand1 = set(coeffs1.values())
    cand2 = set(coeffs2.values())
    inter = list(cand1 & cand2)

    if inter:
        secret = inter[0]
        print("[+] Found secret via DFT intersection.")
    else:
        secret = next(iter(cand2))
        print("[!] No intersection; picking a round-2 candidate (still likely).")

    io.sendline(str(secret).encode())

    # Print server output (flag or ':<')
    try:
        while True:
            line = io.recvline(timeout=3)
            if not line: break
            print(line.decode(errors="ignore").rstrip())
    except EOFError:
        pass
    io.close()

if __name__ == "__main__":
    solve()