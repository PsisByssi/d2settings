;Process, Priority, , High
#MaxThreadsPerHotkey 3
#singleinstance force

;http://www.autohotkey.com/docs/KeyList.htm
LALT & 1::MsgBox, You pressed Numpad1 while holding down Numpad0

;--------------- Disable the windows key -----------	

Lwin:: return

;------------------- Hot Keys----------------------

!F9:: send {NumpadMult}  		; Testing Mode, binds for loading items gold and heros etc  CHANGE BACK TO f9

!F2:: send {NumpadDiv}          ; Makes Courier come to you and sends message

!`:: send {end}					; Clears text from help menu etc

LCtrl & LAlt:: send {F3}	; Toggles between rune and hero

;------------------- Courier ----------------------

Control & q::			; The next few are for using the Courier commands
send {f2}q1 
sleep 200
send 1
return

Control & w::
send {f2}w1 
sleep 200
send 1
return

Control & e::
send {f2}e1 
sleep 200
send 1
return

Control & r::
send {f2}r1 
sleep 200
send 1
return
