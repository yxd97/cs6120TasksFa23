#include <map>
#include <vector>
#include "llvm/Pass.h"
#include "llvm/IR/Instructions.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/IR/Operator.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Analysis/LoopPass.h"
#include "llvm/Analysis/LoopInfo.h"
#include "llvm/Support/raw_ostream.h"

using namespace llvm;


namespace {

int get_instr_max_len(LoopInfo &LI) {
    int max_len = 0;
    for (auto &L : LI) {
        for (auto &B : L->blocks()) {
            for (auto &I : *B) {
                std::string i_str;
                raw_string_ostream ss(i_str);
                ss << I;
                if (max_len < i_str.length()) {
                    max_len = i_str.length();
                }
            }
        }
    }
    return max_len;
}

void pretty_print_instr(raw_ostream &os, Instruction &I, int line_width) {
    std::string i_str;
    raw_string_ostream ss(i_str);
    ss << I;
    for (int i = i_str.length(); i < line_width; i++) {
        ss << " ";
    }
    os << i_str;
}

class LICM: public PassInfoMixin<LICM> {
private:

    /// Determine if an instruction is loop-invariant
    /// return true if the instruction is loop-invariant
    /// otherwise, return false
    bool is_all_operands_li(Instruction &I, Loop &L) {
        bool is_loop_invariant = true;
        for (Value* operand : I.operands()) {
            is_loop_invariant &= L.isLoopInvariant(operand);
        }
        return is_loop_invariant;
    }

    /// Determine if an instruction is safe to be moved
    /// return true if the instruction is safe to be moved
    /// otherwise, return false
    bool is_safe_to_move(Instruction &I, DominatorTree &DT, bool print_to_errs = false) {
        // see if this definition dominates all its uses
        auto def = DT.getNode(I.getParent());
        bool all_uses_dominated = true;
        for (auto &U : I.uses()) {
            bool real_dominated = false;
            if (auto user = dyn_cast<Instruction>(U.getUser())) {
                auto use = DT.getNode(user->getParent());
                real_dominated = DT.dominates(def, use);
            }
            // a corner case: if the use is a phi node,
            // and there are no other definitions coming into this phi
            // we can treat is as "dominated"
            bool phi_dominated = true;
            if (auto phi = dyn_cast<PHINode>(U.getUser())) {
                unsigned in_vals = phi->getNumIncomingValues();
                for (unsigned i = 0; i < in_vals; i++) {
                    auto val = phi->getIncomingValue(i);
                    if (auto cst = dyn_cast<UndefValue>(val)) {
                        continue;
                    }
                    if (val == &I) {
                        continue;
                    }
                    phi_dominated = false;
                    break;
                }
            }
            all_uses_dominated &= (real_dominated || phi_dominated);
        }
        // see if there could be side effects
        bool se_write_mem = I.mayWriteToMemory();
        bool se_call = isa<CallInst>(&I) || isa<InvokeInst>(&I);
        bool se_except = I.mayThrow();
        bool no_side_effects = !se_write_mem && !se_call && !se_except;
        // see if this instruction terminates a basic block
        bool not_a_terminator = !I.isTerminator();
        if (print_to_errs) {
            errs() << "["
                   << all_uses_dominated
                   << no_side_effects
                   << not_a_terminator
                   << "]";
        }
        return all_uses_dominated && no_side_effects && not_a_terminator;
    }

    /// Move an instruction to a loop's preheader
    /// return true if the instruction is moved
    /// otherwise, return false
    bool move_instr_to_preheader(Instruction* I, Loop &L) {
        auto preheader = L.getLoopPreheader();
        if (preheader) {
            I->moveBefore(preheader->getTerminator());
            return true;
        }
        return false;
    }

    bool licm(Loop &L, DominatorTree &DT) {
        // find all LI code
        std::vector<Instruction*> movable_instrs;
        for (auto &B : L.blocks()) {
            for (auto &I : *B) {
                if (is_all_operands_li(I, L) && is_safe_to_move(I, DT)) {
                    movable_instrs.push_back(&I);
                }
            }
        }
        // move them
        bool changed = false;
        for (auto I : movable_instrs) {
            changed |= move_instr_to_preheader(I, L);
        }
        return changed;
    }

    void print_loops(LoopInfo &LI, DominatorTree &DT) {
        int max_len = get_instr_max_len(LI);
        for (auto &L : LI) {
            L->print(errs());
            for (auto &B : L->blocks()) {
                B->printAsOperand(errs(), false);
                errs() << ":\n";
                for (auto &I : *B) {
                    pretty_print_instr(errs(), I, max_len);
                    errs() << "  ; ";
                    if (auto phi = dyn_cast<PHINode>(&I)) {
                        unsigned num_in_vals = phi->getNumIncomingValues();
                        errs() << "{";
                        for (unsigned i = 0; i < num_in_vals; i++) {
                            auto val = phi->getIncomingValue(i);
                            if (auto cst = dyn_cast<UndefValue>(val)) {
                                errs() << "undef";
                            } else {
                                val->printAsOperand(errs());
                            }
                            if (i < num_in_vals - 1) {
                                errs() << ", ";
                            }
                        }
                        errs() << "}";
                    }
                    if (is_all_operands_li(I, *L)) {
                        errs() << "[LI] ";
                        is_safe_to_move(I, DT, true);
                    }
                    errs() << "\n";
                }
            }
        }
    }

public:
    PreservedAnalyses run(Function &F, FunctionAnalysisManager &FAM) {
        LoopInfo &LI = FAM.getResult<LoopAnalysis>(F);
        if (LI.getTopLevelLoopsVector().size() > 0) {
            DominatorTree &DT = FAM.getResult<DominatorTreeAnalysis>(F);
            errs() << "Loops in " << F.getName() << "\n";
            // print_loops(LI, DT);
            for (auto &L : LI) {
                licm(*L, DT);
            }
            return PreservedAnalyses::none();
        }
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
                            LICM()
                        )
                    );
                }
            );
        }
    };
}
