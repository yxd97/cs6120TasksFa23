CXX = $(LLVM)/bin/clang

CXX_FLAGS += -O0 -Xclang -disable-O0-optnone

SRC_DIR = tests
BUILD_DIR = build
PASS_NAME = LICM
PASS_SRC = $(PASS_NAME)/$(PASS_NAME).cpp

PROGRAM := $(PROGRAM)

### to build the LICM pass
$(BUILD_DIR)/Makefile:
	mkdir -p $(BUILD_DIR); cd $(BUILD_DIR); cmake ..

$(BUILD_DIR)/$(PASS_NAME)/$(PASS_NAME).so: $(PASS_SRC) $(BUILD_DIR)/Makefile
	cd $(BUILD_DIR); make

.PHONY: pass
pass: $(BUILD_DIR)/$(PASS_NAME)/$(PASS_NAME).so

### to build the test program
.PHONY: base opt bese_ir opt_ir

# with original clang
$(BUILD_DIR)/$(PROGRAM): $(SRC_DIR)/$(PROGRAM).c
	$(CXX) $(CXX_FLAGS) $< -o $@
base: $(BUILD_DIR)/$(PROGRAM)

# with LICM pass
$(BUILD_DIR)/$(PROGRAM)_$(PASS_NAME): $(SRC_DIR)/$(PROGRAM).c $(BUILD_DIR)/$(PASS_NAME)/$(PASS_NAME).so
	$(CXX) $(CXX_FLAGS) -fpass-plugin=$(BUILD_DIR)/$(PASS_NAME)/$(PASS_NAME).so $< -o $@
opt: $(BUILD_DIR)/$(PROGRAM)_$(PASS_NAME)

# original IR
$(BUILD_DIR)/$(PROGRAM).ll: $(SRC_DIR)/$(PROGRAM).c
	$(CXX) $(CXX_FLAGS) -S -emit-llvm $< -o $@
base_ir: $(BUILD_DIR)/$(PROGRAM).ll

# optimized IR
$(BUILD_DIR)/$(PROGRAM)_$(PASS_NAME).ll: $(SRC_DIR)/$(PROGRAM).c $(BUILD_DIR)/$(PASS_NAME)/$(PASS_NAME).so
	$(CXX) $(CXX_FLAGS) -S -emit-llvm -fpass-plugin=$(BUILD_DIR)/$(PASS_NAME)/$(PASS_NAME).so $< -o $@
opt_ir: $(BUILD_DIR)/$(PROGRAM)_$(PASS_NAME).ll
