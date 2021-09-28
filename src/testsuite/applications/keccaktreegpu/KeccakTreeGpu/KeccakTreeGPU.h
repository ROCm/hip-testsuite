/*
GPU Implementation of Keccak by Guillaume Sevestre, 2010

This code is hereby put in the public domain.
It is given as is, without any guarantee.
*/

#ifndef KECCAKTREEGPU_H_INCLUDED
#define KECCAKTREEGPU_H_INCLUDED

#include "KeccakTree.h"
#include "KeccakTypes.h"

//************************
//First Tree mode
//data to be hashed is in h_inBuffer
//output chaining values hashes are copied to h_outBuffer
//************************

void KeccakTreeGPU(tKeccakLane * h_inBuffer, tKeccakLane * d_inBuffer,
					tKeccakLane * h_outBuffer, tKeccakLane * d_outBuffer);



//Overlap CPU computation of previous results with computation of present data in GPU
//Kstate is a pointer to Keccak state of final node
//h_inBuffer contains data to be hashed
//h_outBuffer contains previsous results at the call of the function, and present results when the function returns

void KeccakTreeGPU_overlapCPU(tKeccakLane * h_inBuffer, tKeccakLane * d_inBuffer,
							  tKeccakLane * h_outBuffer, tKeccakLane * d_outBuffer,
							  tKeccakLane *Kstate);

void KeccakTreeGPU_Split(tKeccakLane * h_inBuffer, tKeccakLane * d_inBuffer,
						  tKeccakLane * h_outBuffer, tKeccakLane * d_outBuffer);

void KeccakTreeGPU_Stream(tKeccakLane * h_inBuffer, tKeccakLane * d_inBuffer,
						  tKeccakLane * h_outBuffer, tKeccakLane * d_outBuffer);

void KeccakTreeGPU_Stream_OverlapCPU(tKeccakLane * h_inBuffer, tKeccakLane * d_inBuffer,
								   tKeccakLane * h_outBuffer, tKeccakLane * d_outBuffer, 
								   tKeccakLane *Kstate);

//********************
// 2nd stage Tree mode
//********************
void KeccakTreeGPU_2stg(tKeccakLane * h_inBuffer, tKeccakLane * d_inBuffer,
							 tKeccakLane * h_outBuffer, tKeccakLane * d_outBuffer);



//Streams and overlap CPU 
void KeccakTreeGPU_2stg_Stream_OverlapCPU(tKeccakLane * h_inBuffer, tKeccakLane * d_inBuffer,
								   tKeccakLane * h_outBuffer, tKeccakLane * d_outBuffer, 
								   tKeccakLane *Kstate);


//******************
// StreamCipher
//******************
//256 bits key and Nonce should be in h_inKeyNonce
//
//output streams are copied in h_outBuffer

void KeccakSCipherGPU_Stream(tKeccakLane * h_inKeyNonce, tKeccakLane * d_inKeyNonce,
								   tKeccakLane * h_outBuffer, tKeccakLane * d_outBuffer);


//error function
void  checkCUDAError(const char *msg);

#endif // KECCAKTREEGPU_H_INCLUDED
