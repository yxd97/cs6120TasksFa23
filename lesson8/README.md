## LLVM Pass: Loop-Invariant Code Motion (LICM)
All build and testing processes have been automated by `run.sh`.
It's usage can be obtained by running `./run.sh -h` or `./run.sh --help`.

### Source Code
The source code for the LICM pass is located in `LICM/LICM.cpp`.

### Build
You can either build the test programs with or without the LICM optimization.
This is done by setting the `-t` option of `run.sh` to either `base` or `opt`.

To specify which test porgram to build,
simply pass the program file name **without the extension**
to `run.sh`. To build all programs, set the `--all` option
(in this case, the program input will be ignored).

E.g., to build the optimized version of `polybench-gemm.c`,
run `./run.sh -t opt polybench-gemm`.

An additional `--dump-ir` option may be specified
to output the LLVM IR instead of building the program executable.

The pass will be automatically built.

### Test
To test the pass, please specify the target to be `test`.
The script will first compare the optimized and un-optimized IRs.
If there is no difference, a warning shall appear to ask you double check if this is by design.
The script will also run the original and optimized programs and compare their outputs.
If the outputs mismatch, an error will be raised.

**Note**: The baseline IR is set to be the output of applying `mem2reg` on the `O0` optimization level.
That is because `mem2reg` will turn the IR into a standard SSA form with phi nodes, instead of
having lots of memory accesses to model mutable variables.
