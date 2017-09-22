# brainfreeze

[Fully Homomorphic Encryption](https://en.wikipedia.org/wiki/Homomorphic_encryption) is this hip new thing all the cool crypto kids are talking about.
It lets you operate on encrypted ciphertexts - so that anyone can compute the encrypted result of some function without ever knowing what the inputs really were (or even what the output really was).

Brainfreeze is a fully homomorphic compiler and runtime for [Brainfuck](https://en.wikipedia.org/wiki/Brainfuck). This means it takes encrypted Brainfuck programs as an input, evaluates them homomorphically, and returns their encrypted output, without learning anything from the entire process. Let's call it **Fully Homomorphic Computing**.

To the best of my knowledge, this is the first time a Turing-complete language has been implemented in FHE [1]. 
This is probably because FHE is excruciatingly slow: using [TFHE](https://tfhe.github.io/tfhe/), each boolean gate takes 10-20 milliseconds to evaluate. 
With an 8-bit architecture and 16 bytes of RAM, Brainfreeze sputters along at around 0.1 hertz (1 cycle every 10 seconds) on a 2017 Macbook Pro.

The bytes of RAM affect speed because the instruction pointer is encrypted along with every other register. 
Since we never actually know which instruction we're executing, or where the data pointer is, Brainfreeze has to execute every possible operation on every possible memory address on every clock cycle.
This is a general problem with FHE: every branch in your control flow has to be explored and recombined at the end.
There's no way around it without leaking information about your inputs.

[1] [This paper](https://www.researchgate.net/publication/258628022_Towards_a_working_fully_homomorphic_crypto-processor_Practice_and_the_secret_computer) discusses "the possibility" of fully homomorphic computing but makes no attempt at implementation.
