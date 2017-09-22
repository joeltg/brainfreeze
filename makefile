# replace "-ltfhe-spqlios-fma" with the right version of TFHE from tfhe_utils.py
all: build
build:
	gcc -shared -Wl,-install_name,tfhe_io.so -L/usr/local/lib -ltfhe-spqlios-fma -o tfhe_io.so -fPIC tfhe_io.c
clean:
	rm -f tfhe_io.so