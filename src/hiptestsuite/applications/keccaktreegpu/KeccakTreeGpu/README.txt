Compiling using Microsoft Visual Studio : 
After installing Cuda SDK and toolkit, use the project file in \VCKeccakTree.

Testing software on Windows with a Nvidia recent card (>= 8800 GT), even without the cuda toolkit should be ok with the executable (to be renamed in .exe) and the runtime dll included in release folder of VS project.


Compiling under Linux :
After installing Cuda SDK and toolkit, use the included Makefile. the Path to cuda SDK and toolkit must be changed in this Makefile. Beware of the 64 bits target used  (could be easily changed to 32 bits).

Description of Source files:

KeccakF.c : Implementation of Keccak function on CPU 

KeccakTree.h : Definition of constants (number of threads, size of input blocks, output blocks, etc...)

KeccakTreeCPU.c : Implementation of Keccak tree hash mode on CPU only

KeccakTreeGPU.cu : Cuda code of implementation of Keccak tree hash on GPU 

KeccakTypes.h : Types definition

main.c : main file

Test.c : Implementation of test functions of different modes, performance mesure.

