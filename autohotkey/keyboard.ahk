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
<!s::Send !{Left}
<!k::Send {Up}
<!m::Send {Down}
<!j::Send {Left}
<!i::Send {Right}
<!<+k::Send +{Up}
<!<+m::Send +{Down}
<!<+j::Send +{Left}
<!<+i::Send +{Right}
<!<+<^k::Send ^+{Up}
<!<+<^m::Send ^+{Down}
<!<+<^j::Send ^+{Left}
<!<+<^i::Send ^+{Right}

<!o::Send {Backspace}
;<!<+o::Send +{Backspace}
<!d::Send {Delete}
;<!<^d::Send ^{Delete}
;<!<+d::Send +{Delete}
<!f::Send {Enter}
<!e::Send {Escape}

<!p::Send {-}
<!<+p::Send {_}

<!<+,::Send {PgUp}
<!<+.::Send {PgDn}
<!l::Send {Home}
<!;::Send {End}
#If

