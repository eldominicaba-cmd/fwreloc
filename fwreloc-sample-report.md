# fwreloc report — worked sample (real input)

**Firmware pair:** OpenWrt x86-64 bzImage, two service releases of the same
device build.

| | Old | New |
|---|---|---|
| Source file | fw_25.12.5.bin | fw_25.12.6.bin |
| Linux kernel | 6.12.94 | 6.12.112 |
| Type | bzImage, x86_64 | bzImage, x86_64 |

**Diff summary**

| | Old | New |
|---|---|---|
| Functions | 126 | 132 |
| Added | 129 | |
| Removed | | 123 |
| Changed | | |

**Changed functions**

| Name | Old offset | New offset | Old size | New size | Note |
|---|---|---|---|---|---|
| fcn.00573240 | 0x573240 | 0x573240 | 8 bytes | 241 bytes | added ~233 bytes of code (see detail) |

**Executive summary (≤ 150 words)**

Between the 25.12.5 and 25.12.6 service releases of this OpenWrt x86_64 kernel
build, the native-code inventory grew by 129 functions and lost 123, with 1
function expanded from 8 bytes to 241 bytes. The net functional growth is small
and the bulk of the change is new-init/cleanup code, not a behavioural change.
Compatibility is expected to hold unless one of the 123 removed functions was
exposed directly by a custom build; verify against the boot log before
deploying.

**Added / removed examples**

| Category | Representative examples |
|---|---|
| Added (129) | fcn.00063d28, fcn.00246b38, fcn.00579936, (…) |
| Removed (123) | fewest shown; internals rotated |

**Method + limits**
- Tool: fwreloc (radare2 auto-analysis, read-only binary diff).
- Red lines: no patching, no re-patch, no anti-cheat/online/DRM access.
- Scope: this is a **read-only diff of one firmware pair**; it does not
  explain every added function's purpose and does not test the firmware on a
  real device.

**Next steps / EOL**
- Confirm the 1 changed function was not part of a custom ABI you rely on.
- Boot both images and compare kernel log (dmesg) before promoting 25.12.6.
