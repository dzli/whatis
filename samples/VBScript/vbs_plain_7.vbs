Dim dict
Set dict = CreateObject("Scripting.Dictionary")
dict.Add "UeMDj", 97
dict.Add "fcIJM", 77
dict.Add "GwFcM", 36
Dim k
For Each k In dict.Keys
    WScript.Echo k & " => " & dict(k)
Next
WScript.Echo "Count: " & dict.Count
