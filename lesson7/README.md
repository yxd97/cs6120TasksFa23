## LLVM Pass: Integer Multiplication to Shift and Add (IMSA)
This pass turns the multiplication with integer constants into
a series of left shift and adds.

For example:
```
x * 10
```

is the same as:
```
(x << 1) + (x << 3)

```
### Set $LLVM to be the llvm installation path
Scripts in this task all work on an environment variable named `LLVM`.
Please make sure it points to the llvm installation directory.

For example, if llvm is installed at `/usr/bin/llvm-17`, you should do:
```
export LLVM = /usr/bin/llvm-17
```
so that `$LLVM/bin/clang` is using the clang compiler shipped with llvm.

### Build the pass
```
mkdir build
cd build
cmake ..
make
```

After setting up the build directory, you can also build the pass
with the top-level makefile:
```
# in lesson7
make pass
```

### Build the original/transformed binaries
The top-level makefile will build the programs used for testing.
Simply do `make all`.

### Turnt testing envs
There are four testing environments for turnt:
 * `dump_llvm`: save the llvm IR of the original program. Make sure you use the `--save` option of turnt.
 * `dump_imsa_llvm`: save the llvm IR of the transformed program. Make sure you use the `--save` option of turnt.
 * `run`: execute the original program.
 * `run_imsa`: execute the transformed program. The output should be the same as `run`.
