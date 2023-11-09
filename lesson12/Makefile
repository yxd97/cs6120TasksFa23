PY := python3
PARSER := bril2json
INTERP := brili
TRACE_INTERP := brili-tr --trace

OPTIMIZER = trace_optimizer.py

PROGRAM := simple_loop
SUITE := tests
ARGS :=

$(SUITE)/$(PROGRAM).trace: $(SUITE)/$(PROGRAM).bril
	@$(PARSER) < $< | $(TRACE_INTERP) $(ARGS) 2> $@

$(SUITE)/$(PROGRAM).out: $(SUITE)/$(PROGRAM).bril
	@$(PARSER) < $< | $(INTERP) $(ARGS) > $@

$(SUITE)/$(PROGRAM).bril.optimize: $(SUITE)/$(PROGRAM).bril $(SUITE)/$(PROGRAM).trace $(OPTIMIZER)
	@$(PARSER) < $< | $(PY) $(OPTIMIZER) $(SUITE)/$(PROGRAM).trace > $@

.PHONY: ref trace opt check clean cleanall

ref: $(SUITE)/$(PROGRAM).out

trace: $(SUITE)/$(PROGRAM).trace

opt: $(SUITE)/$(PROGRAM).bril.optimize

check: $(SUITE)/$(PROGRAM).bril.optimize $(SUITE)/$(PROGRAM).out
	@$(PARSER) < $< | $(INTERP) $(ARGS) > $(SUITE)/$(PROGRAM).optimize.out
	@diff -q $(SUITE)/$(PROGRAM).optimize.out $(SUITE)/$(PROGRAM).out

clean:
	rm -f tests/*.trace

cleanall: clean
	rm -f tests/*.out
	rm -f tests/*.bril.optimize
	rm -f tests/*.result
