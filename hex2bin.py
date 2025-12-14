import random

BITS = 4  # set to 4 for single hex digit, 8 for one byte, etc.
MAX_VAL = (1 << BITS) - 1
HEX_WIDTH = (BITS + 3) // 4  # 4 bits per hex digit


def to_hex(n: int) -> str:
    return f"{n:0{HEX_WIDTH}X}"


def to_bin(n: int) -> str:
    return f"{n:0{BITS}b}"


def main() -> None:
    print(f"Hex → Bin trainer ({BITS}-bit values, 0x00–0x{MAX_VAL:0{HEX_WIDTH}X})")
    print("Type the binary value. Type 'q' to quit.\n")

    try:
        while True:
            n = random.randint(0, MAX_VAL)
            h = to_hex(n)
            correct_b = to_bin(n)

            ans = input(f"HEX {h} → BIN = ").strip().replace(" ", "")
            if ans.lower() == "q":
                break

            # quick validity check
            if not ans or any(c not in "01" for c in ans):
                print(f"Invalid input. Correct: {correct_b}\n")
                continue

            try:
                val = int(ans, 2)
            except ValueError:
                print(f"Invalid input. Correct: {correct_b}\n")
                continue

            if val == n:
                print("Correct.\n")
            else:
                print(f"Wrong. Correct: {correct_b}\n")

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
