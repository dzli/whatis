Dim name, age
name = InputBox("What is your name?", "Greeting")
If name = "" Then
    MsgBox "No name given.", vbExclamation
    WScript.Quit
End If
age = CInt(InputBox("How old are you?", "Greeting"))
If age < 18 Then
    MsgBox "Hi " & name & ", you're a minor.", vbInformation
ElseIf age < 65 Then
    MsgBox "Hi " & name & ", you're an adult.", vbInformation
Else
    MsgBox "Hi " & name & ", you're a senior.", vbInformation
End If
