rem 用途、IPCのconnect方式の性能検証用、速度検証用
start python ipc_server.py

rem connectしたままの版
rem start python ipc_send.py
rem python ipc_send.py

rem 1回ごとにdisconnectする版
start python ipc_send_disconnect.py
python ipc_send_disconnect2.py

pause
