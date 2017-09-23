# brainfreeze

### FHE
**[Fully Homomorphic Encryption](https://en.wikipedia.org/wiki/Homomorphic_encryption)** is this hip new thing all the cool crypto kids are talking about.
It lets you operate on encrypted ciphertexts - so that anyone can compute the encrypted result of some function without ever knowing what the inputs really were (or even what the output really was). 

People are pretty excited about this because it promises some wild applications. This is one of them!

### FHC
**Fully Homomorphic Computing** is a term I just made up to describe a fully homomorphic *programming language*. This is when the function that we homomorphically evaluate is the `eval` function itself. The input is code, and the output is the result of running that code.

Brainfreeze is a fully homomorphic compiler and runtime for [Brainfuck](https://en.wikipedia.org/wiki/Brainfuck). This means it takes encrypted Brainfuck programs as an input, runs them, and returns their encrypted output, without learning anything from the entire process. To the best of my knowledge, this is the first actual implementation of fully homomorphic computing.

This is probably because FHE is excruciatingly slow: using the [TFHE](https://tfhe.github.io/tfhe/) C library, each boolean operation on two encrypted bits takes 10-20 milliseconds to evaluate. 
With an 8-bit architecture and 16 bytes of RAM, Brainfreeze sputters along at around 0.1 hertz (1 cycle every 10 seconds) on a 2017 Macbook Pro.

The bytes of RAM affect speed because the data pointer is encrypted along with every other register. 
Since we never actually know where the data pointer is, or which instruction we're executing, Brainfreeze has to execute every possible operation on every possible memory address on every clock cycle.
This is a general problem with FHE: every branch in your control flow has to be explored and recombined at the end.
There's no way around it without leaking information about your inputs.

### Brainfreeze

Brainfreeze is a stack of three abstraction layers:

1. A Python wrapper for the TFHE library. This is `tfhe.py` and `tfhe_utils.py`. They're written using `ctypes` and is probably the most useful and resusable part of this whole thing.
2. A collection of homomorphic circuits (adders, muxes, RAM) built from TFHE gates. They inherit from the `Circuit` class in `circuits.py`.
3. A minimal Brainfuck computer similar in design to [this one](https://github.com/briandef/bf16). `Computer` is a circuit from `circuits.py` but the interface in `brainfreeze.py` exposes `compile`, `evaluate`, and `decompile` functions to interact with it concisely.

### API

Help I'm Trapped In A Homomorphic Reality
