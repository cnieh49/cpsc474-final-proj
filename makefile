mcts:
	echo "#!/bin/bash" > Test2048
	echo "pypy3 test_2048.py \"\$$@\"" >> Test2048
	chmod u+x Test2048

clean:
	rm -f Test2048