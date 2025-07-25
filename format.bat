@echo off
setlocal enabledelayedexpansion
set count=1

for %%f in (*.txt) do (
    set "num=00!count!"
    set "num=!num:~-3!"
    ren "%%f" "chain-!num!.txt"
    set /a count+=1
)
