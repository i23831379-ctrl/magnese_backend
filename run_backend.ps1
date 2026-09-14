$pythonExe = "C:/Users/i2383/anaconda3/python.exe"
$backendDir = "c:\Users\i2383\Downloads\MANGANEX_AI_READY_VS_CODE\backend"

Push-Location $backendDir
& $pythonExe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
Pop-Location
