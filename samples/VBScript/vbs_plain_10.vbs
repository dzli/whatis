Function Factorial(n)
    Dim i, result
    result = 1
    For i = 2 To n
        result = result * i
    Next
    Factorial = result
End Function

Sub Greet(name)
    WScript.Echo "Hello, " & name & "! Factorial of 3 is " & Factorial(3)
End Sub

Call Greet("ggZNMm")
