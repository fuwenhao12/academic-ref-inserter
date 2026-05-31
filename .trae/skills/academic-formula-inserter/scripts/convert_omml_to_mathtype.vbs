' Convert OMML equations in a Word document to MathType OLE objects
' Run this script on your desktop (requires visible Word window)
'
' Usage:
'   cscript convert_omml_to_mathtype.vbs "input.docx" ["output.docx"]
'
' Or double-click (slower but works):
'   wscript convert_omml_to_mathtype.vbs

Dim inputPath, outputPath, fso, word, doc, shell, i, nTotal

Set fso = CreateObject("Scripting.FileSystemObject")

' Parse command line arguments
If WScript.Arguments.Count >= 1 Then
    inputPath = fso.GetAbsolutePathName(WScript.Arguments(0))
Else
    inputPath = fso.GetAbsolutePathName("formula_demo_visible.docx")
End If

If WScript.Arguments.Count >= 2 Then
    outputPath = fso.GetAbsolutePathName(WScript.Arguments(1))
Else
    outputPath = fso.GetAbsolutePathName(
        fso.GetBaseName(inputPath) & "_mathtype.docx")
End If

If Not fso.FileExists(inputPath) Then
    WScript.Echo "ERROR: File not found: " & inputPath
    WScript.Quit 1
End If

WScript.Echo "Input:  " & inputPath
WScript.Echo "Output: " & outputPath
WScript.Echo ""

' Start Word
WScript.Echo "Starting Word (visible mode required for equation conversion)..."
Set word = CreateObject("Word.Application")
word.Visible = True
word.DisplayAlerts = 0 ' wdAlertsNone

WScript.Echo "Word v" & word.Version

' Open document
WScript.Echo "Opening document..."
Set doc = word.Documents.Open(inputPath)
nTotal = doc.OMaths.Count
WScript.Echo "OMML equations found: " & nTotal

If nTotal = 0 Then
    WScript.Echo "No OMML equations found. Saving original document as-is..."
    doc.SaveAs2 outputPath
    doc.Close
    word.Quit
    WScript.Echo "Done! Saved: " & outputPath
    WScript.Quit
End If

' Process each equation
Set shell = CreateObject("WScript.Shell")
Dim converted, failed
converted = 0
failed = 0

WScript.Echo ""
WScript.Echo "Converting " & nTotal & " equations to MathType..."
WScript.Echo ""

For i = 1 To nTotal
    WScript.Echo "Equation #" & i & ": selecting..."
    On Error Resume Next
    doc.OMaths(i).Range.Select
    If Err.Number <> 0 Then
        WScript.Echo "  Select failed: " & Err.Description
        Err.Clear
        failed = failed + 1
        GoTo NextEquation
    End If
    On Error GoTo 0
    
    ' Allow Word to process the selection
    WScript.Sleep 300
    
    ' Method 1: SendKeys Alt+\ (MathType convert equation shortcut)
    WScript.Echo "  Sending Alt+\ (MathType Convert)..."
    shell.SendKeys "%\"  ' Alt+\
    WScript.Sleep 2000  ' Wait for MathType to process
    
    ' Press Enter if a confirmation dialog appears
    shell.SendKeys "{ENTER}"
    WScript.Sleep 500
    
    ' Method 2: Try MTCommand via Word.Run as backup
    On Error Resume Next
    word.Run "MTCommand", "ConvertEquation"
    If Err.Number = 0 Then
        WScript.Echo "  (also sent MTCommand)"
    End If
    Err.Clear
    On Error GoTo 0
    
    converted = converted + 1
    WScript.Echo "  Done."
    
NextEquation:
Next

WScript.Echo ""
WScript.Echo "Conversion complete!"
WScript.Echo "  Total:  " & nTotal
WScript.Echo "  OK:     " & converted
WScript.Echo "  Failed: " & failed
WScript.Echo "Remaining OMaths: " & doc.OMaths.Count

' Save
WScript.Echo ""
WScript.Echo "Saving: " & outputPath
On Error Resume Next
doc.SaveAs2 outputPath
If Err.Number <> 0 Then
    doc.SaveAs2 outputPath, 16 ' wdFormatDocumentDefault
End If
On Error GoTo 0
WScript.Echo "Saved!"

' Clean up
doc.Close
word.Quit
Set word = Nothing
Set shell = Nothing
Set fso = Nothing

WScript.Echo ""
WScript.Echo "All done! Open the output file in Word to verify."
WScript.Echo "  " & outputPath
