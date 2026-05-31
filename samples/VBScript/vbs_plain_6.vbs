Dim ie
Set ie = CreateObject("InternetExplorer.Application")
ie.Visible = True
ie.Navigate "https://localhost"
Do While ie.Busy Or ie.ReadyState <> 4
    WScript.Sleep 100
Loop
ie.Document.Title = "Hello yyXrO"
WScript.Sleep 713
ie.Quit
Set ie = Nothing
