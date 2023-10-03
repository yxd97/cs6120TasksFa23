CXX = $(LLVM)/bin/clang

SRC_DIR = tests
BUILD_DIR = build
PASS_DIR = BoolAlgInInt/build/BoolAlgInInt
PASS_NAME = BoolAlgInInt.so
ALL_PROGS :=

ALL_PROGS += $(BUILD_DIR)/and
$(BUILD_DIR)/and: $(SRC_DIR)/and.c
	mkdir -p $(BUILD_DIR)
	$(CXX) $< -o $@

ALL_PROGS += $(BUILD_DIR)/or
$(BUILD_DIR)/or: $(SRC_DIR)/or.c
	mkdir -p $(BUILD_DIR)
	$(CXX) $< -o $@

ALL_PROGS += $(BUILD_DIR)/not
$(BUILD_DIR)/not: $(SRC_DIR)/not.c
	mkdir -p $(BUILD_DIR)
	$(CXX) $< -o $@

ALL_PROGS += $(BUILD_DIR)/xor
$(BUILD_DIR)/xor: $(SRC_DIR)/xor.c
	mkdir -p $(BUILD_DIR)
	$(CXX) $< -o $@

ALL_PROGS += $(BUILD_DIR)/de-morgan
$(BUILD_DIR)/de-morgan: $(SRC_DIR)/de-morgan.c
	mkdir -p $(BUILD_DIR)
	$(CXX) $< -o $@

ALL_PROGS += $(BUILD_DIR)/full-adder
$(BUILD_DIR)/full-adder: $(SRC_DIR)/full-adder.c
	mkdir -p $(BUILD_DIR)
	$(CXX) $< -o $@

.PHONY: all
all: $(ALL_PROGS)

