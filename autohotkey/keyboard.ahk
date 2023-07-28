#SingleInstance force

; optimizations
#NoEnv
#KeyHistory 0
ListLines Off
SetBatchLines -1
SendMode Input
SetTitleMatchMode 2

GroupAdd, RDP, Remote Desktop Connection

#MenuMaskKey vkFF
#If not WinActive("ahk_group RDP")

; main body
<!k::Send {Up}
<!m::Send {Down}
<!j::Send {Left}
<!i::Send {Right}
<!<^k::Send ^{Up}
<!<^m::Send ^{Down}
<!<^j::Send ^{Left}
<!<^i::Send ^{Right}
<!<+k::Send +{Up}
<!<+m::Send +{Down}
<!<+j::Send +{Left}
<!<+i::Send +{Right}
<!<+<^k::Send ^+{Up}
<!<+<^m::Send ^+{Down}
<!<+<^j::Send ^+{Left}
<!<+<^i::Send ^+{Right}

<!o::Send {Backspace}
<!<^o::Send ^{Backspace}
;<!<+o::Send +{Backspace}

<!d::Send {Delete}
<!<^d::Send ^{Delete}
;<!<+d::Send +{Delete}

<!f::Send {Enter}
<!<+f::Send +{Enter}
<!e::Send {Escape}

;<!p::Send {-}
;<!<+p::Send {_}

<!s::Send !{Left}

<!,::Send {PgUp}
<!.::Send {PgDn}
<!<^,::Send ^{PgUp}
<!<^.::Send ^{PgDn}
<!<+,::Send +{PgUp}
<!<+.::Send +{PgDn}

<!l::Send {Home}
<!;::Send {End}
<!<^l::Send ^{Home}
<!<^;::Send ^{End}
<!<+l::Send +{Home}
<!<+;::Send +{End}

