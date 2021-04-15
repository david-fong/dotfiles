
```
Not related, but written here in case I forget what I did:
Computer\HKEY_CURRENT_USER\Software\Policies\Microsoft\Windows\Explorer\NoUninstallFromStart
Computer\HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\CredUI\DisablePasswordReveal
right-click recycle bin and check the "prompt before moving to recycle-bin" box

don't turn on "lower screen brightness in battery saving mode".
  seems to lock screen brightness until next computer restart.
settings > system > multitasking > don't show snap beside options.

Search up how to "force" uninstall things like Microsoft Solitaire Collection.
https://www.windowscentral.com/how-disable-password-reveal-button-sign-screen-windows-10
https://www.howtogeek.com/224159/how-to-disable-bing-in-the-windows-10-start-menu/

https://man7.org/linux/man-pages/man4/console_codes.4.html
https://www.howtogeek.com/129178/why-does-64-bit-windows-need-a-separate-program-files-x86-folder/
```

- [Don't Do's for configuring Windows Defender Exclusions](https://docs.microsoft.com/en-us/windows/security/threat-protection/microsoft-defender-antivirus/common-exclusion-mistakes-microsoft-defender-antivirus)
- [File Type settings for .ts files](https://superuser.com/a/1464304)

## Windows Exodus

Things about windows that are starting to bug me and push me toward trying out Linux:

- No standard application install / update / uninstall method. It's the wild west. Apps can do whatever weird thing they want. If I want to be safe, I need to verify checksums myself (assuming they're even provided).
- ConPty compatibility with in-band terminal control sequences is not there yet. To be honest, I'm tired of running into problems and waiting for fixes.
- Archaic, scattered, inconsistent system configuration facilities and UI.
- Complicated filesystem indexing and access control with scattered, archaic, and clunky configuration interface.
- Constant antivirus performance hits when running programs which process many files such as compilers or VCS TUI such as lazygit.
- Need to create a Microsoft account to use it (one more important password I won't need to use enough to want to remember, which will bite me when I need to remember it).

I don't use anything that requires me to use windows. I use VS Code, Chrome, MSYS2, and some electron apps. Sometimes I use a drawing application, and sometimes I play music files. I don't play games on my laptop.
