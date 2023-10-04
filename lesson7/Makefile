CXX = $(LLVM)/bin/clang

CXX_FLAGS += -O3

SRC_DIR = tests
BUILD_DIR = build
PASS_NAME = BoolAlgInInt
PASS_SRC = $(PASS_NAME)/$(PASS_NAME).cpp

$(BUILD_DIR)/$(PASS_NAME)/$(PASS_NAME).so: $(PASS_SRC)
	cd $(BUILD_DIR); make

.PHONY: pass
pass: $(BUILD_DIR)/$(PASS_NAME)/$(PASS_NAME).so

ALL_PROGS :=

ALL_PROGS += $(BUILD_DIR)/and
$(BUILD_DIR)/and: $(SRC_DIR)/and.c
	mkdir -p $(BUILD_DIR)
	$(CXX) $(CXX_FLAGS) $< -o $@

.PHONY: all-progs
all-progs: $(ALL_PROGS)

ALL_PROGS_BAII :=

ALL_PROGS_BAII += $(BUILD_DIR)/and-baii
$(BUILD_DIR)/and-baii: $(SRC_DIR)/and.c $(BUILD_DIR)/$(PASS_NAME)/$(PASS_NAME).so
	mkdir -p $(BUILD_DIR)
	$(CXX) $(CXX_FLAGS) -fpass-plugin=$(BUILD_DIR)/$(PASS_NAME)/$(PASS_NAME).so $< -o $@

.PHONY: all-progs-baii
all-progs-baii: $(ALL_PROGS_BAII)

.PHONY: all
all: pass all-progs all-progs-baii

.PHONY: clean clean-progs
clean:
	rm -f *.out *.llvm $(BUILD_DIR)/*.llvm

clean-progs:
	rm -f $(ALL_PROGS) $(ALL_PROGS_BAII)
