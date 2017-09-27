# brainfreeze

### FHE
**[Fully Homomorphic Encryption](https://en.wikipedia.org/wiki/Homomorphic_encryption)** is this hip new thing all the cool crypto kids are talking about.
It lets you operate on encrypted ciphertexts - so that anyone can compute the encrypted result of some function without ever knowing what the inputs really were (or even what the output really was). 

People are pretty excited about this because it promises some wild applications, like truly secure cloud computing or truly anonymous smart contracts.

### FHC
**Fully Homomorphic Computing** is something I just made up to describe fully homomorphic *programming languages*. 
This is when the function that we homomorphically evaluate is the `eval` function itself. 
The input is encrypted code, and the output is the encrypted result of running that code.
But the computer itself never actually knows what it's executing!

Brainfreeze is a fully homomorphic computer for the [Brainfuck](https://en.wikipedia.org/wiki/Brainfuck) language. 
This means it takes encrypted Brainfuck programs as an input, runs them, and returns their encrypted output, without learning anything from the entire process.
It's built on the [TFHE](https://tfhe.github.io/tfhe/) library, and to the best of my knowledge, it's is the first actual implementation of fully homomorphic computing.

This is probably because FHE is excruciatingly slow: with TFHE, each boolean operation on two encrypted bits takes 10-20 milliseconds to evaluate. 
With an 8-bit architecture and 16 bytes of RAM, Brainfreeze sputters along at around 0.1 hertz (1 cycle every 10 seconds) on a 2017 Macbook Pro. 😬

The size of RAM affects speed because the data pointer is encrypted (along with every other register). 
Since we never actually know where the data pointer points, or which instruction we're executing, Brainfreeze has to execute every possible operation on every possible memory address on every clock cycle, and pretend to update each one.
This is a general problem with FHE: every path through your control flow has to be explored and recombined at the end.
There's no way around it without leaking information about your inputs; we must surrender to the Tyranny of Exponential Branch Unrolling.

FHE efficiency has jumped several orders of magnitude in the last few years, which will hopefully continue. It's also [theoretically possible](https://eprint.iacr.org/2013/229) to sidestep exponential branch unrolling if you're willing to leak a little bit of information about your program's runtime. So FHC is comically useless for now, but there's no better time to start thinking about it.

### Brainfreeze

Brainfreeze is a stack of three abstraction layers:

1. A Python wrapper for the TFHE library. This is `tfhe.py` and `tfhe_utils.py`. They're written using `ctypes` and is probably the most useful part of this whole rigmarole.
2. A collection of homomorphic circuits (adders, muxes, RAM, CPU) built from TFHE gates. They inherit from the `Circuit` class in `circuits.py`. The CPU design is inspired by [this one](https://github.com/briandef/bf16).
3. A minimal Brainfuck computer. See it in action in `main.py`.

## API

1. [Install TFHE](https://tfhe.github.io/tfhe/installation.html).

2. Clone this repo and edit `tfhe.py` and `makefile` to reference the right version of TFHE. [1] The defaults are for `libtfhe-spqlios-fma`, which is what you get when you compile TFHE with the `-DENABLE_SPQLIOS_FMA=on` flag. If you've already installed TFHE and don't remember what version it is, you can probably find it with `ls /usr/local/lib | grep libtfhe`.

3. Compile the Python wrapper. [2]
```shell
git clone https://github.com/joeltg/brainfreeze
cd brainfreeze
make
```

4. Profit
```python
from main import *from circuits import *

secret = create_secret_keyset(GATE_PARAMS)
cloud = get_cloud_keyset(secret)

TRUE.eval(cloud)
FALSE.eval(cloud)

rom = compile_code("++[-]", secret)

computer = Computer(rom)
computer.init(cloud)

computer.eval(cloud)
```

You can also read and write ciphertextst to files with `import_ciphertext` and `export_ciphertext`.

[1] "Isn't this what makfiles are supposed to replace?" Yes.

[2] This `tfhe_io.c` wrapper is actually *just* for I/O. The TFHE functions to read and write ciphertexts and gate parameters to and from files takes `FILE*` objects, which I can't figure out how to pass into a `ctypes` function in Python. So `tfhe_io.c` has wrapper functions that take file paths as string literals, which gets compiled and then dynamically loaded in `tfhe_utils.py`. If anyone has a real solution to this, please tell me.

`<marquee><blink> ~ ~ ~ HeLp I'm TrApPeD iN a HoMoMoRpHiC rEaLiTy ~ ~ ~ </blink></marquee>`
