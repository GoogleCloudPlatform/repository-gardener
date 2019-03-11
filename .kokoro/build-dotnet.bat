set /p DPEBOT_GITHUB_TOKEN= < %KOKORO_GFILE_DIR%/%DPEBOT_GITHUB_TOKEN_FILE%

cd %KOKORO_ARTIFACTS_DIR%/github/repository-gardener

powershell .\.kokoro\build-dotnet.ps1
