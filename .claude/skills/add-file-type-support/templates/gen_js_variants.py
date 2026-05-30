#!/usr/bin/env python3
"""Generate synthetic training samples for three JS obfuscation variants.

Each generator emits files into the project samples/ tree. Patterns are
modeled after structural signatures observed in real samples, but the
generated content is otherwise random (no real-file content is reused).
"""
import os
import random
import string

ROOT = "/Users/dazhi/projects/filetyping/whatis/samples"


def rand_lower(n):
    return "".join(random.choices(string.ascii_lowercase, k=n))


def rand_ident(n, leading_alpha=True):
    first = random.choice(string.ascii_letters + "_$")
    rest = "".join(random.choices(string.ascii_letters + string.digits + "_$", k=n - 1))
    return first + rest


# -------- Group A: JavaScript+LongIdent --------
# Pattern: single line, one giant lowercase identifier, assigned [], then
# many property assignments with long random property names mapping to
# single chars. Trailing ",0,false);" tail mimics an outer wscript-shell call.
def gen_longident(out_dir, seed):
    random.seed(seed)
    ident_len = random.randint(800, 2500)
    n_assigns = random.randint(150, 500)
    main_id = rand_lower(ident_len)
    parts = [f"{main_id}=[];"]
    for _ in range(n_assigns):
        prop_len = random.randint(40, 220)
        prop = rand_lower(prop_len)
        val = random.choice(string.ascii_letters + string.digits + "+/=")
        parts.append(f"{main_id}['{prop}']='{val}';")
    # final concat-ish tail
    last_prop = rand_lower(random.randint(40, 220))
    parts.append(f"{main_id}['{last_prop}']+'='+'',0,false);")
    return "".join(parts)


# -------- Group D: JavaScript+CharCodeSubtract --------
# Pattern: var K = <big_int>; var S = String.fromCharCode(N1-K, N2-K, ...); eval(S);
def gen_charcode_subtract(out_dir, seed):
    random.seed(seed)
    k_ident = rand_ident(random.randint(3, 6))
    s_ident = rand_ident(random.randint(4, 10))
    base = random.randint(1_000_000, 200_000_000)
    # Decode payload: random characters that look like an executable JS or shell string.
    payload_len = random.randint(40, 600)
    payload_chars = random.choices(
        string.ascii_letters + string.digits + ' "(),.;:=/\\!?\'-+', k=payload_len
    )
    nums = [f"{base + ord(c)}-{k_ident}" for c in payload_chars]
    s_init = ",".join(nums)
    body = (
        f"var {k_ident}={base}\n"
        f"var {s_ident} = String.fromCharCode({s_init})\n"
        f"eval({s_ident});\n"
    )
    return body


# -------- Group B: JavaScript+ObfuscatorIO with dictionary-word name mangler --------
# obfuscator.io structure with `identifiersDictionary` enabled:
# - hex-array of obfuscated string literals
# - IIFE that rotates the array
# - decode function reading from the array with a subtracted offset
# - several short decode-call assignments
# - word-style identifiers instead of _0xXXXX
WORDS = (
    "march thehas wasbut overchurch viiheld fromhabit mostchanged honour ground "
    "river shadow mountain river path window stone heart bridge candle wandering "
    "letter remember willow forgotten morning silver crimson lonely silent silver "
    "ember meadow horizon midnight hollow swallow sparrow lantern echo whisper "
    "season harbour winter summer linger orchard wandering crimson moonlit forest"
).split()


def rand_word_ident():
    return "_".join(random.sample(WORDS, k=random.randint(1, 3))) + str(random.randint(0, 99))


def hex_blob(n):
    # Strings that look like obfuscator.io encoded strings: capital W, lowercase,
    # mixed case base64-ish without padding.
    alphabet = string.ascii_letters + string.digits
    return "W" + "".join(random.choices(alphabet, k=n - 1))


def gen_obfuscatorio_words(out_dir, seed):
    random.seed(seed)
    array_ident = rand_word_ident()
    array_fn = rand_word_ident()
    decode_fn = rand_word_ident()
    rotate_param = rand_word_ident()
    rotate_count = rand_word_ident()
    arr_size = random.randint(15, 60)
    strings = ", ".join("'" + hex_blob(random.randint(12, 60)) + "'" for _ in range(arr_size))

    # rotate IIFE constants (hex literal arithmetic — signature of obfuscator.io)
    a, b, c = (
        random.randint(0x100, 0xfff),
        random.randint(0x100, 0xfff),
        random.randint(0x10000, 0xfffff),
    )
    offset = random.randint(0, 0xff)

    header = (
        f"function {array_fn}() {{\n"
        f"    var overchurch = [\n"
        f"        {strings}\n"
        f"    ];\n"
        f"    {array_fn} = function () {{\n"
        f"        return overchurch;\n"
        f"    }};\n"
        f"    return {array_fn}();\n"
        f"}}\n"
        f"var {rand_word_ident()} = {decode_fn};\n"
        f"function {decode_fn}({rand_word_ident()}, {rand_word_ident()}) {{\n"
        f"    var viiheld = {array_fn}();\n"
        f"    {decode_fn} = function ({rotate_param}, {rotate_count}) {{\n"
        f"        {rotate_param} = {rotate_param} - (0x{a:x} * 0x{a:x} + -0x{b:x} * 0x{c:x} + 0x{(a*b+c):x});\n"
        f"        var {rand_word_ident()} = viiheld[{rotate_param}];\n"
        f"        return {rand_word_ident()};\n"
        f"    }};\n"
        f"    return {decode_fn}({rand_word_ident()}, {rand_word_ident()});\n"
        f"}}\n"
        f"(function ({rand_word_ident()}, {rand_word_ident()}) {{\n"
        f"    var {rand_word_ident()} = {decode_fn};\n"
        f"    while (!![]) {{\n"
        f"        try {{\n"
        f"            var {rand_word_ident()} = parseInt({rand_word_ident()}('0x{random.randint(0,0xff):x}')) "
        f"+ -parseInt({rand_word_ident()}('0x{random.randint(0,0xff):x}'));\n"
        f"            if ({rand_word_ident()} === {rand_word_ident()}) break;\n"
        f"            else {rand_word_ident()}['push']({rand_word_ident()}['shift']());\n"
        f"        }} catch ({rand_word_ident()}) {{\n"
        f"            {rand_word_ident()}['push']({rand_word_ident()}['shift']());\n"
        f"        }}\n"
        f"    }}\n"
        f"}}({array_fn}, 0x{offset:x}));\n"
    )

    # A handful of decode-call statements that exercise the alias.
    extra_lines = []
    for _ in range(random.randint(8, 30)):
        v = rand_word_ident()
        extra_lines.append(
            f"var {v} = {decode_fn}('0x{random.randint(0,0xff):x}', '{hex_blob(8)}');"
        )
    extra_lines.append("function iwntthylrshrho(ytvobbdk) {")
    extra_lines.append("    if (typeof ytvobbdk !== 'string') {")
    extra_lines.append(
        f"        throw new TypeError({decode_fn}('0x{random.randint(0,0xff):x}', '{hex_blob(8)}'));"
    )
    extra_lines.append("    }")
    extra_lines.append("    if (ytvobbdk.length % 2 !== 0) {")
    extra_lines.append(
        f"        throw new RangeError({decode_fn}('0x{random.randint(0,0xff):x}', '{hex_blob(8)}'));"
    )
    extra_lines.append("    }")
    extra_lines.append("    var " + rand_word_ident() + " = [];")
    extra_lines.append("    for (var " + rand_word_ident() + " = 0;")
    extra_lines.append("}")
    return header + "\n".join(extra_lines) + "\n"


def main():
    # Group A: 12 files
    target_a = os.path.join(ROOT, "JavaScript+LongIdent")
    for i in range(12):
        path = os.path.join(target_a, f"longident_{i}.js")
        with open(path, "w") as f:
            f.write(gen_longident(target_a, seed=1000 + i))
        print(f"wrote {path} ({os.path.getsize(path)} bytes)")

    # Group D: 10 files
    target_d = os.path.join(ROOT, "JavaScript+CharCodeSubtract")
    for i in range(10):
        path = os.path.join(target_d, f"charcode_subtract_{i}.js")
        with open(path, "w") as f:
            f.write(gen_charcode_subtract(target_d, seed=2000 + i))
        print(f"wrote {path} ({os.path.getsize(path)} bytes)")

    # Group B: 6 additional ObfuscatorIO files with word-mangler style
    target_b = os.path.join(ROOT, "JavaScript+ObfuscatorIO")
    for i in range(6):
        path = os.path.join(target_b, f"obfusio_words_{i}.js")
        with open(path, "w") as f:
            f.write(gen_obfuscatorio_words(target_b, seed=3000 + i))
        print(f"wrote {path} ({os.path.getsize(path)} bytes)")


if __name__ == "__main__":
    main()
