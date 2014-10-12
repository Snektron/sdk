# Project variables
TARGET_MODEL:=TI84pSE
SDK=.knightos/
INCLUDE=$(SDK)include/;$(SDK)
AS:={{ assembler }}
EMU:={{ emulator }}
DEBUGGER:={{ debugger }}
ASFLAGS:=--encoding "Windows-1252" --include "$(INCLUDE)"
GENKFS:=genkfs
KPACK:=kpack
.DEFAULT_GOAL=all
INIT:=/bin/{{ project_name }}

OUT:=bin/
ROOT:=$(OUT)root/
BIN:=$(ROOT)bin/
ETC:=$(ROOT)etc/
VAR:=$(ROOT)var/
SHARE:=$(ROOT)share/
