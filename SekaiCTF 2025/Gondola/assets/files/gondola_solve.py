from pathlib import Path
import re, itertools, hashlib
from z3 import *

# === constants you dumped with luajit ===
K = [
    0x77ab3bd16e69044a, 0x28613e1ba1b3368c, 0x5b80a90427dfd027, 0x7dd093e0ac1273c0,
    0xed2c47435820775f, 0xd86cfa00c18d6218, 0x5ea21a12280769d4, 0xf40d246c3242308d
]
T = [
    0x291b5ac66a3ae85c, 0xdf1ef268bd407c90, 0xa9f798551b79797a, 0x91e5b6efce05735a,
    0xf565b92f43a07c75, 0x8e3dc34d4d9107bd, 0xb43335bfc0181b24, 0xd569cc8badd8c4eb
]
TARGET_SHA = "204d015073f84763c0ff865d0fc4e046f882e2ade6afcf7bcb56904a6b96eb38"

# === 64-bit helpers ===
MASK64 = (1 << 64) - 1
def C(v): return BitVecVal(v & MASK64, 64)
def to64(x): return C(x) if isinstance(x, int) else x
def band(a,b): return to64(a) & to64(b)
def bor(a,b):  return to64(a) | to64(b)
def bxor(a,b): return to64(a) ^ to64(b)
def shl(a,n):
    if isinstance(n,int): n &= 63
    else: n = band(n, C(63))
    return (to64(a) << to64(n)) & C(MASK64)
def shr(a,n):
    if isinstance(n,int): n &= 63
    else: n = band(n, C(63))
    return LShR(to64(a), to64(n))
def ashr(a,n):
    if isinstance(n,int): n &= 63
    else: n = band(n, C(63))
    return to64(a) >> to64(n)
def rotl(a,n):
    if isinstance(n,int): n &= 63
    else: n = band(n, C(63))
    return bor((to64(a) << to64(n)) & C(MASK64),
               LShR(to64(a), (C(64) - to64(n)) & C(63)))
def rotr(a,n):
    if isinstance(n,int): n &= 63
    else: n = band(n, C(63))
    return bor(LShR(to64(a), to64(n)),
               (to64(a) << ((C(64) - to64(n)) & C(63))) & C(MASK64))
def byteswap64_const(v):
    v &= MASK64
    b = [(v >> (8*i)) & 0xff for i in range(8)]
    return (b[0]<<56)|(b[1]<<48)|(b[2]<<40)|(b[3]<<32)|(b[4]<<24)|(b[5]<<16)|(b[6]<<8)|b[7]

# === parse FUNC_LIST[78] and slice the case bodies ===
def slice_func78(lua_text: str) -> str:
    i = lua_text.find("FUNC_LIST[78] = function()")
    return lua_text[i: lua_text.find("\nend", i) if i >= 0 else len(lua_text)] if i >= 0 else lua_text

def build_case_from_lua(lua_text: str, label_num: int):
    body = slice_func78(lua_text)
    start = body.find(f"::continue_at_{label_num}::")
    assert start >= 0, f"Label ::continue_at_{label_num}:: not found"
    g = body.find("goto continue_at_4", start)
    l = body.find("::continue_at_4::", start)
    ends = [x for x in (g, l) if x != -1]
    assert ends, "End-of-branch not found"
    block = body[start:min(ends)]
    assigns = []
    for ln in block.splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("::") or ln.startswith("goto"):
            continue
        ln = ln.rstrip(';')
        if '=' in ln:
            assigns.append(ln)
    return assigns

CALL_MAP = {
    'band_i64': 'band', 'bor_i64' : 'bor',  'bxor_i64': 'bxor',
    'shl_i64' : 'shl',  'shr_u64' : 'shr',  'shr_i64' : 'ashr',
    'rotl_i64': 'rotl', 'rotr_i64': 'rotr', 'rol_i64' : 'rotl', 'ror_i64' : 'rotr',
}
NUM_RE = re.compile(r'(?<![A-Za-z0-9_])(-?\d+)LL?')
def lua_expr_to_py(src: str) -> str:
    for k, v in CALL_MAP.items():
        src = src.replace(k, v)
    return NUM_RE.sub(r'C(\1)', src)

def prelude_env(x_bv):
    env = {}
    env['loc_4']  = ZeroExt(32, x_bv)
    env['loc_5']  = C(byteswap64_const(K[4]))
    env['loc_6']  = C((K[6] * -511) & MASK64)
    env['loc_7']  = C((K[7] * -511) & MASK64)
    env['loc_8']  = C(K[0]); env['loc_9']  = bxor(rotl(env['loc_8'], 39), env['loc_8'])
    env['loc_10'] = C(K[1]); env['loc_11'] = C(K[2]); env['loc_12'] = C(K[3]); env['loc_13'] = C(K[5])
    env['loc_14'] = C(0); env['loc_15'] = C(0); env['loc_16'] = C(0); env['loc_17'] = C(0); env['loc_18'] = C(0); env['loc_19'] = C(0)
    env['reg_0']  = C(0)
    return env

def build_case_expr(lua_text: str, case_index: int, x_bv: BitVecRef):
    label_map = [12,11,10,9,8,7,6,5]
    assigns = build_case_from_lua(lua_text, label_map[case_index])
    ctx = prelude_env(x_bv)
    ctx.update(dict(C=C, band=band, bor=bor, bxor=bxor, shl=shl, shr=shr, ashr=ashr, rotl=rotl, rotr=rotr))
    for line in assigns:
        lhs, rhs = line.split('=', 1)
        ctx[lhs.strip()] = eval(lua_expr_to_py(rhs.strip()), {"__builtins__": {}}, ctx)
    return ctx['loc_4']

# === enumerate per-block printable solutions, then build all flags ===
def enumerate_all_flags(lua_path: Path, target_sha: str, max_show=10000):
    lua_text = lua_path.read_text(encoding="utf-8", errors="ignore")
    per_block = []
    for i in range(8):
        x = BitVec(f"x_{i}", 32)
        y = build_case_expr(lua_text, i, x)
        s = Solver()
        s.add(y == C(T[i]))
        # force printable ASCII per byte
        for b in [Extract(7,0,x),Extract(15,8,x),Extract(23,16,x),Extract(31,24,x)]:
            s.add(ULE(BitVecVal(32,8), b), ULE(b, BitVecVal(126,8)))
        sols = []
        while s.check() == sat:
            m = s.model()
            val = m[x].as_long()
            sols.append(bytes([(val>>0)&0xff,(val>>8)&0xff,(val>>16)&0xff,(val>>24)&0xff]))
            s.add(x != m[x])
            if len(sols) > 512:  # safety
                break
        per_block.append(sols)

    counts = [len(s) for s in per_block]
    total = 1
    for c in counts: total *= c
    print("Per-block printable counts:", counts)
    print("Total candidates (cartesian product):", total)

    flags = []
    match = None
    for combo in itertools.product(*per_block):
        flag = b"".join(combo)
        flags.append(flag)
        if hashlib.sha256(flag).hexdigest() == target_sha:
            match = flag
        if len(flags) >= max_show:
            break

    print(f"\nEnumerated {len(flags)} flags (showing up to {max_show}).")
    if match:
        print("SHA-256 match (platform-accepted):", match.decode(errors="replace"))
    else:
        print("No match found in the first batch.")

    for i, f in enumerate(flags, 1):
        try:
            print(f"{i:3d}. {f.decode()}")
        except:
            print(f"{i:3d}. {f!r}")

if __name__ == "__main__":
    lua_path = Path("chal.lua")
    assert lua_path.exists(), "Put this script next to 'chal.lua'"
    enumerate_all_flags(lua_path, TARGET_SHA)