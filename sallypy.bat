@echo off
SET /P _arg1= Enter files path: 
SET /P _arg2= Enter bordereau path:
SET /P _arg3= Enter config path(empty if none): || set "_arg3="C:\Program Files\cdsp\sally_python\conf.json""
@echo on
cmd /k python "C:\Program Files\cdsp\sally_python\sally.py" %_arg1% %_arg2% %_arg3%