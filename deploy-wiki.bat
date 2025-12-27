@echo off
REM Deploy wiki to GitHub Wiki (Windows version)

setlocal

set REPO_NAME=SITH_MISCHUNG_COMBUSTION
set REPO_OWNER=Bestsage
set WIKI_URL=https://github.com/%REPO_OWNER%/%REPO_NAME%.wiki.git
set WIKI_DIR=%TEMP%\wiki-deploy

echo 🚀 Deploying Wiki to GitHub...
echo.

REM Clean up previous deployment directory
if exist "%WIKI_DIR%" (
    echo 🧹 Cleaning up previous deployment...
    rmdir /s /q "%WIKI_DIR%"
)

REM Clone the wiki repository
echo 📥 Cloning wiki repository...
git clone "%WIKI_URL%" "%WIKI_DIR%"
if errorlevel 1 (
    echo ❌ Failed to clone wiki repository
    exit /b 1
)

REM Copy markdown files
echo 📝 Copying markdown files...
copy /Y wiki\*.md "%WIKI_DIR%\" >nul
if errorlevel 1 (
    echo ❌ Failed to copy markdown files
    exit /b 1
)

REM Navigate to wiki directory
cd /d "%WIKI_DIR%"

REM Check if there are changes
git status --porcelain > nul 2>&1
for /f %%i in ('git status --porcelain ^| find /c /v ""') do set CHANGES=%%i

if "%CHANGES%"=="0" (
    echo ✅ No changes to deploy.
    cd /d "%~dp0"
    rmdir /s /q "%WIKI_DIR%"
    exit /b 0
)

REM Commit and push
echo 💾 Committing changes...
git add .
git commit -m "Update wiki documentation with improved formatting" -m "" -m "- Better visual structure with Markdown formatting" -m "- Enhanced navigation between pages" -m "- Improved content organization" -m "- Better readability with tables, lists, and code blocks"
if errorlevel 1 (
    echo ❌ Failed to commit changes
    exit /b 1
)

echo 📤 Pushing to GitHub Wiki...
git push origin master
if errorlevel 1 (
    echo ❌ Failed to push to GitHub Wiki
    exit /b 1
)

echo.
echo ✅ Wiki deployed successfully!
echo 🔗 View at: https://github.com/%REPO_OWNER%/%REPO_NAME%/wiki
echo.

REM Clean up
cd /d "%~dp0"
rmdir /s /q "%WIKI_DIR%"

endlocal
