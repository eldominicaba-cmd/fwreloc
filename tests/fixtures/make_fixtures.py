# synthetic firmware "old" (1 native function) and "new" (2 functions)
import subprocess

open("old_fw.c", "w").write(
    "int boot_stack(void){return 42;}\n"
    "int fw_check(void){return 7;}\n"
    "void firmware_main(void){}\n"
)
open("new_fw.c", "w").write(
    "int boot_stack(void){return 44;}\n"
    "int fw_check(void){return 11;}\n"
    "int new_feature(void){return 99;}\n"
    "void firmware_main(void){}\n"
)
subprocess.run(["gcc", "-Os", "-c", "old_fw.c", "-o", "tests/fixtures/old_fw.o"], check=True)
subprocess.run(["gcc", "-Os", "-c", "new_fw.c", "-o", "tests/fixtures/new_fw.o"], check=True)
print("fixtures built")
