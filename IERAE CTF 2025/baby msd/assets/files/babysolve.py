from pwn import *
import time
import re

context.log_level = 'info'

def play_once():
    r = remote("35.200.10.230", 12343)
    r.timeout = 30
    try:
        for stage in range(100):
            r.recvuntil(b"====", timeout=10)
            log.info(f"Stage {stage + 1}")

            # Send 2000 times the all-1s modulus to bias MSD toward '1'
            r.recvuntil(b"Enter mod:", timeout=10)
            all_ones_mod = b"1111111111111111111111111111111\n"
            r.send(all_ones_mod * 2000)

            # Respond to the question about which digit appeared the most
            r.recvuntil(b"appeared the most?", timeout=30)
            r.sendline(b"1")

            result = r.recvline(timeout=10)
            if b"Failed" in result:
                log.warning(f"Failed at stage {stage + 1}")
                return False
            elif b"OK" in result:
                log.success(f"Stage {stage + 1} passed!")
            else:
                log.warning(f"Unexpected response: {result}")
                return False

        # Final flag retrieval
        flag_data = r.recvall(timeout=10)
        if flag_data:
            flag_text = flag_data.decode('utf-8', errors='ignore')
            match = re.search(r'[A-Za-z0-9_]+\{[^}]+\}', flag_text)
            if match:
                print(f"\n🎉 FLAG FOUND: {match.group()} 🎉\n")
            else:
                print(f"\n🎉 FLAG DATA: {flag_text.strip()} 🎉\n")
        else:
            log.warning("No flag data received after final stage")
        return True

    except Exception as e:
        log.error(f"Error: {e}")
        return False
    finally:
        r.close()

def main():
    log.info("Starting Baby MSD Solver using all-1s modulus")
    for attempt in range(1, 51):
        log.info(f"Attempt #{attempt}")
        if play_once():
            log.success("Challenge completed successfully!")
            break
        else:
            log.warning("Retrying in 2 seconds...")
            time.sleep(2)
    else:
        log.error("Max attempts reached without success.")

if __name__ == "__main__":
    main()
