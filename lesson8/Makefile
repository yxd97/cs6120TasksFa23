CXX = clang

CXX_FLAGS += -O0 -Xclang -disable-O0-optnone

SRC_DIR = tests
BUILD_DIR = build
PASS_NAME = LICM
PASS_SRC = $(PASS_NAME)/$(PASS_NAME).cpp

PROGRAM := $(PROGRAM)

### to build the hand-written pass
$(BUILD_DIR)/Makefile:
	mkdir -p $(BUILD_DIR); cd $(BUILD_DIR); cmake ..

$(BUILD_DIR)/$(PASS_NAME)/$(PASS_NAME).so: $(PASS_SRC) $(BUILD_DIR)/Makefile
	cd $(BUILD_DIR); make

### to build the test program

# generate llvm ir first
$(BUILD_DIR)/$(PROGRAM).ll: $(SRC_DIR)/$(PROGRAM).c
	mkdir -p $(BUILD_DIR)
	$(CXX) $(CXX_FLAGS) -S -emit-llvm $< -o $@

# then apply mem2reg pass
$(BUILD_DIR)/$(PROGRAM)_m2r.ll: $(BUILD_DIR)/$(PROGRAM).ll
	mkdir -p $(BUILD_DIR)
	opt -mem2reg -S $< -o $@

# build the baseline program
$(BUILD_DIR)/$(PROGRAM): $(BUILD_DIR)/$(PROGRAM)_m2r.ll
	mkdir -p $(BUILD_DIR)
	$(CXX) $(CXX_FLAGS) $< -o $@

# also apply hand-written pass
$(BUILD_DIR)/$(PROGRAM)_$(PASS_NAME).ll: $(BUILD_DIR)/$(PROGRAM)_m2r.ll $(BUILD_DIR)/$(PASS_NAME)/$(PASS_NAME).so
	mkdir -p $(BUILD_DIR)
	$(CXX) $(CXX_FLAGS) -fpass-plugin=$(BUILD_DIR)/$(PASS_NAME)/$(PASS_NAME).so -S -emit-llvm $< -o $@

# finally build executable
$(BUILD_DIR)/$(PROGRAM)_$(PASS_NAME): $(BUILD_DIR)/$(PROGRAM)_$(PASS_NAME).ll $(SRC_DIR)/$(PROGRAM).c
	mkdir -p $(BUILD_DIR)
	$(CXX) $(CXX_FLAGS) $< -o $@

.PHONY: clean
clean:
	rm -f $(BUILD_DIR)/$(PROGRAM)
	rm -f $(BUILD_DIR)/$(PROGRAM).ll
	rm -f $(BUILD_DIR)/$(PROGRAM)_m2r.ll
	rm -f $(BUILD_DIR)/$(PROGRAM)_$(PASS_NAME).ll
	rm -f $(BUILD_DIR)/$(PROGRAM)_$(PASS_NAME)
