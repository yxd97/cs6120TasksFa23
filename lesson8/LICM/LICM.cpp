#include "llvm/Pass.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Analysis/LoopPass.h"
#include "llvm/Analysis/LoopInfo.h"
#include "llvm/Support/raw_ostream.h"

using namespace llvm;


namespace {

class PrintLoop: public PassInfoMixin<PrintLoop> {
private:
    void print_loops(LoopInfo &LI) {
        for (auto &L : LI) {
            L->print(errs());
        }
    }
public:
    PreservedAnalyses run(Function &F, FunctionAnalysisManager &FAM) {
        errs() << F.getName() << "\n";
        LoopInfo &LI = FAM.getResult<LoopAnalysis>(F);
        DominatorTree &DT = FAM.getResult<DominatorTreeAnalysis>(F);
        DT.print(errs());
        errs() << "Loops in " << F.getName() << "\n";
        print_loops(LI);
        return PreservedAnalyses::all();
    }
};

} // namespace

extern "C" LLVM_ATTRIBUTE_WEAK ::llvm::PassPluginLibraryInfo
llvmGetPassPluginInfo() {
    return {
        .APIVersion = LLVM_PLUGIN_API_VERSION,
        .PluginName = "Loop Invariant Code Motion",
        .PluginVersion = "v0.1",
        .RegisterPassBuilderCallbacks = [](PassBuilder &PB) {
            PB.registerPipelineStartEPCallback(
                [](ModulePassManager &MPM, OptimizationLevel Level) {
                    MPM.addPass(
                        createModuleToFunctionPassAdaptor(
                            PrintLoop()
                        )
                    );
                }
            );
        }
    };
}
