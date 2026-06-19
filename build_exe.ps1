py -3.10 -m PyInstaller --version *> $null
if ($LASTEXITCODE -ne 0) {
    if (Test-Path -LiteralPath "wheels") {
        py -3.10 -m pip install --no-index --find-links wheels pyinstaller
    } else {
        py -3.10 -m pip install pyinstaller
    }
}

py -3.10 -m PyInstaller --noconfirm --onefile --windowed --name "BulkRename" bulk_rename_app.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

py -3.10 -m PyInstaller --noconfirm --onefile --windowed --name "BulkRenameSetup" --add-data "dist\BulkRename.exe;." installer_app.py
