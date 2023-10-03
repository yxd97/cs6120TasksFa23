#include "llvm/Pass.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Support/raw_ostream.h"

using namespace llvm;

namespace {

struct BoolAlgInInt : public PassInfoMixin<BoolAlgInInt> {
    PreservedAnalyses run(Module &M, ModuleAnalysisManager &AM) {
        for (auto &F : M) {
            std::string fname = F.getName().str();
            if (fname.starts_with("bool_func")) {
                for (auto &B : F) {
                    for (auto &I : B) {
                        auto* op = dyn_cast<BinaryOperator>(&I);
                        if (op) {
                            IRBuilder<> builder(op);
                            Value* lhs = op->getOperand(0);
                            Value* rhs = op->getOperand(1);
                            Value* mul = builder.CreateMul(lhs, rhs);
                            for (auto &U: op->uses()){
                                User* user = U.getUser();
                                user->setOperand(U.getOperandNo(), mul);
                            }
                            errs() << I << "// BinOp\n";
                        } else {
                            errs() << I << '\n';
                        }

                    }
                }
            }
        }
        return PreservedAnalyses::all();
    };
};

}

extern "C" LLVM_ATTRIBUTE_WEAK ::llvm::PassPluginLibraryInfo
llvmGetPassPluginInfo() {
    return {
        .APIVersion = LLVM_PLUGIN_API_VERSION,
        .PluginName = "Skeleton pass",
        .PluginVersion = "v0.1",
        .RegisterPassBuilderCallbacks = [](PassBuilder &PB) {
            PB.registerPipelineStartEPCallback(
                [](ModulePassManager &MPM, OptimizationLevel Level) {
                    MPM.addPass(BoolAlgInInt());
                });
        }
    };
}
