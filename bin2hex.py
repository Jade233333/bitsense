import random

BITS = 4  # change to 4 if you want single hex-digit inputs
MAX_VAL = (1 << BITS) - 1
HEX_WIDTH = (BITS + 3) // 4  # 4 bits per hex digit


def to_hex(n: int) -> str:
    return f"{n:0{HEX_WIDTH}X}"


def to_bin(n: int) -> str:
    return f"{n:0{BITS}b}"


def main() -> None:
    print(f"Bin → Hex trainer ({BITS}-bit values). Type 'q' to quit.\n")

    try:
        while True:
            n = random.randint(0, MAX_VAL)
            b = to_bin(n)
            correct_h = to_hex(n)

            ans = input(f"BIN {b} → HEX = ").strip()
            if ans.lower() == "q":
                break

            # optional "0x" prefix allowed
            if ans.lower().startswith("0x"):
                ans = ans[2:]

            # validate hex characters
            if not ans or any(c not in "0123456789abcdefABCDEF" for c in ans):
                print(f"Invalid input. Correct: {correct_h}\n")
                continue

            try:
                val = int(ans, 16)
            except ValueError:
                print(f"Invalid input. Correct: {correct_h}\n")
                continue

            if val == n:
                print("Correct.\n")
            else:
                print(f"Wrong. Correct: {correct_h}\n")

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
