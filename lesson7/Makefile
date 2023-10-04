CXX = $(LLVM)/bin/clang

CXX_FLAGS += -O0

SRC_DIR = tests
BUILD_DIR = build
PASS_NAME = IMulToSftAdd
PASS_SRC = $(PASS_NAME)/$(PASS_NAME).cpp

$(BUILD_DIR)/$(PASS_NAME)/$(PASS_NAME).so: $(PASS_SRC)
	cd $(BUILD_DIR); make

.PHONY: pass
pass: $(BUILD_DIR)/$(PASS_NAME)/$(PASS_NAME).so

ALL_PROGS :=

ALL_PROGS += $(BUILD_DIR)/imul
$(BUILD_DIR)/imul: $(SRC_DIR)/imul.c
	mkdir -p $(BUILD_DIR)
	$(CXX) $(CXX_FLAGS) $< -o $@

ALL_PROGS += $(BUILD_DIR)/powsOfTwo
$(BUILD_DIR)/powsOfTwo: $(SRC_DIR)/powsOfTwo.c
	mkdir -p $(BUILD_DIR)
	$(CXX) $(CXX_FLAGS) $< -o $@

ALL_PROGS += $(BUILD_DIR)/positive
$(BUILD_DIR)/positive: $(SRC_DIR)/positive.c
	mkdir -p $(BUILD_DIR)
	$(CXX) $(CXX_FLAGS) $< -o $@

ALL_PROGS += $(BUILD_DIR)/negative
$(BUILD_DIR)/negative: $(SRC_DIR)/negative.c
	mkdir -p $(BUILD_DIR)
	$(CXX) $(CXX_FLAGS) $< -o $@

.PHONY: all-progs
all-progs: $(ALL_PROGS)

ALL_PROGS_IMSA :=

ALL_PROGS_IMSA += $(BUILD_DIR)/imul-imsa
$(BUILD_DIR)/imul-imsa: $(SRC_DIR)/imul.c $(BUILD_DIR)/$(PASS_NAME)/$(PASS_NAME).so
	mkdir -p $(BUILD_DIR)
	$(CXX) $(CXX_FLAGS) -fpass-plugin=$(BUILD_DIR)/$(PASS_NAME)/$(PASS_NAME).so $< -o $@

ALL_PROGS_IMSA += $(BUILD_DIR)/powsOfTwo-imsa
$(BUILD_DIR)/powsOfTwo-imsa: $(SRC_DIR)/powsOfTwo.c $(BUILD_DIR)/$(PASS_NAME)/$(PASS_NAME).so
	mkdir -p $(BUILD_DIR)
	$(CXX) $(CXX_FLAGS) -fpass-plugin=$(BUILD_DIR)/$(PASS_NAME)/$(PASS_NAME).so $< -o $@

ALL_PROGS_IMSA += $(BUILD_DIR)/positive-imsa
$(BUILD_DIR)/positive-imsa: $(SRC_DIR)/positive.c $(BUILD_DIR)/$(PASS_NAME)/$(PASS_NAME).so
	mkdir -p $(BUILD_DIR)
	$(CXX) $(CXX_FLAGS) -fpass-plugin=$(BUILD_DIR)/$(PASS_NAME)/$(PASS_NAME).so $< -o $@

ALL_PROGS_IMSA += $(BUILD_DIR)/negative-imsa
$(BUILD_DIR)/negative-imsa: $(SRC_DIR)/negative.c $(BUILD_DIR)/$(PASS_NAME)/$(PASS_NAME).so
	mkdir -p $(BUILD_DIR)
	$(CXX) $(CXX_FLAGS) -fpass-plugin=$(BUILD_DIR)/$(PASS_NAME)/$(PASS_NAME).so $< -o $@

.PHONY: all-progs-imsa
all-progs-imsa: $(ALL_PROGS_IMSA)

.PHONY: all
all: pass all-progs all-progs-imsa

.PHONY: clean clean-progs
clean:
	rm -f *.out *.llvm $(BUILD_DIR)/*.llvm

clean-progs:
	rm -f $(ALL_PROGS) $(ALL_PROGS_IMSA)
