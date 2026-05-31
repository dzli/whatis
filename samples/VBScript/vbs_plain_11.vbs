strComputer = "."
Set objWMI = GetObject("winmgmts:\\" & strComputer & "\root\cimv2")
Set colItems = objWMI.ExecQuery("Select * From Win32_Service")
For Each objItem in colItems
    WScript.Echo objItem.Name & ": " & objItem.Description
Next
