#!/bin/bash
help() {
    echo "Usage: $0 [options] [input]"
    echo "Options:"
    echo "  -t, --target <target>  Target to build (base, opt)"
    echo "  --all                  Build all programs"
    echo "  --dump-ir              Dump IR instead of building"
    echo "  -h, --help             Show this help"
    echo "Input:"
    echo "  <input>                Input file to build"
    echo "                        (ignored if --all is set)"
}

run_make() {
    case $1 in
        base)
            eval "make base PROGRAM=$2"
        ;;
        base_ir)
            eval "make base_ir PROGRAM=$2"
        ;;
        opt)
            eval "make opt PROGRAM=$2"
        ;;
        opt_ir)
            eval "make opt_ir PROGRAM=$2"
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

ALL_PROGS=(
    hello_world
)

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
    done
else
    if [[ $dump_ir -eq 1 ]]; then
        run_make ${target}_ir $input
    else
        run_make $target $input
    fi
fi

exit 0
