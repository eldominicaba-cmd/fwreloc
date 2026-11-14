# raw firmware 1 (old, 1 native function) and "new" (2 native functions), no ELF header
import os
import subprocess


def build(firmware: str, code: str) -> None:
    c = firmware + ".src.c"
    obj = firmware + ".src.o"
    open(c, "w").write(code)
    subprocess.run(["gcc", "-Os", "-c", c, "-o", obj], check=True)
    subprocess.run(["objcopy", "-O", "binary", "-j", ".text", obj, firmware], check=True)
    os.remove(c)
    os.remove(obj)


build("tests/fixtures/raw/old.bin",
      "int a(void){return 1;}\n"
      "int b(void){return 2;}\n"
      "void init(void){}\n")
build("tests/fixtures/raw/new.bin",
      "int a(void){return 3;}\n"
      "int b(void){return 4;}\n"
      "int c(void){return 99;}\n"
      "void init(void){}\n")
print("raw fixtures built")
