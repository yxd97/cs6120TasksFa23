CXX = $(LLVM)/bin/clang

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

.PHONY: all-progs
all-progs: $(ALL_PROGS)

ALL_PROGS_BAII :=

ALL_PROGS_BAII += $(BUILD_DIR)/and-baii
$(BUILD_DIR)/and-baii: $(SRC_DIR)/and.c $(BUILD_DIR)/$(PASS_NAME)/$(PASS_NAME).so
	mkdir -p $(BUILD_DIR)
	$(CXX) -fpass-plugin=$(BUILD_DIR)/$(PASS_NAME)/$(PASS_NAME).so $< -o $@

ALL_PROGS_BAII += $(BUILD_DIR)/or-baii
$(BUILD_DIR)/or-baii: $(SRC_DIR)/or.c $(BUILD_DIR)/$(PASS_NAME)/$(PASS_NAME).so
	mkdir -p $(BUILD_DIR)
	$(CXX) -fpass-plugin=$(BUILD_DIR)/$(PASS_NAME)/$(PASS_NAME).so $< -o $@

ALL_PROGS_BAII += $(BUILD_DIR)/not-baii
$(BUILD_DIR)/not-baii: $(SRC_DIR)/not.c $(BUILD_DIR)/$(PASS_NAME)/$(PASS_NAME).so
	mkdir -p $(BUILD_DIR)
	$(CXX) -fpass-plugin=$(BUILD_DIR)/$(PASS_NAME)/$(PASS_NAME).so $< -o $@

ALL_PROGS_BAII += $(BUILD_DIR)/xor-baii
$(BUILD_DIR)/xor-baii: $(SRC_DIR)/xor.c $(BUILD_DIR)/$(PASS_NAME)/$(PASS_NAME).so
	mkdir -p $(BUILD_DIR)
	$(CXX) -fpass-plugin=$(BUILD_DIR)/$(PASS_NAME)/$(PASS_NAME).so $< -o $@

ALL_PROGS_BAII += $(BUILD_DIR)/de-morgan-baii
$(BUILD_DIR)/de-morgan-baii: $(SRC_DIR)/de-morgan.c $(BUILD_DIR)/$(PASS_NAME)/$(PASS_NAME).so
	mkdir -p $(BUILD_DIR)
	$(CXX) -fpass-plugin=$(BUILD_DIR)/$(PASS_NAME)/$(PASS_NAME).so $< -o $@

ALL_PROGS_BAII += $(BUILD_DIR)/full-adder-baii
$(BUILD_DIR)/full-adder-baii: $(SRC_DIR)/full-adder.c $(BUILD_DIR)/$(PASS_NAME)/$(PASS_NAME).so
	mkdir -p $(BUILD_DIR)
	$(CXX) -fpass-plugin=$(BUILD_DIR)/$(PASS_NAME)/$(PASS_NAME).so $< -o $@

.PHONY: all-progs-baii
all-progs-baii: $(ALL_PROGS_BAII)

.PHONY: all
all: pass all-progs all-progs-baii

.PHONY: clean
clean:
	rm *.out *.llvm
