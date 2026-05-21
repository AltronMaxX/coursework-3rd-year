{ pkgs ? import <nixpkgs> {} }:

let
  crossPkgs = pkgs.pkgsCross.riscv64;

  # Объединяем нужные пакеты с прошивками в одну виртуальную директорию
  firmwareEnv = pkgs.symlinkJoin {
    name = "kernel-firmware-merged";
    paths = [
      pkgs.wireless-regdb
      pkgs.linux-firmware
    ];
  };

in
pkgs.mkShell {
  nativeBuildInputs = [
    pkgs.buildPackages.stdenv.cc
    pkgs.gnumake
    pkgs.pkg-config
    pkgs.bison
    pkgs.flex
    pkgs.bc
    pkgs.elfutils
    pkgs.openssl
    pkgs.ncurses
    pkgs.rsync
    pkgs.kmod
    pkgs.qemu
    crossPkgs.stdenv.cc
  ];

  buildInputs = with pkgs; [
    (python3.withPackages (ps: with ps; [
      pyserial
    ]))
  ];

  shellHook = ''
    export ARCH=riscv
    export CROSS_COMPILE=riscv64-unknown-linux-gnu-
    export HOSTCC=gcc

    # Указываем на объединенную директорию
    export NIX_FIRMWARE_DIR="${firmwareEnv}/lib/firmware"

    echo "--- RISC-V Environment Loaded ---"
    echo "ARCH: $ARCH"
    echo "Firmware DIR: $NIX_FIRMWARE_DIR"

    echo "================================================="
    echo " Найдено окружение для логгера Arduino!"
    echo " Доступные порты в системе:"
    ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null || echo " [!] Порты не найдены. Подключите Arduino."
    echo " Активируйте логгер: python logger.py"
    echo "================================================="
  '';
}
