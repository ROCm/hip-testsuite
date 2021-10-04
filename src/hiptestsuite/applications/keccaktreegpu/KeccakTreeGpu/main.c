/*
GPU Implementation of Keccak by Guillaume Sevestre, 2010

This code is hereby put in the public domain.
It is given as is, without any guarantee.
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <time.h>

//Cuda
#include <hip/hip_runtime.h>
#include <hip/hip_runtime.h>



#include "KeccakF.h"
#include "KeccakTreeCPU.h"
#include "KeccakTreeGPU.h"
#include "Test.h"





int main()
{
   
	

	Device_Info();

	Print_Param();

	//Test_Completness();

	/*
	TestCPU(1);
	
	TestGPU();

	TestGPU_OverlapCPU();

	//TestGPU_Split();

	TestGPU_Stream();

	TestGPU_Stream_OverlapCPU();
	*/
	
	

	TestCPU_2stg(80);

	TestGPU_2stg();

	TestGPU_2stg_Stream_OverlapCPU();

	

	TestGPU_SCipher();
	

    return 0;
}
