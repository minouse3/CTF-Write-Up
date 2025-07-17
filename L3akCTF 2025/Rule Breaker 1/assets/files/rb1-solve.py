import hashlib
import itertools
import sys

# Load SHA256 hashes from hashes256.txt
try:
    with open("hash.txt", "r") as f:
        lines = [line.strip() for line in f.readlines()]
        if len(lines) < 3:
            print("Error: hashes256.txt must contain at least 3 hashes (one per line)")
            sys.exit(1)
        target_hashes = {
            "pass1": lines[0],
            "pass2": lines[1],
            "pass3": lines[2],
        }
except FileNotFoundError:
    print("Error: hashes256.txt not found")
    sys.exit(1)

found = {}

# Mutation 1: Append special + digit + uppercase
def try_mutation_1(word):
    specials = "!@#$%^&*"
    digits = "0123456789"
    uppers = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for c1, c2, c3 in itertools.product(specials, digits, uppers):
        mutated = word + c1 + c2 + c3
        h = hashlib.sha256(mutated.encode()).hexdigest()
        if h == target_hashes["pass1"]:
            return mutated
    return None

# Mutation 2: Remove one character
def try_mutation_2(word):
    if len(word) <= 1:
        return None
    for i in range(len(word)):
        mutated = word[:i] + word[i+1:]
        h = hashlib.sha256(mutated.encode()).hexdigest()
        if h == target_hashes["pass2"]:
            return mutated
    return None

# Mutation 3: Leetify vowels only
def try_mutation_3(word):
    leet_map = str.maketrans("aeio", "@310")
    mutated = word.translate(leet_map)
    h = hashlib.sha256(mutated.encode()).hexdigest()
    if h == target_hashes["pass3"]:
        return mutated
    return None

# Main cracking loop
try:
    with open("/usr/share/wordlists/rockyou.txt", "r", errors="ignore") as f:
        for line in f:
            word = line.strip()

            # Skip if all found
            if len(found) == 3:
                break

            # Try pass1
            if "pass1" not in found:
                m1 = try_mutation_1(word)
                if m1:
                    print(f"[+] Found pass1: {m1}")
                    found["pass1"] = m1

            # Try pass2
            if "pass2" not in found:
                m2 = try_mutation_2(word)
                if m2:
                    print(f"[+] Found pass2: {m2}")
                    found["pass2"] = m2

            # Try pass3
            if "pass3" not in found:
                m3 = try_mutation_3(word)
                if m3:
                    print(f"[+] Found pass3: {m3}")
                    found["pass3"] = m3

    # Output final flag
    if len(found) == 3:
        flag = f"L3AK{{{found['pass1']}_{found['pass2']}_{found['pass3']}}}"
        print(f"\n🎉 Flag: {flag}")
    else:
        print("\n⚠️ Some passwords were not found.")
except FileNotFoundError:
    print("Error: rockyou.txt not found. Please make sure it's in the same directory.")

