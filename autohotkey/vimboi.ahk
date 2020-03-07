; optimizations
#NoEnv
#KeyHistory 0
ListLines Off
SetBatchLines -1
SendMode Input

#MenuMaskKey vkFF
+CapsLock::CapsLock
CapsLock::Ctrl

; main body
;#If WinNotActive("Octave")
<!h::Send {Left}
<!j::Send {Down}
<!k::Send {Up}
<!l::Send {Right}
<!;::Send {Backspace}
<!n::Send {Enter}
#If

