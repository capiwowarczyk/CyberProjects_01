# MD5 Numeric Brute-Force Hash Recovery Script

A Python utility script designed to demonstrate numeric brute-force recovery of MD5 cryptographic hashes. The script generates sequential numbers, computes their MD5 digest, and compares the result against a user-supplied target hash string while tracking execution duration.

---

## Technical Overview

- **Algorithm**: MD5 (Message-Digest Algorithm 5), producing a 128-bit (16-byte) hash value represented as a 32-digit hexadecimal string.
- **Search Space**: Sequential integer evaluation covering range $1$ to $99,999,999,999$.
- **Performance Benchmarking**: Uses Python's native `time.time()` module to measure total elapsed brute-force duration in seconds.

---

## Code Breakdown & Analysis

```python
# This is my Python MD5 hash cracker!!

import hashlib, time

hash = str(input("Enter your hash here: ")) # getting user input
print("Attempting to find the password...")

start = time.time() # starting a timer

for i in range(1, 99999999999):  # attempting to crack the given hash
    guess = hashlib.md5(repr(i).encode('utf-8')).hexdigest()
    if guess == hash:
        print("Password Found: ", i) # prints the found hash
        break

end = time.time()
print("Found in: ", end - start, "seconds") # prints execution time
```

> **Note on Syntax Improvement**: In standard execution, `hexdigest` is a method and must be invoked with parentheses (`.hexdigest()`).

---

## Key Concepts & Implementation Details

1. **Input & Sanitization**: Prompts the user to enter a 32-character MD5 hash string.
2. **String Encoding**: Converts each integer `i` into its representation string (`repr(i)`) and encodes it into UTF-8 bytes prior to hashing.
3. **Digest Generation**: Computes `hashlib.md5(...)` for each candidate number.
4. **Target Matching**: Checks candidate hash against the target hash. Once matched, it outputs the plaintext value and breaks out of the loop.

---

## Usage Instructions

1. **Save the Script**: Save the code as `md5_cracker.py`.
2. **Execute**: Run the script using Python 3:
   ```bash
   python md5_cracker.py
   ```
3. **Prompt**: Enter an MD5 hash of a simple number (e.g., MD5 for `"12345"` is `827ccb0eea8a706c4c34a16891f84e7b`).

---

## Cryptographic & Defensive Context

- **MD5 Insecurity**: MD5 is cryptographically broken and vulnerable to collision attacks and extremely fast rainbow table or brute-force lookups. It is strictly prohibited for storing sensitive passwords or data protection under modern standards like NIST SP 800-63B.
- **Secure Hashing Recommendation**: Secure authentication systems require salted, slow key-derivation functions (KDFs) such as **Argon2id**, **bcrypt**, or **PBKDF2** to prevent rapid parallelized brute-force attacks.

---

## License

MIT License / Educational Use.
