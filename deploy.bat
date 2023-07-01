set NAME=separatebrusheraser
set ZIP="%PROGRAMFILES%\7-Zip\7z.exe"
set KRITA="%PROGRAMFILES%\Krita (x64)\bin\krita.com"

del /S /Q %appdata%\krita\pykrita\%NAME%
del /Q %appdata%\krita\pykrita\%NAME%.desktop
del /Q %appdata%\krita\actions\%NAME%.action
del /Q .\%NAME%.zip

robocopy .\%NAME% %appdata%\krita\pykrita\%NAME% /E
robocopy . %appdata%\krita\pykrita %NAME%.desktop
robocopy .\%NAME% %appdata%\krita\actions %NAME%.action

%ZIP% a -tzip .\%NAME%.zip .\%NAME% .\%NAME%.desktop

%KRITA%