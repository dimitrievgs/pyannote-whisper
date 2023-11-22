In the case of Windows, make sure that the creation of symbolic links is available for current user
https://translated.turbopages.org/proxy_u/en-ru.ru.90efdd60-655c8b97-abb7b901-74722d776562/https/stackoverflow.com/questions/32877260/privlege-error-trying-to-create-symlink-using-python-on-windows-10/65504258#65504258

In case of WIndows 10 Home you need to install gpedit.msc first:

make *.bat with
```
@echo off
dir /b C:\Windows\servicing\Packages\Microsoft-Windows-GroupPolicy-ClientExtensions-Package~3*.mum >find-gpedit.txt
dir /b C:\Windows\servicing\Packages\Microsoft-Windows-GroupPolicy-ClientTools-Package~3*.mum >>find-gpedit.txt
for /f %%i in ('findstr /i . find-gpedit.txt 2^>nul') do dism /online /norestart /add-package:"C:\Windows\servicing\Packages\%%i"
pause
```
and run it. Restart Windows.