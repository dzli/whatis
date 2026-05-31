Dim oNet, oDrives, i
Set oNet = CreateObject("WScript.Network")
Set oDrives = oNet.EnumNetworkDrives()
For i = 0 To oDrives.Count - 1 Step 2
    WScript.Echo oDrives.Item(i) & " => " & oDrives.Item(i + 1)
Next
