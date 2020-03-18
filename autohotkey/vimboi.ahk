#SingleInstance force

; optimizations
#NoEnv
#KeyHistory 0
ListLines Off
SetBatchLines -1
SendMode Input

;#MenuMaskKey vkFF
;+CapsLock::CapsLock
;*Shift::Send {LShift down}
;*Shift Up::Send {LShift up}
*CapsLock::Send {LControl down}
*CapsLock Up::Send {LControl up}

; main body
;#If WinNotActive("Octave")
<!h::Send {Left}
<!j::Send {Down}
<!k::Send {Up}
<!l::Send {Right}
<!;::Send {Backspace}
<!d::Send {Delete}
<!n::Send {Enter}
<!e::Send {Escape}
#If

