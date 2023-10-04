#include "llvm/Pass.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Support/raw_ostream.h"

using namespace llvm;

namespace {

struct IMulToSftAdd : public PassInfoMixin<IMulToSftAdd> {
    PreservedAnalyses run(Module &M, ModuleAnalysisManager &AM) {
        for (auto &F : M) {
            LLVMContext& context = F.getContext();
            for (auto &B : F) {
                Type* i32_t = IntegerType::getInt32Ty(context);
                for (auto &I : B) {
                    auto* op = dyn_cast<BinaryOperator>(&I);
                    if (op) {
                        auto opcode = op->getOpcode();
                        if (opcode == Instruction::Mul) {

                            // see if it's var * const or const * var
                            Value* lhs = op->getOperand(0);
                            Value* rhs = op->getOperand(1);
                            Value* var;
                            ConstantInt* lcst = dyn_cast<ConstantInt>(lhs);
                            ConstantInt* rcst = dyn_cast<ConstantInt>(rhs);
                            ConstantInt* cst;
                            if (lcst && !rcst) {
                                cst = lcst;
                                var = rhs;
                            } else if (!lcst && rcst) {
                                cst = rcst;
                                var = lhs;
                            } else {
                                // skip var * var
                                // skip const * const, this should be cautured
                                // by constant propagation
                                continue;
                            }

                            // initialize the IR builder
                            IRBuilder<> builder(op);
                            builder.SetInsertPoint(&B, ++builder.GetInsertPoint());

                            // initialize new value to zero
                            Constant* zero = ConstantInt::get(i32_t, 0);
                            Value* new_val = builder.CreateAdd(zero, zero);

                            // factor the const into sum of powers of 2
                            int mask = 1;
                            int cst_val = cst->getSExtValue();
                            for (int i = 0; i < 32; i++) {
                                int bit = cst_val & mask;
                                if (bit) {
                                    Constant* smt = ConstantInt::get(i32_t, i);
                                    Value* incr = builder.CreateShl(var, smt);
                                    new_val = builder.CreateAdd(new_val, incr);
                                }
                                mask = mask << 1;
                            }

                            // update uses of the original op
                            for (auto &U: op->uses()){
                                User* user = U.getUser();
                                user->setOperand(U.getOperandNo(), new_val);
                            }
                        }
                    }
                }
            }
        }
        return PreservedAnalyses::none();
    };
};

}

extern "C" LLVM_ATTRIBUTE_WEAK ::llvm::PassPluginLibraryInfo
llvmGetPassPluginInfo() {
    return {
        .APIVersion = LLVM_PLUGIN_API_VERSION,
        .PluginName = "IMulToSftAdd pass",
        .PluginVersion = "v0.1",
        .RegisterPassBuilderCallbacks = [](PassBuilder &PB) {
            PB.registerPipelineStartEPCallback(
                [](ModulePassManager &MPM, OptimizationLevel Level) {
                    MPM.addPass(IMulToSftAdd());
                });
        }
    };
}
