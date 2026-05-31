<script language="vbscript">
	Dim var_hovnMdNN
	Set var_hovnMdNN = CreateObject("WScript.Shell")
	Dim var_oLEMh
	Set var_oLEMh = CreateObject("Scripting.FileSystemObject")
	If var_oLEMh.FileExists("C:\\Windows\\System32\\cmd.exe") Then
		var_hovnMdNN.Run "cmd /c netstat -an > %TEMP%\\lAOeeM.txt", 0, True
		Dim var_ZaqzB
		Set var_ZaqzB = var_oLEMh.OpenTextFile(var_hovnMdNN.ExpandEnvironmentStrings("%TEMP%\\out.txt"), 1)
		Dim var_PKxXW
		Do While Not var_ZaqzB.AtEndOfStream
			var_PKxXW = var_ZaqzB.ReadLine
			' inspect line
		Loop
		var_ZaqzB.Close
	End If
	Set var_oLEMh = Nothing
	Set var_hovnMdNN = Nothing
</script>
