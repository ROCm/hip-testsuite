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

#define IMAX 1600 //2400 // 1600 for high speed mesures // iteration for speed mesure loops


//debug print function
void print_out(tKeccakLane * h_outBuffer,int nb_threads)
{
printf("%08x ",h_outBuffer[0]);printf("%08x ",h_outBuffer[1]);
printf("%08x ",h_outBuffer[nb_threads]);printf("%08x ",h_outBuffer[nb_threads +1]);
printf("\n\n");
}



void TestCPU(int reduc)
{
	time_t t1,t2;
	double speed1;
	int i;

	tKeccakLane *h_inBuffer;// Host in buffer for data to be hashed
	tKeccakLane *h_outBuffer;// Host out buffer 

	tKeccakLane Kstate[25]; //Keccak State for top node
	memset(Kstate, 0, 25 * sizeof(tKeccakLane));


	//init host inBuffer 
	h_inBuffer=(tKeccakLane *) malloc( INPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS * NB_INPUT_BLOCK );
	memset(h_inBuffer, 0, INPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS * NB_INPUT_BLOCK);

	//init host outBuffer	
	h_outBuffer=(tKeccakLane *) malloc( OUTPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS );
	memset(h_outBuffer, 0, OUTPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS );

	//***************************
	//init h_inBuffer with values
	for(i=0;i<INPUT_BLOCK_SIZE_B/4 * NB_INPUT_BLOCK * NB_THREADS*NB_THREADS_BLOCKS;i++ )
	{h_inBuffer[i]=i;}

	
	//CPU computation *******************************
	printf("CPU speed test started \n");	
	
	t1=time(NULL);
	for(i=0;i<(IMAX/reduc);i++)
	{
		KeccakTreeCPU(h_inBuffer,h_outBuffer);

		//print_out(h_outBuffer,NB_THREADS);

		Keccak_top(Kstate,h_outBuffer,NB_THREADS*NB_THREADS_BLOCKS);
	}
	t2=time(NULL);

	print_KS_256(Kstate);

	speed1= (INPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS * NB_INPUT_BLOCK *(IMAX/(reduc*1000.)))  / ((t2-t1) + 0.01);
	printf("CPU speed : %.2f kB/s \n\n",speed1);


	//free all buffer host and device
	free(h_inBuffer);
	free(h_outBuffer); 	


}

void TestGPU()
{

	time_t t1,t2;
	double speed1;
	unsigned int i;

	tKeccakLane *h_inBuffer;// Host in buffer for data to be hashed
	tKeccakLane *h_outBuffer;// Host out buffer 

	tKeccakLane *d_inBuffer; // device in buffer
	tKeccakLane *d_outBuffer;// device out buffer 

	tKeccakLane Kstate[25]; //Keccak State for top node
	memset(Kstate, 0, 25 * sizeof(tKeccakLane));


	//init host inBuffer 
	h_inBuffer=(tKeccakLane *) malloc( INPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS * NB_INPUT_BLOCK );
	memset(h_inBuffer, 0, INPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS * NB_INPUT_BLOCK);

	//init host outBuffer	
	h_outBuffer=(tKeccakLane *) malloc( OUTPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS );
	memset(h_outBuffer, 0, OUTPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS );

	//init device inBuffer
	hipMalloc((void **)&d_inBuffer, INPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS * NB_INPUT_BLOCK );
	checkCUDAError(" hipMalloc d_inBuffer");
	hipMemset(d_inBuffer,0,INPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS * NB_INPUT_BLOCK);
	checkCUDAError(" hipMemset d_inBuffer");

	//init device outBuffer
	hipMalloc((void **)&d_outBuffer, OUTPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS );
	checkCUDAError(" hipMalloc d_outBuffer");
	hipMemset(d_outBuffer,0, OUTPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS);
	checkCUDAError(" hipMemset d_outBuffer");

	//***************************
	//init h_inBuffer with values
	for(i=0;i<INPUT_BLOCK_SIZE_B/4 * NB_INPUT_BLOCK * NB_THREADS*NB_THREADS_BLOCKS;i++ )
	{h_inBuffer[i]=i;}

	//GPU computation *******************************
	printf("GPU speed test started\n");
	
	t1=time(NULL);
	for(i=0;i<IMAX;i++)
	{
		KeccakTreeGPU(h_inBuffer,d_inBuffer,h_outBuffer,d_outBuffer);
		//print_out(h_outBuffer,NB_THREADS*NB_THREADS_BLOCKS);

		Keccak_top(Kstate,h_outBuffer,NB_THREADS*NB_THREADS_BLOCKS);
		//print_KS_256(Kstate);
	}

	t2=time(NULL);
	
	print_KS_256(Kstate);

	speed1= (INPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS * NB_INPUT_BLOCK *(IMAX/1000.))  / ((t2-t1) + 0.01);
	printf("GPU speed : %.2f kB/s \n\n",speed1);


	//free all buffer host and device
	free(h_inBuffer);
	free(h_outBuffer); 	

	hipFree(d_inBuffer);
	hipFree(d_outBuffer);

}



void TestGPU_OverlapCPU()
{

	time_t t1,t2;
	double speed1;
	int i;

	tKeccakLane *h_inBuffer;// Host in buffer for data to be hashed
	tKeccakLane *h_outBuffer;// Host out buffer 

	tKeccakLane *d_inBuffer; // device in buffer
	tKeccakLane *d_outBuffer;// device out buffer 

	tKeccakLane Kstate[25]; //Keccak State for top node
	memset(Kstate, 0, 25 * sizeof(tKeccakLane));


	//init host inBuffer 
	h_inBuffer=(tKeccakLane *) malloc( INPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS * NB_INPUT_BLOCK );
	memset(h_inBuffer, 0, INPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS * NB_INPUT_BLOCK);

	//init host outBuffer	
	h_outBuffer=(tKeccakLane *) malloc( OUTPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS );
	memset(h_outBuffer, 0, OUTPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS );

	//init device inBuffer
	hipMalloc((void **)&d_inBuffer, INPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS * NB_INPUT_BLOCK );
	checkCUDAError(" hipMalloc d_inBuffer");
	hipMemset(d_inBuffer,0,INPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS * NB_INPUT_BLOCK);
	checkCUDAError(" hipMemset d_inBuffer");

	//init device outBuffer
	hipMalloc((void **)&d_outBuffer, OUTPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS );
	checkCUDAError(" hipMalloc d_outBuffer");
	hipMemset(d_outBuffer,0, OUTPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS);
	checkCUDAError(" hipMemset d_outBuffer");

	//***************************
	//init h_inBuffer with values
	for(i=0;i<INPUT_BLOCK_SIZE_B/4 * NB_INPUT_BLOCK * NB_THREADS*NB_THREADS_BLOCKS;i++ )
	{h_inBuffer[i]=i;}


	//GPU computation *******************************

	printf("GPU speed overlap CPU test started \n");

	t1=time(NULL);

	//first iteration 
	KeccakTreeGPU(h_inBuffer,d_inBuffer,h_outBuffer,d_outBuffer);
	
	//print_out(h_outBuffer,NB_THREADS*NB_THREADS_BLOCKS);
	//print_KS_256(Kstate);


	//other iteration overlapping GPU computation with CPU
	for(i=1;i<IMAX;i++)
	{
		KeccakTreeGPU_overlapCPU(h_inBuffer,d_inBuffer,h_outBuffer,d_outBuffer,Kstate);
		
		//print_out(h_outBuffer,NB_THREADS*NB_THREADS_BLOCKS);
		//print_KS_256(Kstate);
		
	}
	//last output block on CPU
	Keccak_top(Kstate,h_outBuffer,NB_THREADS*NB_THREADS_BLOCKS);

	t2=time(NULL);
	print_KS_256(Kstate);

		speed1= (INPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS * NB_INPUT_BLOCK *(IMAX/1000.))  / ((t2-t1) + 0.01);
	printf("GPU speed overlap CPU : %.2f kB/s \n\n",speed1);

	//free all buffer host and device
	free(h_inBuffer);
	free(h_outBuffer); 	

	hipFree(d_inBuffer);
	hipFree(d_outBuffer);

}



void TestGPU_Split()
{

	time_t t1,t2;
	double speed1;
	int i;

	tKeccakLane *h_inBuffer;// Host in buffer for data to be hashed
	tKeccakLane *h_outBuffer;// Host out buffer 

	tKeccakLane *d_inBuffer; // device in buffer
	tKeccakLane *d_outBuffer;// device out buffer 

	tKeccakLane Kstate[25]; //Keccak State for top node
	memset(Kstate, 0, 25 * sizeof(tKeccakLane));


	//init host inBuffer 
	h_inBuffer=(tKeccakLane *) malloc( INPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS * NB_INPUT_BLOCK );
	memset(h_inBuffer, 0, INPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS * NB_INPUT_BLOCK);

	//init host outBuffer	
	h_outBuffer=(tKeccakLane *) malloc( OUTPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS );
	memset(h_outBuffer, 0, OUTPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS );

	//init device inBuffer
	hipMalloc((void **)&d_inBuffer, INPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS * NB_INPUT_BLOCK );
	checkCUDAError(" hipMalloc d_inBuffer");
	hipMemset(d_inBuffer,0,INPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS * NB_INPUT_BLOCK);
	checkCUDAError(" hipMemset d_inBuffer");

	//init device outBuffer
	hipMalloc((void **)&d_outBuffer, OUTPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS );
	checkCUDAError(" hipMalloc d_outBuffer");
	hipMemset(d_outBuffer,0, OUTPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS);
	checkCUDAError(" hipMemset d_outBuffer");

	//***************************
	//init h_inBuffer with values
	for(i=0;i<INPUT_BLOCK_SIZE_B/4 * NB_INPUT_BLOCK * NB_THREADS*NB_THREADS_BLOCKS ; i++ )
	{h_inBuffer[i]=i;}

	//GPU computation *******************************

	t1=time(NULL);
	for(i=0;i<IMAX;i++)
	{
		KeccakTreeGPU_Split(h_inBuffer,d_inBuffer,h_outBuffer,d_outBuffer);
		//print_out(h_outBuffer,NB_THREADS*NB_THREADS_BLOCKS);

		Keccak_top(Kstate,h_outBuffer,NB_THREADS*NB_THREADS_BLOCKS);
		//print_KS_256(Kstate);
	}

	t2=time(NULL);
	
	print_KS_256(Kstate);

	speed1= (INPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS * NB_INPUT_BLOCK *(IMAX/1000.))  / ((t2-t1) + 0.01);
	printf("GPU Split speed : %.2f kB/s \n\n",speed1);


	//free all buffer host and device
	free(h_inBuffer);
	free(h_outBuffer); 	

	hipFree(d_inBuffer);
	hipFree(d_outBuffer);

}

void TestGPU_Stream()
{

	time_t t1,t2;
	double speed1;
	int i;

	tKeccakLane *h_inBuffer=NULL;	// Host in buffer for data to be hashed
	tKeccakLane *h_outBuffer=NULL;	// Host out buffer 

	tKeccakLane *d_inBuffer; // device in buffer
	tKeccakLane *d_outBuffer;// device out buffer 

	tKeccakLane Kstate[25]; //Keccak State for top node
	memset(Kstate, 0, 25 * sizeof(tKeccakLane));


	//alloc host inBuffer WITH CudaHostAlloc 
	hipHostMalloc( (void **)&h_inBuffer, INPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS * NB_INPUT_BLOCK,
		hipHostMallocDefault);
	checkCUDAError("hipHostMalloc h_inBuffer");

	memset(h_inBuffer, 0, INPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS * NB_INPUT_BLOCK);

	//alloc host outBuffer WITH CudaHostAlloc 
	hipHostMalloc( (void **)&h_outBuffer, OUTPUT_BLOCK_SIZE_B * NB_THREADS * NB_THREADS_BLOCKS,
		hipHostMallocDefault);
	checkCUDAError("hipHostMalloc h_outBuffer");

	memset(h_outBuffer, 0, OUTPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS);

	//init device inBuffer
	hipMalloc((void **)&d_inBuffer, INPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS * NB_INPUT_BLOCK );
	checkCUDAError(" hipMalloc d_inBuffer");
	hipMemset(d_inBuffer,0,INPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS * NB_INPUT_BLOCK);
	checkCUDAError(" hipMemset d_inBuffer");

	//init device outBuffer
	hipMalloc((void **)&d_outBuffer, OUTPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS );
	checkCUDAError(" hipMalloc d_outBuffer");
	hipMemset(d_outBuffer,0, OUTPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS);
	checkCUDAError(" hipMemset d_outBuffer");

	//***************************
	//init h_inBuffer with values
	for(i=0;i<INPUT_BLOCK_SIZE_B/4 * NB_INPUT_BLOCK * NB_THREADS*NB_THREADS_BLOCKS ; i++ )
	{h_inBuffer[i]=i;}

	//GPU computation *******************************
	printf("GPU Stream speed test started \n");
	
	t1=time(NULL);
	for(i=0;i<IMAX;i++)
	{
		KeccakTreeGPU_Stream(h_inBuffer,d_inBuffer,h_outBuffer,d_outBuffer);
		//print_out(h_outBuffer,NB_THREADS*NB_THREADS_BLOCKS);

		Keccak_top(Kstate,h_outBuffer,NB_THREADS*NB_THREADS_BLOCKS);
		//print_KS_256(Kstate);
	}

	t2=time(NULL);
	
	print_KS_256(Kstate);

	speed1= (INPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS * NB_INPUT_BLOCK *(IMAX/1000.))  / ((t2-t1) + 0.01);
	printf("GPU Stream speed : %.2f kB/s \n\n",speed1);


	//free all buffer host and device
	hipHostFree(h_inBuffer);
	hipHostFree(h_outBuffer); 	

	hipFree(d_inBuffer);
	hipFree(d_outBuffer);

}


void TestGPU_Stream_OverlapCPU()
{

	time_t t1,t2;
	double speed1;
	int i;

	tKeccakLane *h_inBuffer=NULL;	// Host in buffer for data to be hashed
	tKeccakLane *h_outBuffer=NULL;	// Host out buffer 

	tKeccakLane *d_inBuffer; // device in buffer
	tKeccakLane *d_outBuffer;// device out buffer 

	tKeccakLane Kstate[25]; //Keccak State for top node
	memset(Kstate, 0, 25 * sizeof(tKeccakLane));


	//alloc host inBuffer WITH CudaHostAlloc 
	hipHostMalloc( (void **)&h_inBuffer, INPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS * NB_INPUT_BLOCK,
		hipHostMallocDefault);
	checkCUDAError("hipHostMalloc h_inBuffer");

	memset(h_inBuffer, 0, INPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS * NB_INPUT_BLOCK);

	//alloc host outBuffer WITH CudaHostAlloc 
	hipHostMalloc( (void **)&h_outBuffer, OUTPUT_BLOCK_SIZE_B * NB_THREADS * NB_THREADS_BLOCKS,
		hipHostMallocDefault);
	checkCUDAError("hipHostMalloc h_outBuffer");

	memset(h_outBuffer, 0, OUTPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS);

	//init device inBuffer
	hipMalloc((void **)&d_inBuffer, INPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS * NB_INPUT_BLOCK );
	checkCUDAError(" hipMalloc d_inBuffer");
	hipMemset(d_inBuffer,0,INPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS * NB_INPUT_BLOCK);
	checkCUDAError(" hipMemset d_inBuffer");

	//init device outBuffer
	hipMalloc((void **)&d_outBuffer, OUTPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS );
	checkCUDAError(" hipMalloc d_outBuffer");
	hipMemset(d_outBuffer,0, OUTPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS);
	checkCUDAError(" hipMemset d_outBuffer");

	//***************************
	//init h_inBuffer with values
	for(i=0;i<INPUT_BLOCK_SIZE_B/4 * NB_INPUT_BLOCK * NB_THREADS*NB_THREADS_BLOCKS ; i++ )
	{h_inBuffer[i]=i;}

	//GPU computation *******************************
	printf("GPU Stream OverlapCPU speed test started \n");	

	t1=time(NULL);

	//first iteration WITH STREAMS
	KeccakTreeGPU_Stream(h_inBuffer,d_inBuffer,h_outBuffer,d_outBuffer);

	for(i=1;i<IMAX;i++)
	{
		KeccakTreeGPU_Stream_OverlapCPU(h_inBuffer,d_inBuffer,h_outBuffer,d_outBuffer,Kstate);
		//print_out(h_outBuffer,NB_THREADS*NB_THREADS_BLOCKS);

		
	}
	//last CPU computation
	Keccak_top(Kstate,h_outBuffer,NB_THREADS*NB_THREADS_BLOCKS);

	t2=time(NULL);
	
	print_KS_256(Kstate);

	speed1= (INPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS * NB_INPUT_BLOCK *(IMAX/1000.))  / ((t2-t1) + 0.01);
	printf("GPU Stream OverlapCPU speed : %.2f kB/s \n\n",speed1);


	//free all buffer host and device
	hipHostFree(h_inBuffer);
	hipHostFree(h_outBuffer); 	

	hipFree(d_inBuffer);
	hipFree(d_outBuffer);

}



// Using Mapped memory 
// UNTESTED not supported by Author's GPU Hardware
void TestGPU_MappedMemory()
{

	time_t t1,t2;
	double speed1;
	int i;


	tKeccakLane *h_inBuffer;// Host in buffer for data to be hashed
	tKeccakLane *h_outBuffer;// Host out buffer 

	tKeccakLane *d_inBuffer; // device in buffer pointer
	tKeccakLane *d_outBuffer;// device out buffer pointer

	// check device Prop
	struct hipDeviceProp_t deviceProp ;
	int device=0;

	tKeccakLane Kstate[25]; //Keccak State for top node
	memset(Kstate, 0, 25 * sizeof(tKeccakLane));


	// Get properties and verify device 0 supports mapped memory
	hipGetDeviceProperties(&deviceProp, 0);
	checkCUDAError("hipGetDeviceProperties");


	if(!deviceProp.canMapHostMemory) {
		fprintf(stderr, "Device %d cannot map host memory!\n", 0);
		exit(EXIT_FAILURE);
	}


	//init host inBuffer WITH CudaHostAlloc 
	hipHostMalloc((void **)&h_inBuffer,INPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS * NB_INPUT_BLOCK ,
		hipHostMallocMapped);
	checkCUDAError("hipHostMalloc Mapped inBuffer");

	memset(h_inBuffer, 0, INPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS * NB_INPUT_BLOCK);


	//init host outBuffer WITH CudaHostAlloc 
	hipHostMalloc((void **)&h_outBuffer,OUTPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS ,
		hipHostMallocMapped);
	checkCUDAError("hipHostMalloc Mapped outBuffer");

	memset(h_outBuffer, 0, OUTPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS);

	//retreive device pointer to inBuffer mapped memory
	hipHostGetDevicePointer((void **)&d_inBuffer, (void *)h_inBuffer, 0);
	checkCUDAError("hipHostGetDevicePointer d_inBuffer");

	//retreive device pointer to outBuffer mapped memory
	hipHostGetDevicePointer((void **)&d_outBuffer, (void *)h_outBuffer, 0);
	checkCUDAError("hipHostGetDevicePointer d_outBuffer");


	//GPU computation *******************************

	t1=time(NULL);
	for(i=0;i<IMAX;i++)
	{
		KeccakTreeGPU(h_inBuffer,d_inBuffer,h_outBuffer,d_outBuffer);
		//print_out(h_outBuffer,NB_THREADS);

		Keccak_top(Kstate,h_outBuffer,NB_THREADS*NB_THREADS_BLOCKS);
	}

	t2=time(NULL);
	print_KS_256(Kstate);
	
	speed1= (INPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS * NB_INPUT_BLOCK *(IMAX/1000.))  / ((t2-t1) + 0.01);
	printf("GPU speed Mapped : %.2f kB/s \n",speed1);


	//free all host buffers and device pointers
	hipHostFree(h_inBuffer);
	hipHostFree(h_outBuffer); 	

}

//**************************************************
// Use 2 stages hashtree
//**************************************************
void TestCPU_2stg(int reduc)
{
	time_t t1,t2;
	double speed1;
	int i;

	tKeccakLane *h_inBuffer;// Host in buffer for data to be hashed
	tKeccakLane *h_outBuffer;// Host out buffer 

	tKeccakLane Kstate[25]; //Keccak State for top node
	memset(Kstate, 0, 25 * sizeof(tKeccakLane));


	//init host inBuffer 
	h_inBuffer=(tKeccakLane *) malloc( INPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS * NB_INPUT_BLOCK );
	memset(h_inBuffer, 0, INPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS * NB_INPUT_BLOCK);

	//init host outBuffer size :  2*OUTPUT_BLOCK_SIZE_B * NB_SCND_STAGE_THREADS * NB_THREADS_BLOCKS
	h_outBuffer=(tKeccakLane *) malloc( 2*OUTPUT_BLOCK_SIZE_B * NB_SCND_STAGE_THREADS * NB_THREADS_BLOCKS );
	memset(h_outBuffer, 0, 2*OUTPUT_BLOCK_SIZE_B * NB_SCND_STAGE_THREADS * NB_THREADS_BLOCKS);

	//***************************
	//init h_inBuffer with values
	for(i=0;i<INPUT_BLOCK_SIZE_B/4 * NB_INPUT_BLOCK * NB_THREADS*NB_THREADS_BLOCKS;i++ )
	{h_inBuffer[i]=i;}

	
	//CPU computation *******************************
	printf("CPU_2stg speed test started \n");	
	
	t1=time(NULL);
	for(i=0;i<(IMAX/reduc);i++)
	{
		KeccakTreeCPU_2stg(h_inBuffer,h_outBuffer);

		//print_out(h_outBuffer,2* NB_SCND_STAGE_THREADS* NB_THREADS_BLOCKS);

		Keccak_top(Kstate,h_outBuffer,2* NB_SCND_STAGE_THREADS * NB_THREADS_BLOCKS);
	}
	t2=time(NULL);

	print_KS_256(Kstate);

	speed1= (INPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS * NB_INPUT_BLOCK *(IMAX/(reduc*1000.)))  / ((t2-t1) + 0.01);
	printf("CPU_2stg speed : %.2f kB/s \n\n",speed1);


	//free all buffer host and device
	free(h_inBuffer);
	free(h_outBuffer); 	
}


// GPU 2 stages 
void TestGPU_2stg()
{

	time_t t1,t2;
	double speed1;
	unsigned int i;

	tKeccakLane *h_inBuffer;// Host in buffer for data to be hashed
	tKeccakLane *h_outBuffer;// Host out buffer 

	tKeccakLane *d_inBuffer; // device in buffer
	tKeccakLane *d_outBuffer;// device out buffer 

	tKeccakLane Kstate[25]; //Keccak State for top node
	memset(Kstate, 0, 25 * sizeof(tKeccakLane));


	//init host inBuffer 
	h_inBuffer=(tKeccakLane *) malloc( INPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS * NB_INPUT_BLOCK );
	memset(h_inBuffer, 0, INPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS * NB_INPUT_BLOCK);

	//init host outBuffer	
	h_outBuffer=(tKeccakLane *) malloc( 2*OUTPUT_BLOCK_SIZE_B * NB_SCND_STAGE_THREADS * NB_THREADS_BLOCKS );
	memset(h_outBuffer, 0, 2*OUTPUT_BLOCK_SIZE_B * NB_SCND_STAGE_THREADS * NB_THREADS_BLOCKS );

	//init device inBuffer
	hipMalloc((void **)&d_inBuffer, INPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS * NB_INPUT_BLOCK );
	checkCUDAError(" hipMalloc d_inBuffer");
	hipMemset(d_inBuffer,0,INPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS * NB_INPUT_BLOCK);
	checkCUDAError(" hipMemset d_inBuffer");

	//init device outBuffer
	hipMalloc((void **)&d_outBuffer, 2*OUTPUT_BLOCK_SIZE_B * NB_SCND_STAGE_THREADS * NB_THREADS_BLOCKS );
	checkCUDAError(" hipMalloc d_outBuffer");
	hipMemset(d_outBuffer,0, 2*OUTPUT_BLOCK_SIZE_B * NB_SCND_STAGE_THREADS * NB_THREADS_BLOCKS);
	checkCUDAError(" hipMemset d_outBuffer");

	//***************************
	//init h_inBuffer with values
	for(i=0;i<INPUT_BLOCK_SIZE_B/4 * NB_INPUT_BLOCK * NB_THREADS*NB_THREADS_BLOCKS;i++ )
	{h_inBuffer[i]=i;}

	//GPU computation *******************************
	printf("GPU_2stg speed test started\n");
	
	t1=time(NULL);
	for(i=0;i<IMAX;i++)
	{
		KeccakTreeGPU_2stg(h_inBuffer,d_inBuffer,h_outBuffer,d_outBuffer);

		//print_out(h_outBuffer,2* NB_SCND_STAGE_THREADS* NB_THREADS_BLOCKS);

		Keccak_top(Kstate,h_outBuffer, 2* NB_SCND_STAGE_THREADS * NB_THREADS_BLOCKS);

	}

	t2=time(NULL);
	
	print_KS_256(Kstate);

	speed1= (INPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS * NB_INPUT_BLOCK *(IMAX/1000.))  / ((t2-t1) + 0.01);
	printf("GPU_2stg speed : %.2f kB/s \n\n",speed1);


	//free all buffer host and device
	free(h_inBuffer);
	free(h_outBuffer); 	

	hipFree(d_inBuffer);
	hipFree(d_outBuffer);

}


void TestGPU_2stg_Stream_OverlapCPU()
{

	time_t t1,t2;
	double speed1;
	int i;

	tKeccakLane *h_inBuffer=NULL;	// Host in buffer for data to be hashed
	tKeccakLane *h_outBuffer=NULL;	// Host out buffer 

	tKeccakLane *d_inBuffer; // device in buffer
	tKeccakLane *d_outBuffer;// device out buffer 

	tKeccakLane Kstate[25]; //Keccak State for top node
	memset(Kstate, 0, 25 * sizeof(tKeccakLane));


	//alloc host inBuffer WITH CudaHostAlloc 
	hipHostMalloc( (void **)&h_inBuffer, INPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS * NB_INPUT_BLOCK,
		hipHostMallocDefault);
	checkCUDAError("hipHostMalloc h_inBuffer");

	memset(h_inBuffer, 0, INPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS * NB_INPUT_BLOCK);

	//alloc host outBuffer WITH CudaHostAlloc 
	hipHostMalloc( (void **)&h_outBuffer, 2*OUTPUT_BLOCK_SIZE_B * NB_SCND_STAGE_THREADS * NB_THREADS_BLOCKS,
		hipHostMallocDefault);
	checkCUDAError("hipHostMalloc h_outBuffer");

	memset(h_outBuffer, 0, 2*OUTPUT_BLOCK_SIZE_B * NB_SCND_STAGE_THREADS * NB_THREADS_BLOCKS);

	//init device inBuffer
	hipMalloc((void **)&d_inBuffer, INPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS * NB_INPUT_BLOCK );
	checkCUDAError(" hipMalloc d_inBuffer");
	hipMemset(d_inBuffer,0,INPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS * NB_INPUT_BLOCK);
	checkCUDAError(" hipMemset d_inBuffer");

	//init device outBuffer
	hipMalloc((void **)&d_outBuffer, 2*OUTPUT_BLOCK_SIZE_B * NB_SCND_STAGE_THREADS * NB_THREADS_BLOCKS );
	checkCUDAError(" hipMalloc d_outBuffer");
	hipMemset(d_outBuffer,0, 2*OUTPUT_BLOCK_SIZE_B * NB_SCND_STAGE_THREADS * NB_THREADS_BLOCKS);
	checkCUDAError(" hipMemset d_outBuffer");

	//***************************
	//init h_inBuffer with values
	for(i=0;i<INPUT_BLOCK_SIZE_B/4 * NB_INPUT_BLOCK * NB_THREADS*NB_THREADS_BLOCKS ; i++ )
	{h_inBuffer[i]=i;}

	//GPU computation *******************************
	printf("GPU_2stg Stream OverlapCPU speed test started \n");	

	t1=time(NULL);

	//first iteration 
	KeccakTreeGPU_2stg(h_inBuffer,d_inBuffer,h_outBuffer,d_outBuffer);

	for(i=1;i<IMAX;i++)
	{
		KeccakTreeGPU_2stg_Stream_OverlapCPU(h_inBuffer,d_inBuffer,h_outBuffer,d_outBuffer,Kstate);
		//print_out(h_outBuffer,NB_THREADS*NB_THREADS_BLOCKS);

		
	}
	//last CPU computation
	Keccak_top(Kstate,h_outBuffer,2* NB_SCND_STAGE_THREADS * NB_THREADS_BLOCKS );

	t2=time(NULL);
	
	print_KS_256(Kstate);

	speed1= (INPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS * NB_INPUT_BLOCK *(IMAX/1000.))  / ((t2-t1) + 0.01);
	printf("GPU_2stg Stream OverlapCPU speed : %.2f kB/s \n\n",speed1);


	//free all buffer host and device
	hipHostFree(h_inBuffer);
	hipHostFree(h_outBuffer); 	

	hipFree(d_inBuffer);
	hipFree(d_outBuffer);

}


//***************************************
// Keccak Stream CipherMode
// Use 256 bit key and 256 bit Nonce
//***************************************
void TestGPU_SCipher()
{

	time_t t1,t2;
	double speed1;
	int i;

	tKeccakLane *h_inKeyNonce=NULL;	// Host in buffer for Key and Nonce
	tKeccakLane *h_outBuffer=NULL;	// Host out buffer 

	tKeccakLane *d_inKeyNonce; // device in buffer
	tKeccakLane *d_outBuffer; // device out buffer 


	//alloc host inBuffer WITH CudaHostAlloc 
	hipHostMalloc( (void **)&h_inKeyNonce, 2*32 ,
		hipHostMallocDefault);
	checkCUDAError("hipHostMalloc h_inKeyNonce");

	memset(h_inKeyNonce, 0, 2*32 );

	//alloc host outBuffer WITH CudaHostAlloc 
	hipHostMalloc( (void **)&h_outBuffer, SC_NB_OUTPUT_BLOCK * OUTPUT_BLOCK_SIZE_B * NB_THREADS * NB_THREADS_BLOCKS,
		hipHostMallocDefault);
	checkCUDAError("hipHostMalloc h_outBuffer");

	memset(h_outBuffer, 0, SC_NB_OUTPUT_BLOCK * OUTPUT_BLOCK_SIZE_B * NB_THREADS * NB_THREADS_BLOCKS );

	//init device inKeyNonce
	hipMalloc((void **)&d_inKeyNonce, 2*32 );
	checkCUDAError(" hipMalloc d_inKeyNonce");
	hipMemset(d_inKeyNonce,0,2*32 );
	checkCUDAError(" hipMemset d_inKeyNonce");

	//init device outBuffer
	hipMalloc((void **)&d_outBuffer, SC_NB_OUTPUT_BLOCK * OUTPUT_BLOCK_SIZE_B * NB_THREADS * NB_THREADS_BLOCKS );
	checkCUDAError(" hipMalloc d_outBuffer");
	hipMemset(d_outBuffer,0, SC_NB_OUTPUT_BLOCK * OUTPUT_BLOCK_SIZE_B * NB_THREADS * NB_THREADS_BLOCKS);
	checkCUDAError(" hipMemset d_outBuffer");

	//GPU computation *******************************
	printf("GPU SCipher  speed test started \n");
	
	t1=time(NULL);
	for(i=0;i<IMAX;i++)
	{
		KeccakSCipherGPU_Stream( h_inKeyNonce, d_inKeyNonce,
								  h_outBuffer, d_outBuffer);
	
	}

	t2=time(NULL);

	print_out(h_outBuffer,NB_THREADS*SC_NB_OUTPUT_BLOCK * OUTPUT_BLOCK_SIZE_B/4);


	speed1= (SC_NB_OUTPUT_BLOCK * OUTPUT_BLOCK_SIZE_B *  NB_THREADS*NB_THREADS_BLOCKS *(IMAX/1000.))  / ((t2-t1) + 0.01);
	printf("GPU SCipher speed : %.2f kB/s \n\n",speed1);


	//free all buffer host and device
	hipHostFree(h_inKeyNonce);
	hipHostFree(h_outBuffer); 	

	hipFree(d_inKeyNonce);
	hipFree(d_outBuffer);

}








//*******************
// Test completness (use of each word of input buffer) 
//*******************
void Test_Completness()
{

	
	int i,res,ctr;

	tKeccakLane *h_inBuffer=NULL;	// Host in buffer for data to be hashed
	tKeccakLane *h_outBuffer=NULL;	// Host out buffer 

	tKeccakLane *d_inBuffer; // device in buffer
	tKeccakLane *d_outBuffer;// device out buffer 

	tKeccakLane Ks1[25]; //Keccak State for top node
	tKeccakLane Ks2[25]; //Keccak State for top node
	memset(Ks1, 0, 25 * sizeof(tKeccakLane));
	memset(Ks2, 0, 25 * sizeof(tKeccakLane));

	
	//alloc host inBuffer WITH CudaHostAlloc 
	hipHostMalloc( (void **)&h_inBuffer, INPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS * NB_INPUT_BLOCK,
		hipHostMallocDefault);
	checkCUDAError("hipHostMalloc h_inBuffer");

	memset(h_inBuffer, 0, INPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS * NB_INPUT_BLOCK);

	//alloc host outBuffer WITH CudaHostAlloc 
	hipHostMalloc( (void **)&h_outBuffer, OUTPUT_BLOCK_SIZE_B * NB_THREADS * NB_THREADS_BLOCKS,
		hipHostMallocDefault);
	checkCUDAError("hipHostMalloc h_outBuffer");

	memset(h_outBuffer, 0, OUTPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS);

	//init device inBuffer
	hipMalloc((void **)&d_inBuffer, INPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS * NB_INPUT_BLOCK );
	checkCUDAError(" hipMalloc d_inBuffer");
	hipMemset(d_inBuffer,0,INPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS * NB_INPUT_BLOCK);
	checkCUDAError(" hipMemset d_inBuffer");

	//init device outBuffer
	hipMalloc((void **)&d_outBuffer, OUTPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS );
	checkCUDAError(" hipMalloc d_outBuffer");
	hipMemset(d_outBuffer,0, OUTPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS);
	checkCUDAError(" hipMemset d_outBuffer");

	//***************************
	//init h_inBuffer with values
	for(i=0;i<INPUT_BLOCK_SIZE_B/4 * NB_INPUT_BLOCK * NB_THREADS*NB_THREADS_BLOCKS ; i++ )
	{h_inBuffer[i]=i;}

	//***************************
	//compute the reference Hash in Ks1 

	KeccakTreeGPU_Stream(h_inBuffer,d_inBuffer,h_outBuffer,d_outBuffer);
	Keccak_top(Ks1,h_outBuffer,NB_THREADS*NB_THREADS_BLOCKS);

	res=0; ctr=0;
	printf ("Test Completness start \n");
	// Apply a change in all input words to see if hash is different
	for(i=0;i<INPUT_BLOCK_SIZE_B/4 * NB_INPUT_BLOCK * NB_THREADS*NB_THREADS_BLOCKS ; i++ )
	{
		//zeroize device buffers and host result buffer
		hipMemset(d_inBuffer,0,INPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS * NB_INPUT_BLOCK);	
		hipMemset(d_outBuffer,0, OUTPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS);
		memset(h_outBuffer, 0, OUTPUT_BLOCK_SIZE_B * NB_THREADS*NB_THREADS_BLOCKS);

		zeroize(Ks2);
		
		//change one word
		h_inBuffer[i]= h_inBuffer[i] + 3 ;

		KeccakTreeGPU_Stream(h_inBuffer,d_inBuffer,h_outBuffer,d_outBuffer);
		Keccak_top(Ks2,h_outBuffer,NB_THREADS*NB_THREADS_BLOCKS);

		if (isEqual_KS(Ks1,Ks2))
		{ printf("Change in Word : %d of input seems to have no effect \n",i); res=1;  }

		//reset old value
		h_inBuffer[i]=i;
		
		if((i% (INPUT_BLOCK_SIZE_B/4 * NB_INPUT_BLOCK)) == 0 )
			{	
				ctr++;
				printf("\r");
				printf("[ %04d / %04d ]",ctr, NB_THREADS*NB_THREADS_BLOCKS );
			}

	}
	if(res==0)
		printf ("\nTest Completness passed ! \n");


	//free all buffer host and device
	hipHostFree(h_inBuffer); hipHostFree(h_outBuffer); 	
	hipFree(d_inBuffer); hipFree(d_outBuffer);

	

}




void Print_Param(void)
{
	printf("\n");
	printf("Numbers of Threads PER BLOCK            NB_THREADS           %u \n", NB_THREADS);
	printf("Numbers of Threads Blocks               NB_THREADS_BLOCKS    %u \n", NB_THREADS_BLOCKS);
	printf("\n");
	printf("Input block size of Keccak (in Byte)    INPUT_BLOCK_SIZE_B   %u \n", INPUT_BLOCK_SIZE_B);
	printf("Output block size of Keccak (in Byte)   OUTPUT_BLOCK_SIZE_B  %u \n", OUTPUT_BLOCK_SIZE_B);
	printf("\n");
	printf("NB of input blocks in by Threads        NB_INPUT_BLOCK       %u \n", NB_INPUT_BLOCK );
	printf("Numbers of Streams                      NB_STREAMS           %u \n", NB_STREAMS );
	printf("\n");
	printf("NB of 2 stage Threads                   NB_SCND_STAGE_THREADS        %u \n", NB_SCND_STAGE_THREADS );
	printf("NB of in blocks 2 stage                 NB_INPUT_BLOCK_SNCD_STAGE    %u \n", NB_INPUT_BLOCK_SNCD_STAGE );
	printf("\n");

}


void Device_Info(void)
{
	struct hipDeviceProp_t deviceProp ;
	int device = 0;
	// Get properties and verify device 0 supports mapped memory
	hipGetDeviceProperties(&deviceProp, 0);
	checkCUDAError("hipGetDeviceProperties");
	
	printf("\n");
	// List hardware specs
	printf( "%d - name:                    %s\n" ,device ,deviceProp.name );
	printf( "%d - MultiProcessorCount:     %d \n", device , deviceProp.multiProcessorCount );
	printf( "%d - compute capability:      %d.%d\n" ,device ,deviceProp.major ,deviceProp.minor);
	printf( "%d - clockRate                %d kilohertz\n" ,device ,deviceProp.clockRate );
	printf("\n");
	printf( "%d - totalGlobalMem:          %d bytes ( %.2f Gbytes)\n" ,device ,deviceProp.totalGlobalMem , deviceProp.totalGlobalMem / (float)( 1024 * 1024 * 1024)  );
	printf( "%d - sharedMemPerBlock:       %d bytes ( %.2f Kbytes)\n" ,device ,deviceProp.sharedMemPerBlock ,deviceProp.sharedMemPerBlock / (float)1024  );
	printf( "%d - regsPerBlock:            %d\n" ,device ,deviceProp.regsPerBlock );
	printf("\n");
	printf( "%d - warpSize:                %d\n" ,device ,deviceProp.warpSize );
	printf( "%d - memPitch:                %d\n" ,device ,deviceProp.memPitch );
	printf( "%d - maxThreadsPerBlock:      %d\n" ,device ,deviceProp.maxThreadsPerBlock );
	
	/*
	printf( "%d - maxThreadsDim[0]:        %d\n" ,device ,deviceProp.maxThreadsDim[0] );
	printf( "%d - maxThreadsDim[1]:        %d\n" ,device ,deviceProp.maxThreadsDim[1] );
	printf( "%d - maxThreadsDim[2]:        %d\n" ,device ,deviceProp.maxThreadsDim[2] );
	printf( "%d - maxGridSize[0]:          %d\n" ,device ,deviceProp.maxGridSize[0] );
	printf( "%d - maxGridSize[1]:          %d\n" ,device ,deviceProp.maxGridSize[1] );
	printf( "%d - maxGridSize[2]:          %d\n" ,device ,deviceProp.maxGridSize[2] );
	printf( "%d - totalConstMem:           %d bytes ( %.2f Kbytes)\n" ,device ,deviceProp.totalConstMem ,deviceProp.totalConstMem / (float) 1024 );


	printf( "%d - textureAlignment         %d\n\n" ,device ,deviceProp.textureAlignment );
	*/

}
