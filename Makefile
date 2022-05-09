.SECONDARY:

test_results/ga.beam.%:
	python3 test_models.py 0 > $@

test_results/ga.regular.%:
	python3 test_models.py 2 > $@

test_results/nce.beam.%:
	python3 test_models.py 1 > $@

test_results/nce.regular.%:
	python3 test_models.py 3 > $@

%.ten: test_results/%.0 test_results/%.1 test_results/%.2 test_results/%.3 test_results/%.4 test_results/%.5 test_results/%.6 test_results/%.7 test_results/%.8 test_results/%.9
	true