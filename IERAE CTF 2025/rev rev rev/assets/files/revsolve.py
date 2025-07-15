with open("output.txt", "r") as f:
    z = eval(f.read())  # Load the mangled list

y = [~i for i in z]            # Step 1: Undo bitwise NOT
x = [i ^ 0xff for i in y]      # Step 2: Undo XOR with 0xff
x.reverse()                    # Step 3: Undo the list reversal
flag = ''.join(chr(i) for i in x)  # Step 4: ASCII to character

print("Recovered flag:",flag)
