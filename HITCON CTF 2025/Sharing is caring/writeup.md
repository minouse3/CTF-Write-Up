## Sharing is caring - HITCON CTF 2025 Write-up

![Banner](assets/img/banner.png)

**Challenge:** Sharing is caring
**Category:** Reverse, Cryptography
**Points:** 248
**Author:** minouse3

### Introduction
“Sharing is caring” sounds friendly enough, but the description—“I just want to share my flag with you. I’m sooo kind.”—is classic CTF bait. All we actually get is a single file: [`chal.pyc`](assets/files/chal.pyc), a compiled Python bytecode blob. No source, no extras—just this one binary that claims it’ll “share” the flag if we figure out how to talk to it.

### Analyzing the [`chal.pyc`](assets/files/chal.pyc) File
Since it’s Python bytecode, the first move was decompiling it. I tried a bunch of public decompilers and online tools; most either errored out or produced incomplete code. So I asked ChatGPT to decompile it.
```py
from fractions import Fraction as F

# Coefficients (numerators) and denominators used by the Newton series F(n)
NUMS = (
    4144803293417776131310451317495228706499130241044716671850484110288180082374299088166459295448719,
    -2072401646708888065655225658747614353249565120522358335925242055144090041187149544083229647724360,
    1402769202505631727601810730581776197716350949074282314174097681867464170562021714349605843278665,
    -266910464101355921528772386602523543917783644737516474351090027562514187410064675818699897958587,
    -313229353281522365344068664569836505240104176843824464617477560855244400498647725320806722489359,
    557751498740761784158621178035559059268846555052211907264408739687389120087425335352771649978396,
    -148220410045571281675213691246814858326140849250454299621527572224931143542450173517412542679173,
    564587776942621790900159644909288844361323691524579619089869964015177357514421646000222366841011,
    16419311167856483659743166580345122059429852687371972090030542491766200835221304811819328984127643,
    -129495574458812869075479900411721351204283016397163153311462604211940551198569895507569182199080813,
    47898868564720804115714682250274391102579185635034480293836524415742949562361820585750668129254529,
    -218390354027018310133763040209628187632374060689193498603396047814125983080443006327100714094044413,
    59103242197276592018409321873953124131699316618422104513410197920897935735761382943069825870316159,
    -27263762963672679216265023144097755508375724831456195913391130341016602743379285802111387508470863,
    1160187342824936887648971210216937643772466507360201042905423657153536580858662152125535660765491989,
    -444320422098364618829295716221878629448833826150298094515910374813093990742157048727647821855149363,
    3391657179499987245173012089157446876066874678381207432018307585249041358997171094264590277038007977,
    -24577331115755648042095942172693201165277671886951704215934044389070300940570840382524224198279961,
    1269071325010846032881520707673575200237482393580774435940684724230748033745143799781707960856809939,
    -7726874421105907152194917563460067676020997409790741668467611810647472035036892326157134516638801157,
    52668298578428194831854365844392870064649623064538094318250290519368281728564224127244694555479507759,
    -14912585782593436965791721815706880430658073768879853640660934490173887905327298345044778117728763977,
    20665009833075583446533567863500153284398139825571833690969943149563885799810347822665143905426735039,
    -4881669849418826679690882149267389579292004979139066657955496750719085286782861933735958022689574551,
    19727966805580144784665343549651570513281612075070319397079427974816184475541029955406232208165236847,
    -412912430703112866772671727077127791058157331577997254034268890188791073228873359777862031674718585977,
    133658941250435616035761147529730684421152093449583968335054480106579383066071224012305258698560296819,
    -458807313057700431931426630680383859744706640412367673276163407570064822322611955042530141076353045301,
)

DENS = [
    1, 1, 2, 2, 12, 15, 10, 240, 40320, 362880, 403200, 7983360, 11975040,
    37065600, 12454041600, 43589145600, 3487131648000, 302455296000,
    213412456857600, 20274183401472000, 2432902008176640000,
    12772735542927360000, 281000181944401920000, 738629049682427904000,
    26976017466662584320000, 5170403347776995328000000,
    16803810880275234816000000, 640521732377550127104000000,
]

def F_eval(n: int) -> int:
    """Newton-series integer-valued polynomial used to derive all constants."""
    if n in (17, 18):
        return 18 - n
    acc = F(0, 1)
    falling = F(1, 1)
    for k, (a, d) in enumerate(zip(NUMS, DENS)):
        acc += F(a, d) * falling
        falling *= F(n - k, 1)
    return int(acc)

# === Constants mirrored from the bytecode ===
p, q = F_eval(0), F_eval(1)   # p = 2*q + 1 (safe prime)
A, B = F_eval(2), F_eval(3)
C0, C1, C2 = F_eval(4), F_eval(5), F_eval(6)
BUILTINS = [
    (F_eval(7),  F_eval(8),  F_eval(9)),
    (F_eval(10), F_eval(11), F_eval(12)),
    (F_eval(13), F_eval(14), F_eval(15)),
]
T = F_eval(16)

def check_triple(x: int, y: int, z: int) -> bool:
    """Implements the core congruence with exponents taken mod q."""
    lhs = pow(A, y % q, p) * pow(B, z % q, p) % p
    rhs = pow(C0, 1 % q, p)
    rhs = (rhs * pow(C1, x % q, p)) % p
    rhs = (rhs * pow(C2, (x * x) % q, p)) % p
    return lhs == rhs

if __name__ == "__main__":
    # IMPORTANT I/O GOTCHA: reads TEXT, converts TEXT BYTES → big-endian integer
    y1 = int.from_bytes(input("1:").strip().encode(), "big")
    y2 = int.from_bytes(input("2:").strip().encode(), "big")
    y3 = int.from_bytes(input("3:").strip().encode(), "big")

    triples = [
        (F_eval(22), y1, F_eval(23)),
        (F_eval(24), y2, F_eval(25)),
        (F_eval(26), y3, F_eval(27)),
    ]

    ok = all(check_triple(x, y, z) for (x, y, z) in triples)
    print("Success!" if ok else "Fail")
```

A few things jump out from that code:

* All the huge constants are rebuilt by a helper ```F_eval(n)``` (a Newton-series over big rational coefficients). That recreates ```p```, ```q```, ```A```, ```B```, ```C0..C2```, and some pre-baked “good” triples.
* ```p``` is a safe prime and every exponent is taken modulo ```q```, which means we can do all reasoning in the exponents (no discrete logs needed).
* The program asks for three text inputs, but immediately converts each to a big-endian integer before checking.
* Each check compares ```pow(A, y, p) * pow(B, z, p)``` to ```pow(C0, 1, p) * pow(C1, x, p) * pow(C2, x*x, p)``` with all exponents reduced modulo ```q```.
* The bytecode also ships three known-good triples ```(BUILTINS)```. Those are the key: we can combine them to cancel the unknown bases and directly solve for the required ```y (mod q)``` for each target ```(x, z)```.

### How to get the flag
The core idea is to work purely with exponents mod ```q``` and use the three built-in witness triples to eliminate everything except the ```A^y``` part.

1. For the target ```(x, z)```, the checker wants ```pow(A, y) * pow(B, z)``` (mod ```p```) to match the right-hand product using ```C0```, ```C1```, ```C2```.
2. For each built-in triple ```(x_i, y_i, z_i)```, the same relation holds with those values.
3. Divide the target relation by each built-in relation. That removes C0 right away and leaves only powers of ```A```, ```B```, ```C1```, ```C2```.
4. Choose three coefficients ```alpha = (a1, a2, a3)``` so that the combined exponent of ```B``` becomes zero (so ```B``` disappears), the combined exponent of ```C1``` becomes zero, and the combined exponent of ``C2`` becomes zero. In code, we form three short arrays that encode those “make it zero” conditions and take a cross product to get a non-trivial ```alpha``` that satisfies them modulo ```q```.
5. After those cancellations, the only thing left is a power of ```A``` with exponent equal to a linear combination of ```(y - y_i)```’s using the alpha weights. The only way this remaining factor can match is if that linear combination is zero mod ```q```, which gives a direct formula for ```y (mod q)``` using the known ```y_i``` and the ```alpha``` weights.
6. Convert the resulting residue ```y (mod q)``` into the exact ASCII the checker expects by doing big-endian bytes (the reverse of ```int.from_bytes(..., "big")``` used by the program).
7. Repeat for the three targets; concatenate the three strings → flag.

Here’s the exact script that does all of that—rebuilds constants, finds the alpha that cancels B/C1/C2, computes each y (mod q), converts to ASCII, and prints the flag.
```py
from fractions import Fraction as F

# ===== Reproduce the constants via the Newton-series F(n) =====
NUMS = (
    4144803293417776131310451317495228706499130241044716671850484110288180082374299088166459295448719,
    -2072401646708888065655225658747614353249565120522358335925242055144090041187149544083229647724360,
    1402769202505631727601810730581776197716350949074282314174097681867464170562021714349605843278665,
    -266910464101355921528772386602523543917783644737516474351090027562514187410064675818699897958587,
    -313229353281522365344068664569836505240104176843824464617477560855244400498647725320806722489359,
    557751498740761784158621178035559059268846555052211907264408739687389120087425335352771649978396,
    -148220410045571281675213691246814858326140849250454299621527572224931143542450173517412542679173,
    564587776942621790900159644909288844361323691524579619089869964015177357514421646000222366841011,
    16419311167856483659743166580345122059429852687371972090030542491766200835221304811819328984127643,
    -129495574458812869075479900411721351204283016397163153311462604211940551198569895507569182199080813,
    47898868564720804115714682250274391102579185635034480293836524415742949562361820585750668129254529,
    -218390354027018310133763040209628187632374060689193498603396047814125983080443006327100714094044413,
    59103242197276592018409321873953124131699316618422104513410197920897935735761382943069825870316159,
    -27263762963672679216265023144097755508375724831456195913391130341016602743379285802111387508470863,
    1160187342824936887648971210216937643772466507360201042905423657153536580858662152125535660765491989,
    -444320422098364618829295716221878629448833826150298094515910374813093990742157048727647821855149363,
    3391657179499987245173012089157446876066874678381207432018307585249041358997171094264590277038007977,
    -24577331115755648042095942172693201165277671886951704215934044389070300940570840382524224198279961,
    1269071325010846032881520707673575200237482393580774435940684724230748033745143799781707960856809939,
    -7726874421105907152194917563460067676020997409790741668467611810647472035036892326157134516638801157,
    52668298578428194831854365844392870064649623064538094318250290519368281728564224127244694555479507759,
    -14912585782593436965791721815706880430658073768879853640660934490173887905327298345044778117728763977,
    20665009833075583446533567863500153284398139825571833690969943149563885799810347822665143905426735039,
    -4881669849418826679690882149267389579292004979139066657955496750719085286782861933735958022689574551,
    19727966805580144784665343549651570513281612075070319397079427974816184475541029955406232208165236847,
    -412912430703112866772671727077127791058157331577997254034268890188791073228873359777862031674718585977,
    133658941250435616035761147529730684421152093449583968335054480106579383066071224012305258698560296819,
    -458807313057700431931426630680383859744706640412367673276163407570064822322611955042530141076353045301,
)
DENS = [
    1, 1, 2, 2, 12, 15, 10, 240, 40320, 362880, 403200, 7983360, 11975040,
    37065600, 12454041600, 43589145600, 3487131648000, 302455296000,
    213412456857600, 20274183401472000, 2432902008176640000,
    12772735542927360000, 281000181944401920000, 738629049682427904000,
    26976017466662584320000, 5170403347776995328000000,
    16803810880275234816000000, 640521732377550127104000000,
]
def F_eval(n: int) -> int:
    if n in (17, 18):  # special cases in the pyc
        return 18 - n
    acc, falling = F(0, 1), F(1, 1)
    for k, (a, d) in enumerate(zip(NUMS, DENS)):
        acc += F(a, d) * falling
        falling *= F(n - k, 1)
    return int(acc)

# === Rebuild everything ===
vals = [F_eval(i) for i in range(28)]
p, q = vals[0], vals[1]
A, B, C0, C1, C2 = vals[2], vals[3], vals[4], vals[5], vals[6]

BUILTINS = [
    (vals[7],  vals[8],  vals[9]),
    (vals[10], vals[11], vals[12]),
    (vals[13], vals[14], vals[15]),
]
targets = [  # (x,z) that the program asks you to satisfy
    (vals[22], vals[23]),   # 0x1337, ...
    (vals[24], vals[25]),   # 0xDEAD, ...
    (vals[26], vals[27]),   # 0xBEEF, ...
]

def modinv(a, m): return pow(a, -1, m)

def y_residue_for_target(x, z):
    # Build the 3×3 homogeneous system for alphas:
    xs = [t[0] for t in BUILTINS]
    ys = [t[1] for t in BUILTINS]
    zs = [t[2] for t in BUILTINS]
    r1 = [(zs[i] - z) % q for i in range(3)]            # cancel B
    r2 = [(x - xs[i]) % q for i in range(3)]            # cancel C1
    r3 = [(x*x - xs[i]*xs[i]) % q for i in range(3)]    # cancel C2

    # A vector in the right nullspace is a cross-product of any two rows
    def cross(u,v):
        return [(u[1]*v[2] - u[2]*v[1]) % q,
                (u[2]*v[0] - u[0]*v[2]) % q,
                (u[0]*v[1] - u[1]*v[0]) % q]
    def dot(u,v): return sum((u[i]*v[i]) % q for i in range(3)) % q

    alpha = cross(r1, r2)
    if dot(r3, alpha) != 0:
        alpha = cross(r1, r3)
        if dot(r2, alpha) != 0:
            alpha = cross(r2, r3)  # rows are dependent by construction

    sA   = sum(alpha) % q
    sAy  = sum((alpha[i] * ys[i]) % q for i in range(3)) % q
    assert sA != 0, "degenerate coefficients"
    return (sAy * modinv(sA, q)) % q  # y ≡ (Σ α_i y_i) / (Σ α_i)

def residue_to_ascii(y):
    nbytes = (y.bit_length() + 7) // 8
    return y.to_bytes(nbytes, "big").decode("ascii")

# Solve all three:
sol_strings = []
for (x,z) in targets:
    y = y_residue_for_target(x, z)
    sol_strings.append(residue_to_ascii(y))

print("[*] Parts:")
for i,s in enumerate(sol_strings,1):
    print(f"  s{i} = {s}")

flag = "".join(sol_strings)
print("\n[+] Flag:")
print(flag)

# Optional: sanity check against the checker logic
def ok(x, s, z):
    y = int.from_bytes(s.encode(), "big")
    lhs = pow(A, y % q, p) * pow(B, z % q, p) % p
    rhs = (pow(C0, 1, p) * pow(C1, x % q, p) * pow(C2, (x*x) % q, p)) % p
    return lhs == rhs

for (x,z), s in zip(targets, sol_strings):
    assert ok(x, s, z)
```

After running the script, it will prints the three readable pieces and then the full flag.
```bash
┌──(minouse3㉿kali)-[~] 
└─$ python3 solver.py 
[*] Parts:
  s1 = hitcon{Like_I_said_....._sharing_is_cari
  s2 = ng_and_caring_is_finding_the_right_share
  s3 = _4f63bf95789178799874ddf1c1bd6ad6b6297b}

[+] Flag:
hitcon{Like_I_said_....._sharing_is_caring_and_caring_is_finding_the_right_share_4f63bf95789178799874ddf1c1bd6ad6b6297b}
```

### Flag
```
hitcon{Like_I_said_....._sharing_is_caring_and_caring_is_finding_the_right_share_4f63bf95789178799874ddf1c1bd6ad6b6297b}
```