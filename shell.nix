{ pkgs ? import <nixpkgs> {} }:

let
  # In most nixpkgs versions, the attribute is simply 'riscv64'
  crossPkgs = pkgs.pkgsCross.riscv64;
in
pkgs.mkShell {
  nativeBuildInputs = [
    # Host tools (x86_64)
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

    # The actual RISC-V cross-toolchain
    crossPkgs.stdenv.cc
  ];

  shellHook = ''
    export ARCH=riscv
    # Nix provides the compiler with this specific triplet prefix
    export CROSS_COMPILE=riscv64-unknown-linux-gnu-
    export HOSTCC=gcc

    echo "--- RISC-V Environment Loaded ---"
    echo "ARCH: $ARCH"
    echo "CROSS_COMPILE: $CROSS_COMPILE"
    echo "Host GCC: $(gcc --version | head -n1)"
    echo "Cross GCC: $(${"$"}{CROSS_COMPILE}gcc --version | head -n1)"
  '';
}