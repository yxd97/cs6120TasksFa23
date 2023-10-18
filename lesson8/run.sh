#!/bin/bash
build_dir="build"

ALL_PROGS=(
    "basic"
    "predefine"
    "first-pass"
    "loop-variant"
    "polybench-gemm"
    "polybench-gramschmidt"
    "polybench-jacobi-2d"
    "polybench-nussinov"
)

help() {
    echo "Usage: $0 [options] [input]"
    echo "Options:"
    echo "  -t, --target <target>  Target to build (base, opt, clean)"
    echo "  --all                  Build all programs"
    echo "  --dump-ir              Dump IR instead of building"
    echo "  -h, --help             Show this help"
    echo "Input:"
    echo "  <input>                Input file to build"
    echo "                         (ignored if --all is set)"
}

verify() {
    # arg $1: program (test case) name
    eval "make $build_dir/$1 PROGRAM=$1"
    eval "make $build_dir/${1}_LICM PROGRAM=$1"
    eval "make $build_dir/${1}_m2r.ll PROGRAM=$1"
    eval "make $build_dir/${1}_LICM.ll PROGRAM=$1"
    diff <(tail -n +2 $build_dir/${1}_m2r.ll) <(tail -n +2 $build_dir/${1}_LICM.ll) > /dev/null
    if [[ $? -eq 0 ]]; then
        echo "WARNING: IR of program \`$1' is not changed! Please check if it's by design!"
    fi
    eval "./$build_dir/$1 > $build_dir/$1.stdout"
    eval "./$build_dir/${1}_LICM > $build_dir/${1}_LICM.stdout"
    diff $build_dir/$1.stdout $build_dir/${1}_LICM.stdout
    if [[ $? -eq 0 ]]; then
        echo "Test on program \`$1' passed"
        return 0
    else
        echo "ERROR: Test on \`$1' failed, program output mismatch!"
        return 1
    fi
}

run_make() {
    # arg $1: target (base, opt, test, clean)
    # arg $2: program (test case) name
    case $1 in
        base)
            eval "make $build_dir/$2 PROGRAM=$2"
            eval "./$build_dir/$2"
            return $?
        ;;
        base_ir)
            eval "make $build_dir/$2.ll PROGRAM=$2"
            return $?
        ;;
        opt)
            eval "make $build_dir/${2}_LICM PROGRAM=$2"
            eval "./$build_dir/${2}_LICM"
            return $?
        ;;
        opt_ir)
            eval "make $build_dir/${2}_LICM.ll PROGRAM=$2"
            return $?
        ;;
        test)
            verify $2
            return $?
        ;;
        clean)
            eval "make clean PROGRAM=$2"
            return 0
        ;;
        *)
            echo "Unknown target $1"
            exit 1
        ;;
    esac
}

if [[ $# -eq 0 ]]; then
    help
    exit 1
fi

make_all_progs=0
dump_ir=0
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            help
            exit 0
        ;;
        --all)
            make_all_progs=1
            shift # past argument
        ;;
        --dump-ir)
            dump_ir=1
            shift # past argument
        ;;
        -t|--target)
            target=$2
            shift # past argument
            shift # past value
        ;;
        -*|--*)
            echo "Unknown option $1"
            exit 1
        ;;
        *)
        if [[ $target_all_progs -eq 1 ]]; then
            echo "Ignoring input file $1 because --all option is set"
        else
            input=$1
        fi
        shift # past argument
        ;;
    esac
done

if [[ $make_all_progs -eq 1 ]]; then
    for prog in "${ALL_PROGS[@]}"; do
        if [[ $dump_ir -eq 1 ]]; then
            run_make ${target}_ir $prog
        else
            run_make $target $prog
        fi
        if [[ $? -ne 0 ]]; then
            echo "===== ERROR: Test failed. ====="
            exit 1
        fi
    done
else
    if [[ $dump_ir -eq 1 ]]; then
        run_make ${target}_ir $input
    else
        run_make $target $input
    fi
    if [[ $? -ne 0 ]]; then
        echo "===== ERROR: Test failed. ====="
        exit 1
    fi
fi

echo "===== Test passed. ====="
exit 0
