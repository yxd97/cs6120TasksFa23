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
            LLVMContext& context = F.getContext();
            errs() << fname << '\n';
            if (fname.rfind("bool_func", 0) == 0) {
                for (auto &B : F) {
                    Type* i1_t = IntegerType::getInt1Ty(context);
                    Constant* one = ConstantInt::get(i1_t, 1);
                    for (auto &I : B) {
                        auto* op = dyn_cast<BinaryOperator>(&I);
                        if (op) {
                            auto opcode = op->getOpcode();
                            Value *lhs, *rhs, *newop;
                            Constant *cst;
                            IRBuilder<> builder(op);
                            User* user;
                            switch (opcode) {
                                case Instruction::And:
                                // rewrite and to mul
                                    lhs = op->getOperand(0);
                                    rhs = op->getOperand(1);
                                    newop = builder.CreateMul(lhs, rhs);
                                    for (auto &U: op->uses()){
                                        user = U.getUser();
                                        user->setOperand(U.getOperandNo(), newop);
                                    }
                                break;
                                case Instruction::Or:
                                // rewrite or to add
                                    lhs = op->getOperand(0);
                                    rhs = op->getOperand(1);
                                    newop = builder.CreateAdd(lhs, rhs);
                                    for (auto &U: op->uses()){
                                        user = U.getUser();
                                        user->setOperand(U.getOperandNo(), newop);
                                    }
                                break;
                                case Instruction::Xor:
                                // rewrite not to 1-
                                    lhs = op->getOperand(0);
                                    rhs = op->getOperand(1);
                                    // errs() << I << " // ";
                                    cst = dyn_cast<Constant>(rhs);
                                    if (cst && cst->isOneValue()) {
                                        // errs() << "using xor true as not\n";
                                        newop = builder.CreateSub(one, lhs);
                                        for (auto &U: op->uses()){
                                            user = U.getUser();
                                            user->setOperand(U.getOperandNo(), newop);
                                        }
                                    }
                                break;
                                default:
                                break;
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
        .PluginName = "BoolAlgInInt pass",
        .PluginVersion = "v0.1",
        .RegisterPassBuilderCallbacks = [](PassBuilder &PB) {
            PB.registerPipelineStartEPCallback(
                [](ModulePassManager &MPM, OptimizationLevel Level) {
                    MPM.addPass(BoolAlgInInt());
                });
        }
    };
}
