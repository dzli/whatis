Function Factorial(n)
    Dim i, result
    result = 1
    For i = 2 To n
        result = result * i
    Next
    Factorial = result
End Function

Sub Greet(name)
    WScript.Echo "Hello, " & name & "! Factorial of 9 is " & Factorial(9)
End Sub

Call Greet("znWsfF")
