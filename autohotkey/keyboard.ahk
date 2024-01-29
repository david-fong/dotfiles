#SingleInstance force

; optimizations
#NoEnv
#KeyHistory 0
ListLines Off
SetBatchLines -1
SendMode Input
SetTitleMatchMode 2

GroupAdd, RDP, Remote Desktop Connection

#MenuMaskKey vkFF ;or vk07
#If not WinActive("ahk_group RDP")

; main body

LAlt::return
;*LAlt::return
;<^LAlt::return
;<+LAlt::return
;<^<+LAlt::return

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
<!<^<+k::Send ^+{Up}
<!<^<+m::Send ^+{Down}
<!<^<+j::Send ^+{Left}
<!<^<+i::Send ^+{Right}

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
<!w::Send {Tab}
<!<^w::Send ^{Tab}
<!<+w::Send +{Tab}
<!<^<+w::Send ^+{Tab}

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

