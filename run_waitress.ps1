# Run the application using the local Python executable (adjust path if needed)
$python = "C:\Users\Denis Mutua\AppData\Local\Programs\Python\Python314\python.exe"
if (-not (Test-Path $python)) { $python = "python" }
& $python (Join-Path $PSScriptRoot 'serve_waitress.py')
