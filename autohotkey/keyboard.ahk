#SingleInstance force

; optimizations
#NoEnv
#KeyHistory 0
ListLines Off
SetBatchLines -1
SendMode Input

#MenuMaskKey vkFF
;+CapsLock::CapsLock
;*Shift::Send {LShift down}
;*Shift Up::Send {LShift up}
*CapsLock::Send {LControl down}
*CapsLock Up::Send {LControl up}

; main body
;#If WinNotActive("Octave")
<!i::Send {Up}
<!o::Send {Down}
<!j::Send {Left}
<!;::Send {Right}
<!<+i::Send +{Up}
<!<+o::Send +{Down}
<!<+j::Send +{Left}
<!<+;::Send +{Right}
<!<+<^i::Send ^+{Up}
<!<+<^o::Send ^+{Down}
<!<+<^j::Send ^+{Left}
<!<+<^;::Send ^+{Right}

<!;::Send {Backspace}
;<!<+;::Send +{Backspace}
<!d::Send {Delete}
;<!<^d::Send ^{Delete}
;<!<+d::Send +{Delete}
<!m::Send {Enter}
<!w::Send {Enter}
<!e::Send {Escape}

<!p::Send {-}
<!<+p::Send {_}

<!<+.::Send {PgUp}
<!<+,::Send {PgDn}
<!,::Send {Home}
<!.::Send {End}
#If

