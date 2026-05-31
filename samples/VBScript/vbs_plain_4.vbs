Dim dict
Set dict = CreateObject("Scripting.Dictionary")
dict.Add "AjJJA", 10
dict.Add "pHFQX", 84
dict.Add "jcLQG", 65
Dim k
For Each k In dict.Keys
    WScript.Echo k & " => " & dict(k)
Next
WScript.Echo "Count: " & dict.Count
