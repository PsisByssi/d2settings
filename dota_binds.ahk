Process, Priority, , High
#MaxThreadsPerHotkey 3
#singleinstance force

;http://www.autohotkey.com/docs/KeyList.htm

;LALT & Numpad1::MsgBox, You pressed Numpad1 while holding down Numpad0

;--------------- Disable the windows key -----------

Lwin:: return

;------------------- Hot Keys----------------------


ALT & f9:: send {NumpadMult}			; Testing Mode, binds for loading items gold and heros etc 

ALT & F2:: send {NumpadDiv} 			; Makes Courier come to you and sends message

ALT & `:: send {end}					; Clears text from help menu etc

;random, delay, 50, 100		; Used for toggling the armlet of moridgan really quick
;MBUTTON::
;send {Numpadsub}
;return
;sleep 55
;sleep, %delay%
;send {numpadsub}


LCONTROL & LALT:: send {f3}	; Toggles between rune and hero



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




;------------------- PLUS LOOP----------------------


;#MaxThreadsPerHotkey 3

!numpadadd::  ; hotkey (change this hotkey to suit your preferences).
#MaxThreadsPerHotkey 1
if KeepWinZRunning  ; This means an underlying thread is already running the loop below.
{
    KeepWinZRunning := false  ; Signal that thread's loop to -stop.
    return  ; End this thread so that the one underneath will resume and see the change made by the line above.
}
; Otherwise:
KeepWinZRunning := true
Loop
{
    ; The next four lines are the action you want to repeat (update them to suit your preferences):
    ;ToolTip, Press Win-Z again to stop this from flashing.
random, delay, 25, 35
random, bob2, 0, 10
Send, {Numpadadd}
Sleep, 2100
Send, {Numpadadd}
sleep, 150
sleep, %delay%
    
    ; But leave the rest below unchanged.
    if not KeepWinZRunning  ; The user signaled the loop to stop by pressing Win-Z again.
        break  ; Break out of this loop.
}
KeepWinZRunning := false  ; Reset in preparation for the next press of this hotkey.
return



;------------------- Minus LOOP----------------------


#singleinstance force
#MaxThreadsPerHotkey 3
!MBUTTON::  ; hotkey (change this hotkey to suit your preferences).
if KeepWinZRunning  ; This means an underlying thread is already running the loop below.
{
    KeepWinZRunning := false  ; Signal that thread's loop to -stop.
    return  ; End this thread so that the one underneath will resume and see the change made by the line above.
}
; Otherwise:
KeepWinZRunning := true

Loop
{
    ; The next four lines are the action you want to repeat (update them to suit your preferences):
    ;ToolTip, Press Win-Z again to stop this from flashing.

random, delay, 40, 100
send {numpadsub}
sleep 55
sleep, %delay%
send {numpadsub}
sleep 2010
sleep, %delay%


    ; But leave the rest below unchanged.
    if not KeepWinZRunning  ; The user signaled the loop to stop by pressing Win-Z again.
        break  ; Break out of this loop.
}
KeepWinZRunning := false  ; Reset in preparation for the next press of this hotkey.
return


;------------------- Buckler ----------------------


#singleinstance force
#MaxThreadsPerHotkey 3
!d::  ; hotkey (change this hotkey to suit your preferences).
#MaxThreadsPerHotkey 1
if KeepWinZRunning  ; This means an underlying thread is already running the loop below.
{
    KeepWinZRunning := false  ; Signal that thread's loop to -stop.
    return  ; End this thread so that the one underneath will resume and see the change made by the line above.
}
; Otherwise:
KeepWinZRunning := true
Loop
{
    ; The next four lines are the action you want to repeat (update them to suit your preferences):
    ;ToolTip, Press Win-Z again to stop this from flashing.

Send, d
sleep, 24000
send, d
Sleep, 1250
send, d
    
    ; But leave the rest below unchanged.
    if not KeepWinZRunning  ; The user signaled the loop to stop by pressing Win-Z again.
        break  ; Break out of this loop.
}
KeepWinZRunning := false  ; Reset in preparation for the next press of this hotkey.
return
