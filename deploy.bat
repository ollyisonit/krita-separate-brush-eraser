set NAME=separatebrusheraser

del /S /Q %appdata%\krita\pykrita\%NAME%
del /Q %appdata%\krita\pykrita\%NAME%.desktop
del /Q %appdata%\krita\actions\%NAME%.action
del /Q .\%NAME%.zip

robocopy .\%NAME% %appdata%\krita\pykrita\%NAME% /E
robocopy . %appdata%\krita\pykrita %NAME%.desktop
robocopy .\%NAME% %appdata%\krita\actions %NAME%.action

tar.exe -c -f .\%NAME%.zip .\%NAME% .\%NAME%.desktop

"%PROGRAMFILES%\Krita (x64)\bin\krita.com"