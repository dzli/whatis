Set objShell = CreateObject("WScript.Shell")
Dim cmd
cmd = "systeminfo"
objShell.Run "cmd /c " & cmd & " > %TEMP%\out.txt", 0, True
Dim fso, ts, line
Set fso = CreateObject("Scripting.FileSystemObject")
Set ts = fso.OpenTextFile(objShell.ExpandEnvironmentStrings("%TEMP%\out.txt"), 1)
Do While Not ts.AtEndOfStream
    line = ts.ReadLine
    WScript.Echo line
Loop
ts.Close
