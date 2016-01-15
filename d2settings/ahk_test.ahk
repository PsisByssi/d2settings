;Process, Priority, , High
#MaxThreadsPerHotkey 3
#singleinstance force
;http://www.autohotkey.com/docs/KeyList.htm

;--------------- Disable the windows key -----------	

Lwin:: return

;------------------- Hot Keys----------------------

!F9:: send {NumpadMult}  		; Testing Mode, binds for loading items gold and heros etc  CHANGE BACK TO f9

!F5:: send {minus}     		; Makes Courier come to you and sends message

!`:: send {end}					; Clears text from help menu etc

^q:: send {7}			; The next few are for using the Courier commands

^w:: send {8} 

^e:: send {9}

^f:: send {0}

^g:: send {-}

^r:: send {=}

LCtrl & RAlt:: send {F3} 

MButton:: send {c}

9:: send {F10} 

1:: send {F10} 

1:: send {8} 

a:: send {f} 

;----------------------------------------


