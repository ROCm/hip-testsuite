diff -ruN HIP/samples/0_Intro/bit_extract/Makefile samples/0_Intro/bit_extract/Makefile
--- HIP/samples/0_Intro/bit_extract/Makefile	2021-07-09 10:33:24.804268020 +0530
+++ samples/0_Intro/bit_extract/Makefile	2021-07-09 10:28:19.000000000 +0530
@@ -20,17 +20,23 @@
 
 #Dependencies : [MYHIP]/bin must be in user's path.
 
-HIP_PATH?= $(wildcard /opt/rocm/hip)
 ifeq (,$(HIP_PATH))
+  HIP_PATH?= $(wildcard /opt/rocm/hip)
+  ifeq (,$(HIP_PATH))
 	HIP_PATH=../../..
+  endif
 endif
-HIP_PLATFORM=$(shell $(HIP_PATH)/bin/hipconfig --platform)
+
 HIPCC=$(HIP_PATH)/bin/hipcc
+HIP_PLATFORM=$(shell $(HIP_PATH)/bin/hipconfig --platform)
+HIP_COMPILER=$(shell $(HIP_PATH)/bin/hipconfig --compiler)
+HIP_RUNTIME=$(shell $(HIP_PATH)/bin/hipconfig --runtime)
 
 # Show how to use PLATFORM to specify different options for each compiler:
-ifeq (${HIP_PLATFORM}, nvcc)
-	HIPCC_FLAGS = -gencode=arch=compute_20,code=sm_20
-endif
+# By default, it will be built for current target
+# ifeq (${HIP_PLATFORM}, nvidia)
+#	HIPCC_FLAGS = -gencode=arch=compute_20,code=sm_20
+# endif
 
 EXE=bit_extract
 
diff -ruN HIP/samples/0_Intro/module_api/defaultDriver.cpp samples/0_Intro/module_api/defaultDriver.cpp
--- HIP/samples/0_Intro/module_api/defaultDriver.cpp	2021-07-09 10:33:24.804268020 +0530
+++ samples/0_Intro/module_api/defaultDriver.cpp	2021-07-09 10:28:19.000000000 +0530
@@ -44,10 +44,11 @@
 
     hipInit(0);
     hipDevice_t device;
+#ifdef __HIP_PLATFORM_NVIDIA__
     hipCtx_t context;
     hipDeviceGet(&device, 0);
     hipCtxCreate(&context, 0, device);
-
+#endif
     hipMalloc((void**)&Ad, SIZE);
     hipMalloc((void**)&Bd, SIZE);
 
@@ -78,10 +79,12 @@
         std::cout << "FAILED!\n";
     };
 
-    hipFree(Ad);
-    hipFree(Bd);
+    hipFree((void *)Ad);
+    hipFree((void *)Bd);
     delete[] A;
     delete[] B;
+#ifdef __HIP_PLATFORM_NVIDIA__
     hipCtxDestroy(context);
+#endif
     return 0;
 }
diff -ruN HIP/samples/0_Intro/module_api/launchKernelHcc.cpp samples/0_Intro/module_api/launchKernelHcc.cpp
--- HIP/samples/0_Intro/module_api/launchKernelHcc.cpp	2021-07-09 10:33:24.804268020 +0530
+++ samples/0_Intro/module_api/launchKernelHcc.cpp	2021-07-09 10:28:19.000000000 +0530
@@ -55,10 +55,11 @@
 
     hipInit(0);
     hipDevice_t device;
+#ifdef __HIP_PLATFORM_NVIDIA__
     hipCtx_t context;
     hipDeviceGet(&device, 0);
     hipCtxCreate(&context, 0, device);
-
+#endif
     hipMalloc((void**)&Ad, SIZE);
     hipMalloc((void**)&Bd, SIZE);
 
@@ -109,6 +110,8 @@
     hipFree(Bd);
     delete[] A;
     delete[] B;
+#ifdef __HIP_PLATFORM_NVIDIA__
     hipCtxDestroy(context);
+#endif
     return 0;
 }
diff -ruN HIP/samples/0_Intro/module_api/Makefile samples/0_Intro/module_api/Makefile
--- HIP/samples/0_Intro/module_api/Makefile	2021-07-09 10:33:24.804268020 +0530
+++ samples/0_Intro/module_api/Makefile	2021-07-09 10:28:19.000000000 +0530
@@ -18,14 +18,24 @@
 # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 # THE SOFTWARE.
 
-HIP_PATH?= $(wildcard /opt/rocm/hip)
 ifeq (,$(HIP_PATH))
-	HIP_PATH=../../..
+  HIP_PATH?= $(wildcard /opt/rocm/hip)
+  ifeq (,$(HIP_PATH))
+        HIP_PATH=../../..
+  endif
 endif
+
 HIPCC=$(HIP_PATH)/bin/hipcc
-HIP_PLATFORM=$(shell $(HIP_PATH)/bin/hipconfig --compiler)
+HIP_PLATFORM=$(shell $(HIP_PATH)/bin/hipconfig --platform)
+HIP_COMPILER=$(shell $(HIP_PATH)/bin/hipconfig --compiler)
+HIP_RUNTIME=$(shell $(HIP_PATH)/bin/hipconfig --runtime)
 
+all:
+ifeq (nvidia, $(HIP_PLATFORM))
+all: vcpy_kernel.code runKernel.hip.out defaultDriver.hip.out
+else
 all: vcpy_kernel.code runKernel.hip.out launchKernelHcc.hip.out defaultDriver.hip.out
+endif
 
 runKernel.hip.out: runKernel.cpp
 	$(HIPCC) $(HIPCC_FLAGS) $< -o $@
diff -ruN HIP/samples/0_Intro/module_api/runKernel.cpp samples/0_Intro/module_api/runKernel.cpp
--- HIP/samples/0_Intro/module_api/runKernel.cpp	2021-07-09 10:33:24.804268020 +0530
+++ samples/0_Intro/module_api/runKernel.cpp	2021-07-09 10:28:19.000000000 +0530
@@ -25,7 +25,7 @@
 #include <iostream>
 #include <fstream>
 #include <vector>
-#include <hip/hip_hcc.h>
+//#include <hip/hip_hcc.h>
 
 #define LEN 64
 #define SIZE LEN << 2
@@ -52,10 +52,11 @@
 
     hipInit(0);
     hipDevice_t device;
+#ifdef __HIP_PLATFORM_NVIDIA__
     hipCtx_t context;
     hipDeviceGet(&device, 0);
     hipCtxCreate(&context, 0, device);
-
+#endif
     hipMalloc((void**)&Ad, SIZE);
     hipMalloc((void**)&Bd, SIZE);
 
@@ -97,10 +98,12 @@
         std::cout << "FAILED!\n";
     };
 
-    hipFree(Ad);
-    hipFree(Bd);
+    hipFree((void *)Ad);
+    hipFree((void *)Bd);
     delete[] A;
     delete[] B;
+#ifdef __HIP_PLATFORM_NVIDIA__
     hipCtxDestroy(context);
+#endif
     return 0;
 }
diff -ruN HIP/samples/0_Intro/module_api_global/Makefile samples/0_Intro/module_api_global/Makefile
--- HIP/samples/0_Intro/module_api_global/Makefile	2021-07-09 10:33:24.804268020 +0530
+++ samples/0_Intro/module_api_global/Makefile	2021-07-09 10:28:19.000000000 +0530
@@ -18,12 +18,17 @@
 # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 # THE SOFTWARE.
 
-HIP_PATH?= $(wildcard /opt/rocm/hip)
 ifeq (,$(HIP_PATH))
-	HIP_PATH=../../..
+  HIP_PATH?= $(wildcard /opt/rocm/hip)
+  ifeq (,$(HIP_PATH))
+        HIP_PATH=../../..
+  endif
 endif
+
 HIPCC=$(HIP_PATH)/bin/hipcc
-HIP_PLATFORM=$(shell $(HIP_PATH)/bin/hipconfig --compiler)
+HIP_PLATFORM=$(shell $(HIP_PATH)/bin/hipconfig --platform)
+HIP_COMPILER=$(shell $(HIP_PATH)/bin/hipconfig --compiler)
+HIP_RUNTIME=$(shell $(HIP_PATH)/bin/hipconfig --runtime)
 
 all: vcpy_kernel.code runKernel.hip.out
 
diff -ruN HIP/samples/0_Intro/module_api_global/runKernel.cpp samples/0_Intro/module_api_global/runKernel.cpp
--- HIP/samples/0_Intro/module_api_global/runKernel.cpp	2021-07-09 10:33:24.804268020 +0530
+++ samples/0_Intro/module_api_global/runKernel.cpp	2021-07-09 10:28:19.000000000 +0530
@@ -25,7 +25,7 @@
 #include <iostream>
 #include <fstream>
 #include <vector>
-#include <hip/hip_ext.h>
+//#include <hip/hip_ext.h>
 
 #define LEN 64
 #define SIZE LEN * sizeof(float)
@@ -54,10 +54,11 @@
 
     hipInit(0);
     hipDevice_t device;
+#ifdef __HIP_PLATFORM_NVIDIA__
     hipCtx_t context;
     hipDeviceGet(&device, 0);
     hipCtxCreate(&context, 0, device);
-
+#endif
     hipMalloc((void**)&Ad, SIZE);
     hipMalloc((void**)&Bd, SIZE);
 
@@ -69,7 +70,7 @@
     float myDeviceGlobal_h = 42.0;
     float* deviceGlobal;
     size_t deviceGlobalSize;
-    HIP_CHECK(hipModuleGetGlobal((void**)&deviceGlobal, &deviceGlobalSize, Module, "myDeviceGlobal"));
+    HIP_CHECK(hipModuleGetGlobal((hipDeviceptr_t *)&deviceGlobal, &deviceGlobalSize, Module, "myDeviceGlobal"));
     HIP_CHECK(hipMemcpyHtoD(hipDeviceptr_t(deviceGlobal), &myDeviceGlobal_h, deviceGlobalSize));
 
 #define ARRAY_SIZE 16
@@ -77,7 +78,7 @@
     float myDeviceGlobalArray_h[ARRAY_SIZE];
     float *myDeviceGlobalArray;
     size_t myDeviceGlobalArraySize;
-    HIP_CHECK(hipModuleGetGlobal((void**)&myDeviceGlobalArray, &myDeviceGlobalArraySize, Module, "myDeviceGlobalArray"));
+    HIP_CHECK(hipModuleGetGlobal((hipDeviceptr_t *)&myDeviceGlobalArray, &myDeviceGlobalArraySize, Module, "myDeviceGlobalArray"));
     for (int i = 0; i < ARRAY_SIZE; i++) {
         myDeviceGlobalArray_h[i] = i * 1000.0f;
         HIP_CHECK(hipMemcpyHtoD(hipDeviceptr_t(myDeviceGlobalArray), &myDeviceGlobalArray_h, myDeviceGlobalArraySize));
@@ -101,7 +102,7 @@
         HIP_CHECK(hipModuleGetFunction(&Function, Module, "hello_world"));
         HIP_CHECK(hipModuleLaunchKernel(Function, 1, 1, 1, LEN, 1, 1, 0, 0, NULL, (void**)&config));
 
-        hipMemcpyDtoH(B, Bd, SIZE);
+        hipMemcpyDtoH(B, (hipDeviceptr_t)Bd, SIZE);
 
         int mismatchCount = 0;
         for (uint32_t i = 0; i < LEN; i++) {
@@ -131,7 +132,7 @@
         printf("Num Regs = %d\n",val);
         HIP_CHECK(hipModuleLaunchKernel(Function, 1, 1, 1, LEN, 1, 1, 0, 0, NULL, (void**)&config));
 
-        hipMemcpyDtoH(B, Bd, SIZE);
+        hipMemcpyDtoH(B, (hipDeviceptr_t)Bd, SIZE);
 
         int mismatchCount = 0;
         for (uint32_t i = 0; i < LEN; i++) {
@@ -156,6 +157,8 @@
     hipFree(Bd);
     delete[] A;
     delete[] B;
+#ifdef __HIP_PLATFORM_NVIDIA__
     hipCtxDestroy(context);
+#endif
     return 0;
 }
diff -ruN HIP/samples/0_Intro/square/Makefile samples/0_Intro/square/Makefile
--- HIP/samples/0_Intro/square/Makefile	2021-07-09 10:33:24.804268020 +0530
+++ samples/0_Intro/square/Makefile	2021-07-09 10:28:19.000000000 +0530
@@ -18,12 +18,17 @@
 # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 # THE SOFTWARE.
 
-HIP_PATH?= $(wildcard /opt/rocm/hip)
 ifeq (,$(HIP_PATH))
-	HIP_PATH=../../..
+  HIP_PATH?= $(wildcard /opt/rocm/hip)
+  ifeq (,$(HIP_PATH))
+        HIP_PATH=../../..
+  endif
 endif
-HIP_PLATFORM=$(shell $(HIP_PATH)/bin/hipconfig --platform)
+
 HIPCC=$(HIP_PATH)/bin/hipcc
+HIP_PLATFORM=$(shell $(HIP_PATH)/bin/hipconfig --platform)
+HIP_COMPILER=$(shell $(HIP_PATH)/bin/hipconfig --compiler)
+HIP_RUNTIME=$(shell $(HIP_PATH)/bin/hipconfig --runtime)
 
 ifeq (${HIP_PLATFORM}, nvidia)
 	SOURCES=square.cu
diff -ruN HIP/samples/0_Intro/square/README.md samples/0_Intro/square/README.md
--- HIP/samples/0_Intro/square/README.md	2021-07-09 10:33:24.804268020 +0530
+++ samples/0_Intro/square/README.md	2021-07-09 10:28:19.000000000 +0530
@@ -1,8 +1,6 @@
 # Square.md
 
-Simple test which shows how to use hipify-perl to port CUDA code to HIP.
-See related [blog](http://gpuopen.com/hip-to-be-squared-an-introductory-hip-tutorial) that explains the example.
-Now it is even simpler and requires no manual modification to the hipified source code - just hipify and compile:
+Simple test below is an example, shows how to use hipify-perl to port CUDA code to HIP:
 
 - Add hip/bin path to the PATH
 
diff -ruN HIP/samples/1_Utils/hipBusBandwidth/Makefile samples/1_Utils/hipBusBandwidth/Makefile
--- HIP/samples/1_Utils/hipBusBandwidth/Makefile	2021-07-09 10:33:24.804268020 +0530
+++ samples/1_Utils/hipBusBandwidth/Makefile	2021-07-09 10:28:19.000000000 +0530
@@ -18,11 +18,17 @@
 # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 # THE SOFTWARE.
 
-HIP_PATH?= $(wildcard /opt/rocm/hip)
 ifeq (,$(HIP_PATH))
-	HIP_PATH=../../..
+  HIP_PATH?= $(wildcard /opt/rocm/hip)
+  ifeq (,$(HIP_PATH))
+        HIP_PATH=../../..
+  endif
 endif
+
 HIPCC=$(HIP_PATH)/bin/hipcc
+HIP_PLATFORM=$(shell $(HIP_PATH)/bin/hipconfig --platform)
+HIP_COMPILER=$(shell $(HIP_PATH)/bin/hipconfig --compiler)
+HIP_RUNTIME=$(shell $(HIP_PATH)/bin/hipconfig --runtime)
 
 EXE=hipBusBandwidth
 CXXFLAGS = -O3
diff -ruN HIP/samples/1_Utils/hipCommander/Makefile samples/1_Utils/hipCommander/Makefile
--- HIP/samples/1_Utils/hipCommander/Makefile	2021-07-09 10:33:24.804268020 +0530
+++ samples/1_Utils/hipCommander/Makefile	2021-07-09 10:28:19.000000000 +0530
@@ -18,11 +18,17 @@
 # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 # THE SOFTWARE.
 
-HIP_PATH?= $(wildcard /opt/rocm/hip)
 ifeq (,$(HIP_PATH))
-	HIP_PATH=../../..
+  HIP_PATH?= $(wildcard /opt/rocm/hip)
+  ifeq (,$(HIP_PATH))
+        HIP_PATH=../../..
+  endif
 endif
+
 HIPCC=$(HIP_PATH)/bin/hipcc
+HIP_PLATFORM=$(shell $(HIP_PATH)/bin/hipconfig --platform)
+HIP_COMPILER=$(shell $(HIP_PATH)/bin/hipconfig --compiler)
+HIP_RUNTIME=$(shell $(HIP_PATH)/bin/hipconfig --runtime)
 
 EXE=hipCommander
 OPT=-O3
diff -ruN HIP/samples/1_Utils/hipDispatchLatency/hipDispatchLatency.cpp samples/1_Utils/hipDispatchLatency/hipDispatchLatency.cpp
--- HIP/samples/1_Utils/hipDispatchLatency/hipDispatchLatency.cpp	2021-07-09 10:33:24.808268042 +0530
+++ samples/1_Utils/hipDispatchLatency/hipDispatchLatency.cpp	2021-07-09 10:28:19.000000000 +0530
@@ -65,10 +65,12 @@
 
 int main() {   
     hipStream_t stream0 = 0;
+#ifdef __HIP_PLATFORM_NVIDIA__
     hipDevice_t device;
     hipDeviceGet(&device, 0);
     hipCtx_t context;     
     hipCtxCreate(&context, 0, device); 
+#endif
     hipModule_t module;
     hipFunction_t function;
     hipModuleLoad(&module, FILE_NAME);
@@ -136,6 +138,8 @@
 
     hipEventDestroy(start);
     hipEventDestroy(stop);
+#ifdef __HIP_PLATFORM_NVIDIA__
     hipCtxDestroy(context);
+#endif
 }
 
diff -ruN HIP/samples/1_Utils/hipDispatchLatency/Makefile samples/1_Utils/hipDispatchLatency/Makefile
--- HIP/samples/1_Utils/hipDispatchLatency/Makefile	2021-07-09 10:33:24.808268042 +0530
+++ samples/1_Utils/hipDispatchLatency/Makefile	2021-07-09 10:28:19.000000000 +0530
@@ -18,11 +18,17 @@
 # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 # THE SOFTWARE.
 
-HIP_PATH?= $(wildcard /opt/rocm/hip)
 ifeq (,$(HIP_PATH))
-	HIP_PATH=../../..
+  HIP_PATH?= $(wildcard /opt/rocm/hip)
+  ifeq (,$(HIP_PATH))
+        HIP_PATH=../../..
+  endif
 endif
-HIPCC=$(HIP_PATH)/bin/hipcc -std=c++11
+
+HIPCC=$(HIP_PATH)/bin/hipcc
+HIP_PLATFORM=$(shell $(HIP_PATH)/bin/hipconfig --platform)
+HIP_COMPILER=$(shell $(HIP_PATH)/bin/hipconfig --compiler)
+HIP_RUNTIME=$(shell $(HIP_PATH)/bin/hipconfig --runtime)
 
 CXXFLAGS = -O3
 
diff -ruN HIP/samples/1_Utils/hipInfo/Makefile samples/1_Utils/hipInfo/Makefile
--- HIP/samples/1_Utils/hipInfo/Makefile	2021-07-09 10:33:24.808268042 +0530
+++ samples/1_Utils/hipInfo/Makefile	2021-07-09 10:28:19.000000000 +0530
@@ -18,11 +18,17 @@
 # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 # THE SOFTWARE.
 
-HIP_PATH?= $(wildcard /opt/rocm/hip)
 ifeq (,$(HIP_PATH))
-	HIP_PATH=../../..
+  HIP_PATH?= $(wildcard /opt/rocm/hip)
+  ifeq (,$(HIP_PATH))
+        HIP_PATH=../../..
+  endif
 endif
+
 HIPCC=$(HIP_PATH)/bin/hipcc
+HIP_PLATFORM=$(shell $(HIP_PATH)/bin/hipconfig --platform)
+HIP_COMPILER=$(shell $(HIP_PATH)/bin/hipconfig --compiler)
+HIP_RUNTIME=$(shell $(HIP_PATH)/bin/hipconfig --runtime)
 
 EXE=hipInfo
 
diff -ruN HIP/samples/2_Cookbook/0_MatrixTranspose/Makefile samples/2_Cookbook/0_MatrixTranspose/Makefile
--- HIP/samples/2_Cookbook/0_MatrixTranspose/Makefile	2021-07-09 10:33:24.808268042 +0530
+++ samples/2_Cookbook/0_MatrixTranspose/Makefile	2021-07-09 10:28:19.000000000 +0530
@@ -18,12 +18,17 @@
 # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 # THE SOFTWARE.
 
-HIP_PATH?= $(wildcard /opt/rocm/hip)
 ifeq (,$(HIP_PATH))
-	HIP_PATH=../../..
+  HIP_PATH?= $(wildcard /opt/rocm/hip)
+  ifeq (,$(HIP_PATH))
+        HIP_PATH=../../..
+  endif
 endif
 
 HIPCC=$(HIP_PATH)/bin/hipcc
+HIP_PLATFORM=$(shell $(HIP_PATH)/bin/hipconfig --platform)
+HIP_COMPILER=$(shell $(HIP_PATH)/bin/hipconfig --compiler)
+HIP_RUNTIME=$(shell $(HIP_PATH)/bin/hipconfig --runtime)
 
 TARGET=hcc
 
diff -ruN HIP/samples/2_Cookbook/10_inline_asm/Makefile samples/2_Cookbook/10_inline_asm/Makefile
--- HIP/samples/2_Cookbook/10_inline_asm/Makefile	2021-07-09 10:33:24.808268042 +0530
+++ samples/2_Cookbook/10_inline_asm/Makefile	2021-07-09 10:28:19.000000000 +0530
@@ -18,12 +18,17 @@
 # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 # THE SOFTWARE.
 
-HIP_PATH?= $(wildcard /opt/rocm/hip)
 ifeq (,$(HIP_PATH))
-	HIP_PATH=../../..
+  HIP_PATH?= $(wildcard /opt/rocm/hip)
+  ifeq (,$(HIP_PATH))
+        HIP_PATH=../../..
+  endif
 endif
 
 HIPCC=$(HIP_PATH)/bin/hipcc
+HIP_PLATFORM=$(shell $(HIP_PATH)/bin/hipconfig --platform)
+HIP_COMPILER=$(shell $(HIP_PATH)/bin/hipconfig --compiler)
+HIP_RUNTIME=$(shell $(HIP_PATH)/bin/hipconfig --runtime)
 
 TARGET=hcc
 
@@ -35,7 +40,10 @@
 .PHONY: test
 
 
+all:
+ifeq ($(HIP_PLATFORM),amd)
 all: $(EXECUTABLE) test
+endif
 
 CXXFLAGS =-g
 CXX=$(HIPCC)
diff -ruN HIP/samples/2_Cookbook/11_texture_driver/Makefile samples/2_Cookbook/11_texture_driver/Makefile
--- HIP/samples/2_Cookbook/11_texture_driver/Makefile	2021-07-09 10:33:24.808268042 +0530
+++ samples/2_Cookbook/11_texture_driver/Makefile	2021-07-09 10:28:19.000000000 +0530
@@ -18,12 +18,17 @@
 # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 # THE SOFTWARE.
 
-HIP_PATH?= $(wildcard /opt/rocm/hip)
 ifeq (,$(HIP_PATH))
-	HIP_PATH=../../..
+  HIP_PATH?= $(wildcard /opt/rocm/hip)
+  ifeq (,$(HIP_PATH))
+        HIP_PATH=../../..
+  endif
 endif
+
 HIPCC=$(HIP_PATH)/bin/hipcc
-HIP_PLATFORM=$(shell $(HIP_PATH)/bin/hipconfig --compiler)
+HIP_PLATFORM=$(shell $(HIP_PATH)/bin/hipconfig --platform)
+HIP_COMPILER=$(shell $(HIP_PATH)/bin/hipconfig --compiler)
+HIP_RUNTIME=$(shell $(HIP_PATH)/bin/hipconfig --runtime)
 
 all: tex2dKernel.code texture2dDrv.out
 
diff -ruN HIP/samples/2_Cookbook/11_texture_driver/texture2dDrv.cpp samples/2_Cookbook/11_texture_driver/texture2dDrv.cpp
--- HIP/samples/2_Cookbook/11_texture_driver/texture2dDrv.cpp	2021-07-09 10:33:24.808268042 +0530
+++ samples/2_Cookbook/11_texture_driver/texture2dDrv.cpp	2021-07-09 10:28:19.000000000 +0530
@@ -26,7 +26,31 @@
 #include <vector>
 
 #define fileName "tex2dKernel.code"
+#ifdef __HIP_PLATFORM_NVIDIA__
+#define CTX_CREATE() \
+  hipCtx_t context;\
+  initHipCtx(&context);
+#define CTX_DESTROY() HIP_CHECK(hipCtxDestroy(context));
+#define ARRAY_DESTROY(array) HIP_CHECK(hipArrayDestroy(array));
+#define HIP_TEX_REFERENCE hipTexRef
+#define HIP_ARRAY hiparray
+/**
+ * Internal Function
+ */
+void initHipCtx(hipCtx_t *pcontext) {
+  hipInit(0);
+  hipDevice_t device;
+  hipDeviceGet(&device, 0);
+  hipCtxCreate(pcontext, 0, device);
+}
 
+#else
+#define CTX_CREATE()
+#define CTX_DESTROY()
+#define ARRAY_DESTROY(array) HIP_CHECK(hipFreeArray(array));
+#define HIP_TEX_REFERENCE textureReference*
+#define HIP_ARRAY hipArray*
+#endif
 bool testResult = true;
 
 #define HIP_CHECK(cmd)                                                                             \
@@ -50,10 +74,11 @@
             hData[i * width + j] = i * width + j;
         }
     }
+    CTX_CREATE();
     hipModule_t Module;
     HIP_CHECK(hipModuleLoad(&Module, fileName));
 
-    hipArray* array;
+    HIP_ARRAY array;
     HIP_ARRAY_DESCRIPTOR desc;
     desc.Format = HIP_AD_FORMAT_FLOAT;
     desc.NumChannels = 1;
@@ -63,23 +88,38 @@
 
     hip_Memcpy2D copyParam;
     memset(&copyParam, 0, sizeof(copyParam));
-    copyParam.dstMemoryType = hipMemoryTypeArray;
+#ifdef __HIP_PLATFORM_NVCC__
+    copyParam.dstMemoryType = CU_MEMORYTYPE_ARRAY;
+    copyParam.srcMemoryType = CU_MEMORYTYPE_HOST;
     copyParam.dstArray = array;
+#else
+    copyParam.dstMemoryType = hipMemoryTypeArray;
     copyParam.srcMemoryType = hipMemoryTypeHost;
+    copyParam.dstArray = array;
+#endif
     copyParam.srcHost = hData;
     copyParam.srcPitch = width * sizeof(float);
     copyParam.WidthInBytes = copyParam.srcPitch;
     copyParam.Height = height;
     HIP_CHECK(hipMemcpyParam2D(&copyParam));
-
-    textureReference* texref;
-    HIP_CHECK(hipModuleGetTexRef(&texref, Module, "tex"));
-    HIP_CHECK(hipTexRefSetAddressMode(texref, 0, hipAddressModeWrap));
-    HIP_CHECK(hipTexRefSetAddressMode(texref, 1, hipAddressModeWrap));
-    HIP_CHECK(hipTexRefSetFilterMode(texref, hipFilterModePoint));
-    HIP_CHECK(hipTexRefSetFlags(texref, 0));
-    HIP_CHECK(hipTexRefSetFormat(texref, HIP_AD_FORMAT_FLOAT, 1));
-    HIP_CHECK(hipTexRefSetArray(texref, array, HIP_TRSA_OVERRIDE_FORMAT));
+    HIP_TEX_REFERENCE texref;
+#ifdef __HIP_PLATFORM_NVIDIA__
+  HIP_CHECK(hipModuleGetTexRef(&texref, Module, "tex"));
+  HIP_CHECK(hipTexRefSetAddressMode(texref, 0, CU_TR_ADDRESS_MODE_WRAP));
+  HIP_CHECK(hipTexRefSetAddressMode(texref, 1, CU_TR_ADDRESS_MODE_WRAP));
+  HIP_CHECK(hipTexRefSetFilterMode(texref, HIP_TR_FILTER_MODE_POINT));
+  HIP_CHECK(hipTexRefSetFlags(texref, 0));
+  HIP_CHECK(hipTexRefSetFormat(texref, HIP_AD_FORMAT_FLOAT, 1));
+  HIP_CHECK(hipTexRefSetArray(texref, array, CU_TRSA_OVERRIDE_FORMAT));
+#else
+  HIP_CHECK(hipModuleGetTexRef(&texref, Module, "tex"));
+  HIP_CHECK(hipTexRefSetAddressMode(texref, 0, hipAddressModeWrap));
+  HIP_CHECK(hipTexRefSetAddressMode(texref, 1, hipAddressModeWrap));
+  HIP_CHECK(hipTexRefSetFilterMode(texref, hipFilterModePoint));
+  HIP_CHECK(hipTexRefSetFlags(texref, 0));
+  HIP_CHECK(hipTexRefSetFormat(texref, HIP_AD_FORMAT_FLOAT, 1));
+  HIP_CHECK(hipTexRefSetArray(texref, array, HIP_TRSA_OVERRIDE_FORMAT));
+#endif
 
     float* dData = NULL;
     HIP_CHECK(hipMalloc((void**)&dData, size));
@@ -121,9 +161,9 @@
             }
         }
     }
-    HIP_CHECK(hipUnbindTexture(texref));
     HIP_CHECK(hipFree(dData));
-    HIP_CHECK(hipFreeArray(array));
+    ARRAY_DESTROY(array)
+    CTX_DESTROY();
     return testResult;
 }
 
diff -ruN HIP/samples/2_Cookbook/13_occupancy/Makefile samples/2_Cookbook/13_occupancy/Makefile
--- HIP/samples/2_Cookbook/13_occupancy/Makefile	2021-07-09 10:33:24.808268042 +0530
+++ samples/2_Cookbook/13_occupancy/Makefile	2021-07-09 10:28:19.000000000 +0530
@@ -18,11 +18,17 @@
 # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 # THE SOFTWARE.
 
-HIP_PATH?= $(wildcard /opt/rocm/hip)
 ifeq (,$(HIP_PATH))
-	HIP_PATH=../../..
+  HIP_PATH?= $(wildcard /opt/rocm/hip)
+  ifeq (,$(HIP_PATH))
+        HIP_PATH=../../..
+  endif
 endif
+
 HIPCC=$(HIP_PATH)/bin/hipcc
+HIP_PLATFORM=$(shell $(HIP_PATH)/bin/hipconfig --platform)
+HIP_COMPILER=$(shell $(HIP_PATH)/bin/hipconfig --compiler)
+HIP_RUNTIME=$(shell $(HIP_PATH)/bin/hipconfig --runtime)
 
 EXE=./occupancy
 
diff -ruN HIP/samples/2_Cookbook/14_gpu_arch/gpuarch.cpp samples/2_Cookbook/14_gpu_arch/gpuarch.cpp
--- HIP/samples/2_Cookbook/14_gpu_arch/gpuarch.cpp	2021-07-09 10:33:24.808268042 +0530
+++ samples/2_Cookbook/14_gpu_arch/gpuarch.cpp	2021-07-09 10:28:19.000000000 +0530
@@ -90,9 +90,9 @@
     }
   }
   if (flag == false) {
-    std::cout << "Error: Kernel is supported for gfx908 architecture\n";
+    std::cout << "info: Kernel is supported only for gfx908 architecture\n";
   } else {
     std::cout << "success\n";
   }
   return 0;
-}
\ No newline at end of file
+}
diff -ruN HIP/samples/2_Cookbook/14_gpu_arch/Makefile samples/2_Cookbook/14_gpu_arch/Makefile
--- HIP/samples/2_Cookbook/14_gpu_arch/Makefile	2021-07-09 10:33:24.808268042 +0530
+++ samples/2_Cookbook/14_gpu_arch/Makefile	2021-07-09 10:28:19.000000000 +0530
@@ -18,17 +18,29 @@
 # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 # THE SOFTWARE.
 
-HIP_PATH?= $(wildcard /opt/rocm/hip)
 ifeq (,$(HIP_PATH))
-	HIP_PATH=../../..
+  HIP_PATH?= $(wildcard /opt/rocm/hip)
+  ifeq (,$(HIP_PATH))
+        HIP_PATH=../../..
+  endif
 endif
+
 HIPCC=$(HIP_PATH)/bin/hipcc
+HIP_PLATFORM=$(shell $(HIP_PATH)/bin/hipconfig --platform)
+HIP_COMPILER=$(shell $(HIP_PATH)/bin/hipconfig --compiler)
+HIP_RUNTIME=$(shell $(HIP_PATH)/bin/hipconfig --runtime)
 
 EXE=./gpuarch
 
 .PHONY: test
 
+all:
+ifneq (amd, $(HIP_PLATFORM))
+all:
+  $(info Not supported for platform $(HIP_PLATFORM)!)
+else
 all: test
+endif
 
 $(EXE): gpuarch.cpp
 	$(HIPCC) $^ -o $@
diff -ruN HIP/samples/2_Cookbook/15_static_library/device_functions/CMakeLists.txt samples/2_Cookbook/15_static_library/device_functions/CMakeLists.txt
--- HIP/samples/2_Cookbook/15_static_library/device_functions/CMakeLists.txt	1970-01-01 05:30:00.000000000 +0530
+++ samples/2_Cookbook/15_static_library/device_functions/CMakeLists.txt	2021-07-09 10:28:19.000000000 +0530
@@ -0,0 +1,36 @@
+project(static_lib)
+
+cmake_minimum_required(VERSION 3.10)
+
+# Search for rocm in common locations
+list(APPEND CMAKE_PREFIX_PATH /opt/rocm/hip /opt/rocm)
+
+# Find hip
+find_package(hip REQUIRED)
+
+# Set compiler and linker
+set(CMAKE_CXX_COMPILER ${HIP_HIPCC_EXECUTABLE})
+set(CMAKE_CXX_LINKER   ${HIP_HIPCC_EXECUTABLE})
+set(CMAKE_BUILD_TYPE Release)
+
+# Turn static library generation ON
+option(BUILD_SHARED_LIBS "Build as a shared library" OFF)
+
+set(CPP_SOURCES hipDevice.cpp)
+
+# Generate static lib libHipDevice.a
+add_library(HipDevice STATIC ${CPP_SOURCES})
+
+target_compile_options(HipDevice PRIVATE -fgpu-rdc)
+target_link_libraries(HipDevice PRIVATE -fgpu-rdc)
+target_include_directories(HipDevice PRIVATE /opt/rocm/hsa/include)
+
+# Create test executable that uses libHipDevice.a
+set(TEST_SOURCES ${CMAKE_SOURCE_DIR}/hipMain2.cpp)
+
+add_executable(test_device_static ${TEST_SOURCES})
+add_dependencies(test_device_static HipDevice)
+target_compile_options(test_device_static PRIVATE -fgpu-rdc)
+target_link_libraries(test_device_static PRIVATE HipDevice)
+target_link_libraries(test_device_static PRIVATE -fgpu-rdc hip::host)
+
diff -ruN HIP/samples/2_Cookbook/15_static_library/device_functions/hipDevice.cpp samples/2_Cookbook/15_static_library/device_functions/hipDevice.cpp
--- HIP/samples/2_Cookbook/15_static_library/device_functions/hipDevice.cpp	1970-01-01 05:30:00.000000000 +0530
+++ samples/2_Cookbook/15_static_library/device_functions/hipDevice.cpp	2021-07-09 10:28:19.000000000 +0530
@@ -0,0 +1,28 @@
+/*
+ * Copyright (c) 2020-present Advanced Micro Devices, Inc. All rights reserved.
+ *
+ * Permission is hereby granted, free of charge, to any person obtaining a copy
+ * of this software and associated documentation files (the "Software"), to deal
+ * in the Software without restriction, including without limitation the rights
+ * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
+ * copies of the Software, and to permit persons to whom the Software is
+ * furnished to do so, subject to the following conditions:
+ *
+ * The above copyright notice and this permission notice shall be included in
+ * all copies or substantial portions of the Software.
+ *
+ * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
+ * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
+ * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
+ * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
+ * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
+ * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
+ * THE SOFTWARE.
+ * */
+
+#include <hip/hip_runtime.h>
+
+__device__ int square_me(int A) {
+  return A*A;
+}
+
diff -ruN HIP/samples/2_Cookbook/15_static_library/device_functions/hipMain2.cpp samples/2_Cookbook/15_static_library/device_functions/hipMain2.cpp
--- HIP/samples/2_Cookbook/15_static_library/device_functions/hipMain2.cpp	1970-01-01 05:30:00.000000000 +0530
+++ samples/2_Cookbook/15_static_library/device_functions/hipMain2.cpp	2021-07-09 10:28:19.000000000 +0530
@@ -0,0 +1,69 @@
+/*
+ * Copyright (c) 2020-present Advanced Micro Devices, Inc. All rights reserved.
+ *
+ * Permission is hereby granted, free of charge, to any person obtaining a copy
+ * of this software and associated documentation files (the "Software"), to deal
+ * in the Software without restriction, including without limitation the rights
+ * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
+ * copies of the Software, and to permit persons to whom the Software is
+ * furnished to do so, subject to the following conditions:
+ *
+ * The above copyright notice and this permission notice shall be included in
+ * all copies or substantial portions of the Software.
+ *
+ * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
+ * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
+ * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
+ * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
+ * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
+ * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
+ * THE SOFTWARE.
+ * */
+
+#include <hip/hip_runtime.h>
+#include <hip/hip_runtime_api.h>
+#include <iostream>
+
+#define HIP_ASSERT(status) assert(status == hipSuccess)
+#define LEN 512
+
+extern __device__ int square_me(int);
+
+__global__ void square_and_save(int* A, int* B) {
+    int tid = threadIdx.x + blockIdx.x * blockDim.x;
+    B[tid] = square_me(A[tid]);
+}
+
+void run_test2() {
+    int *A_h, *B_h, *A_d, *B_d;
+    A_h = new int[LEN];
+    B_h = new int[LEN];
+    for (unsigned i = 0; i < LEN; i++) {
+        A_h[i] = i;
+        B_h[i] = 0;
+    }
+    size_t valbytes = LEN*sizeof(int);
+
+    HIP_ASSERT(hipMalloc((void**)&A_d, valbytes));
+    HIP_ASSERT(hipMalloc((void**)&B_d, valbytes));
+
+    HIP_ASSERT(hipMemcpy(A_d, A_h, valbytes, hipMemcpyHostToDevice));
+    hipLaunchKernelGGL(square_and_save, dim3(LEN/64), dim3(64),
+                       0, 0, A_d, B_d);
+    HIP_ASSERT(hipMemcpy(B_h, B_d, valbytes, hipMemcpyDeviceToHost));
+
+    for (unsigned i = 0; i < LEN; i++) {
+        assert(A_h[i]*A_h[i] == B_h[i]);
+    }
+
+    HIP_ASSERT(hipFree(A_d));
+    HIP_ASSERT(hipFree(B_d));
+    free(A_h);
+    free(B_h);
+    std::cout << "Test Passed!\n";
+}
+
+int main(){
+  // Run test that generates static lib with ar
+  run_test2();
+}
diff -ruN HIP/samples/2_Cookbook/15_static_library/device_functions/Makefile samples/2_Cookbook/15_static_library/device_functions/Makefile
--- HIP/samples/2_Cookbook/15_static_library/device_functions/Makefile	1970-01-01 05:30:00.000000000 +0530
+++ samples/2_Cookbook/15_static_library/device_functions/Makefile	2021-07-09 10:28:19.000000000 +0530
@@ -0,0 +1,41 @@
+HIP_PATH = $(wildcard /opt/rocm/hip)
+ifeq (,$(HIP_PATH))
+      HIP_PATH=../../../../build
+endif
+
+
+HIPCC=$(HIP_PATH)/bin/hipcc
+HIP_PLATFORM=$(shell $(HIP_PATH)/bin/hipconfig --platform)
+HIP_COMPILER=$(shell $(HIP_PATH)/bin/hipconfig --compiler)
+HIP_RUNTIME=$(shell $(HIP_PATH)/bin/hipconfig --runtime)
+
+.PHONY: test
+
+all:
+ifneq (amd, $(HIP_PLATFORM))
+all:
+  $(info Not supported for platform $(HIP_PLATFORM)!)
+else
+all: $(RDC_EXE) test
+endif
+
+STATIC_LIB_SRC=hipDevice.cpp
+STATIC_LIB=./libHipDevice.a
+STATIC_MAIN_SRC=hipMain2.cpp
+RDC_EXE=./test_device_static.out
+
+$(STATIC_LIB):
+	$(HIPCC) $(STATIC_LIB_SRC) -c -fgpu-rdc -fPIC -o hipDevice.o
+	ar rcsD $@ hipDevice.o
+
+# Compiles hipMain2 with hipcc and links with libHipDevice.a which contains device function.
+$(RDC_EXE): $(STATIC_LIB)
+	$(HIPCC) $(STATIC_LIB) $(STATIC_MAIN_SRC) -fgpu-rdc -o $@
+
+test: $(RDC_EXE)
+	$(RDC_EXE)
+
+clean:
+	rm -f $(RDC_EXE)
+	rm -f $(STATIC_LIB)
+	rm -f *.o
diff -ruN HIP/samples/2_Cookbook/15_static_library/host_functions/CMakeLists.txt samples/2_Cookbook/15_static_library/host_functions/CMakeLists.txt
--- HIP/samples/2_Cookbook/15_static_library/host_functions/CMakeLists.txt	1970-01-01 05:30:00.000000000 +0530
+++ samples/2_Cookbook/15_static_library/host_functions/CMakeLists.txt	2021-07-09 10:28:19.000000000 +0530
@@ -0,0 +1,39 @@
+project(static_lib)
+
+cmake_minimum_required(VERSION 3.10)
+
+# Search for rocm in common locations
+list(APPEND CMAKE_PREFIX_PATH /opt/rocm/hip /opt/rocm)
+
+# Find hip
+find_package(hip REQUIRED)
+
+# Set compiler and linker
+set(CMAKE_CXX_COMPILER ${HIP_HIPCC_EXECUTABLE})
+set(CMAKE_CXX_LINKER   ${HIP_HIPCC_EXECUTABLE})
+set(CMAKE_AR           ${HIP_HIPCC_EXECUTABLE})
+set(CMAKE_BUILD_TYPE Release)
+
+# Turn static library generation ON
+option(BUILD_SHARED_LIBS "Build as a shared library" OFF)
+
+set(CPP_SOURCES hipOptLibrary.cpp)
+
+# Generate static lib libHipOptLibrary.a.
+add_library(HipOptLibrary STATIC ${CPP_SOURCES})
+
+# Set-up the correct flags to generate the static library.
+target_link_libraries(HipOptLibrary PRIVATE --emit-static-lib)
+target_include_directories(HipOptLibrary PRIVATE /opt/rocm/hsa/include)
+get_property(link_libraries TARGET HipOptLibrary PROPERTY LINK_LIBRARIES)
+string (REPLACE ";" " " LINK_PROPS "${link_libraries}")
+set(CMAKE_CXX_ARCHIVE_CREATE "<CMAKE_AR> -o <TARGET> ${LINK_PROPS} <LINK_FLAGS> <OBJECTS>")
+
+# Create test executable that uses libHipOptLibrary.a
+set(TEST_SOURCES ${CMAKE_SOURCE_DIR}/hipMain1.cpp)
+
+add_executable(test_opt_static ${TEST_SOURCES})
+add_dependencies(test_opt_static HipOptLibrary)
+target_link_libraries(test_opt_static PRIVATE -lHipOptLibrary -L${CMAKE_BINARY_DIR})
+target_link_libraries(test_opt_static PRIVATE amdhip64 amd_comgr hsa-runtime64::hsa-runtime64)
+
diff -ruN HIP/samples/2_Cookbook/15_static_library/host_functions/hipMain1.cpp samples/2_Cookbook/15_static_library/host_functions/hipMain1.cpp
--- HIP/samples/2_Cookbook/15_static_library/host_functions/hipMain1.cpp	1970-01-01 05:30:00.000000000 +0530
+++ samples/2_Cookbook/15_static_library/host_functions/hipMain1.cpp	2021-07-09 10:28:19.000000000 +0530
@@ -0,0 +1,28 @@
+/*
+ * Copyright (c) 2020-present Advanced Micro Devices, Inc. All rights reserved.
+ *
+ * Permission is hereby granted, free of charge, to any person obtaining a copy
+ * of this software and associated documentation files (the "Software"), to deal
+ * in the Software without restriction, including without limitation the rights
+ * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
+ * copies of the Software, and to permit persons to whom the Software is
+ * furnished to do so, subject to the following conditions:
+ *
+ * The above copyright notice and this permission notice shall be included in
+ * all copies or substantial portions of the Software.
+ *
+ * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
+ * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
+ * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
+ * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
+ * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
+ * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
+ * THE SOFTWARE.
+ * */
+
+extern void run_test1();
+
+int main(){
+  // Run test that generates static lib with -emit-static-lib
+  run_test1();
+}
diff -ruN HIP/samples/2_Cookbook/15_static_library/host_functions/hipOptLibrary.cpp samples/2_Cookbook/15_static_library/host_functions/hipOptLibrary.cpp
--- HIP/samples/2_Cookbook/15_static_library/host_functions/hipOptLibrary.cpp	1970-01-01 05:30:00.000000000 +0530
+++ samples/2_Cookbook/15_static_library/host_functions/hipOptLibrary.cpp	2021-07-09 10:28:19.000000000 +0530
@@ -0,0 +1,62 @@
+/*
+ * Copyright (c) 2020-present Advanced Micro Devices, Inc. All rights reserved.
+ *
+ * Permission is hereby granted, free of charge, to any person obtaining a copy
+ * of this software and associated documentation files (the "Software"), to deal
+ * in the Software without restriction, including without limitation the rights
+ * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
+ * copies of the Software, and to permit persons to whom the Software is
+ * furnished to do so, subject to the following conditions:
+ *
+ * The above copyright notice and this permission notice shall be included in
+ * all copies or substantial portions of the Software.
+ *
+ * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
+ * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
+ * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
+ * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
+ * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
+ * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
+ * THE SOFTWARE.
+ * */
+
+#include <hip/hip_runtime.h>
+#include <hip/hip_runtime_api.h>
+#include <iostream>
+
+#define HIP_ASSERT(status) assert(status == hipSuccess)
+#define LEN 512
+
+__global__ void copy(uint32_t* A, uint32_t* B) {
+    size_t tid = threadIdx.x + blockIdx.x * blockDim.x;
+    B[tid] = A[tid];
+}
+
+void run_test1() {
+    uint32_t *A_h, *B_h, *A_d, *B_d;
+    size_t valbytes = LEN * sizeof(uint32_t);
+
+    A_h = (uint32_t*)malloc(valbytes);
+    B_h = (uint32_t*)malloc(valbytes);
+    for (uint32_t i = 0; i < LEN; i++) {
+        A_h[i] = i;
+        B_h[i] = 0;
+    }
+
+    HIP_ASSERT(hipMalloc((void**)&A_d, valbytes));
+    HIP_ASSERT(hipMalloc((void**)&B_d, valbytes));
+
+    HIP_ASSERT(hipMemcpy(A_d, A_h, valbytes, hipMemcpyHostToDevice));
+    hipLaunchKernelGGL(copy, dim3(LEN/64), dim3(64), 0, 0, A_d, B_d);
+    HIP_ASSERT(hipMemcpy(B_h, B_d, valbytes, hipMemcpyDeviceToHost));
+
+    for (uint32_t i = 0; i < LEN; i++) {
+        assert(A_h[i] == B_h[i]);
+    }
+
+    HIP_ASSERT(hipFree(A_d));
+    HIP_ASSERT(hipFree(B_d));
+    free(A_h);
+    free(B_h);
+    std::cout << "Test Passed!\n";
+}
diff -ruN HIP/samples/2_Cookbook/15_static_library/host_functions/Makefile samples/2_Cookbook/15_static_library/host_functions/Makefile
--- HIP/samples/2_Cookbook/15_static_library/host_functions/Makefile	1970-01-01 05:30:00.000000000 +0530
+++ samples/2_Cookbook/15_static_library/host_functions/Makefile	2021-07-09 10:28:19.000000000 +0530
@@ -0,0 +1,49 @@
+HIP_PATH = $(wildcard /opt/rocm/hip)
+ifeq (,$(HIP_PATH))
+     HIP_PATH=../../../../build
+endif
+
+
+HIPCC=$(HIP_PATH)/bin/hipcc
+GXX=g++
+
+EMIT_STATIC_LIB_SRC=hipOptLibrary.cpp
+EMIT_STATIC_LIB=./libHipOptLibrary.a
+EMIT_STATIC_MAIN_SRC=hipMain1.cpp
+HIPCC_EXE=./test_emit_static_hipcc_linker.out
+HOST_EXE=./test_emit_static_host_linker.out
+HIP_PLATFORM=$(shell $(HIP_PATH)/bin/hipconfig --platform)
+HIP_COMPILER=$(shell $(HIP_PATH)/bin/hipconfig --compiler)
+HIP_RUNTIME=$(shell $(HIP_PATH)/bin/hipconfig --runtime)
+
+
+.PHONY: test
+
+all:
+ifneq (amd, $(HIP_PLATFORM))
+all:
+  $(info Not supported for platform $(HIP_PLATFORM)!)
+else
+all: $(HIPCC_EXE) $(HOST_EXE) test
+endif
+
+$(EMIT_STATIC_LIB):
+	$(HIPCC) $(EMIT_STATIC_LIB_SRC) --emit-static-lib -fPIC -o $@
+
+# Compiles hipMain1 with hipcc and links with libHipOptLibrary.a which contains host function.
+$(HIPCC_EXE): $(EMIT_STATIC_LIB)
+	$(HIPCC) $(EMIT_STATIC_MAIN_SRC) -L. -lHipOptLibrary -o $@
+
+# Compiles hipMain1 with g++ and links with libHipOptLibrary.a which contains host function.
+$(HOST_EXE): $(EMIT_STATIC_LIB)
+	$(GXX) $(EMIT_STATIC_MAIN_SRC) -L. -lHipOptLibrary -L$(HIP_PATH)/lib -lamdhip64 -Wl,-rpath=$(HIP_PATH)/lib -o $@
+
+test: $(HIPCC_EXE) $(HOST_EXE)
+	$(HIPCC_EXE)
+	$(HOST_EXE)
+
+clean:
+	rm -f $(HIPCC_EXE)
+	rm -f $(HOST_EXE)
+	rm -f $(EMIT_STATIC_LIB)
+	rm -f *.o
diff -ruN HIP/samples/2_Cookbook/15_static_library/README.md samples/2_Cookbook/15_static_library/README.md
--- HIP/samples/2_Cookbook/15_static_library/README.md	1970-01-01 05:30:00.000000000 +0530
+++ samples/2_Cookbook/15_static_library/README.md	2021-07-09 10:28:19.000000000 +0530
@@ -0,0 +1,175 @@
+# Emitting Static Library
+
+This sample shows how to generate a static library for a simple HIP application. We will evaluate two types of static libraries: the first type exports host functions in a static library generated with --emit-static-lib and is compatible with host linkers, and second type exports device functions in a static library made with system ar.
+
+Please refer to the hip_programming_guide for limitations.
+
+## Static libraries with host functions
+
+### Source files
+The static library source files may contain host functions and kernel `__global__` and `__device__` functions. Here is an example (please refer to the directory host_functions).
+
+hipOptLibrary.cpp:
+```
+#define HIP_ASSERT(status) assert(status == hipSuccess)
+#define LEN 512
+
+__global__ void copy(uint32_t* A, uint32_t* B) {
+    size_t tid = threadIdx.x + blockIdx.x * blockDim.x;
+    B[tid] = A[tid];
+}
+
+void run_test1() {
+    uint32_t *A_h, *B_h, *A_d, *B_d;
+    size_t valbytes = LEN * sizeof(uint32_t);
+
+    A_h = (uint32_t*)malloc(valbytes);
+    B_h = (uint32_t*)malloc(valbytes);
+    for (uint32_t i = 0; i < LEN; i++) {
+        A_h[i] = i;
+        B_h[i] = 0;
+    }
+
+    HIP_ASSERT(hipMalloc((void**)&A_d, valbytes));
+    HIP_ASSERT(hipMalloc((void**)&B_d, valbytes));
+
+    HIP_ASSERT(hipMemcpy(A_d, A_h, valbytes, hipMemcpyHostToDevice));
+    hipLaunchKernelGGL(copy, dim3(LEN/64), dim3(64), 0, 0, A_d, B_d);
+    HIP_ASSERT(hipMemcpy(B_h, B_d, valbytes, hipMemcpyDeviceToHost));
+
+    for (uint32_t i = 0; i < LEN; i++) {
+        assert(A_h[i] == B_h[i]);
+    }
+
+    HIP_ASSERT(hipFree(A_d));
+    HIP_ASSERT(hipFree(B_d));
+    free(A_h);
+    free(B_h);
+    std::cout << "Test Passed!\n";
+}
+```
+
+The above source file can be compiled into a static library, libHipOptLibrary.a, using the --emit-static-lib flag, like so:
+```
+hipcc hipOptLibrary.cpp --emit-static-lib -fPIC -o libHipOptLibrary.a
+```
+
+### Main source files
+The main() program source file may link with the above static library using either hipcc or a host compiler (such as g++). A simple source file that calls the host function inside libHipOptLibrary.a:
+
+hipMain1.cpp:
+```
+extern void run_test1();
+
+int main(){
+  run_test1();
+}
+```
+
+To link to the static library:
+
+Using hipcc:
+```
+hipcc hipMain1.cpp -L. -lHipOptLibrary -o test_emit_static_hipcc_linker.out
+```
+Using g++:
+```
+g++ hipMain1.cpp -L. -lHipOptLibrary -L/opt/rocm/hip/lib -lamdhip64 -o test_emit_static_host_linker.out
+```
+
+## Static libraries with device functions
+
+### Source files
+The static library source files which contain only `__device__` functions need to be created using ar. Here is an example (please refer to the directory device_functions).
+
+hipDevice.cpp:
+```
+#include <hip/hip_runtime.h>
+
+__device__ int square_me(int A) {
+  return A*A;
+}
+```
+
+The above source file may be compiled into a static library, libHipDevice.a, by first compiling into a relocatable object, and then placed in an archive using ar:
+```
+hipcc hipDevice.cpp -c -fgpu-rdc -fPIC -o hipDevice.o
+ar rcsD libHipDevice.a hipDevice.o
+```
+
+### Main source files
+The main() program source file can link with the static library using hipcc. A simple source file that calls the device function inside libHipDevice.a:
+
+hipMain2.cpp:
+```
+#include <hip/hip_runtime.h>
+#include <hip/hip_runtime_api.h>
+#include <iostream>
+
+#define HIP_ASSERT(status) assert(status == hipSuccess)
+#define LEN 512
+
+extern __device__ int square_me(int);
+
+__global__ void square_and_save(int* A, int* B) {
+    int tid = threadIdx.x + blockIdx.x * blockDim.x;
+    B[tid] = square_me(A[tid]);
+}
+
+void run_test2() {
+    int *A_h, *B_h, *A_d, *B_d;
+    A_h = new int[LEN];
+    B_h = new int[LEN];
+    for (unsigned i = 0; i < LEN; i++) {
+        A_h[i] = i;
+        B_h[i] = 0;
+    }
+    size_t valbytes = LEN*sizeof(int);
+
+    HIP_ASSERT(hipMalloc((void**)&A_d, valbytes));
+    HIP_ASSERT(hipMalloc((void**)&B_d, valbytes));
+
+    HIP_ASSERT(hipMemcpy(A_d, A_h, valbytes, hipMemcpyHostToDevice));
+    hipLaunchKernelGGL(square_and_save, dim3(LEN/64), dim3(64),
+                       0, 0, A_d, B_d);
+    HIP_ASSERT(hipMemcpy(B_h, B_d, valbytes, hipMemcpyDeviceToHost));
+
+    for (unsigned i = 0; i < LEN; i++) {
+        assert(A_h[i]*A_h[i] == B_h[i]);
+    }
+
+    HIP_ASSERT(hipFree(A_d));
+    HIP_ASSERT(hipFree(B_d));
+    free(A_h);
+    free(B_h);
+    std::cout << "Test Passed!\n";
+}
+
+int main(){
+  // Run test that generates static lib with ar
+  run_test2();
+}
+```
+
+To link to the static library:
+```
+hipcc libHipDevice.a hipMain2.cpp -fgpu-rdc -o test_device_static_hipcc.out
+```
+
+##  How to build and run this sample:
+Use the make command to build the static libraries, link with it, and execute it.
+- Change directory to either host or device functions folder.
+- To build the static library and link the main executable, use `make all`.
+- To execute, run the generated executable `./test_*.out`.
+
+Alternatively, use these CMake commands.
+```
+cd device_functions
+mkdir -p build
+cd build
+cmake ..
+make
+./test_*.out
+```
+
+## For More Infomation, please refer to the HIP FAQ.
diff -ruN HIP/samples/2_Cookbook/16_assembly_to_executable/Makefile samples/2_Cookbook/16_assembly_to_executable/Makefile
--- HIP/samples/2_Cookbook/16_assembly_to_executable/Makefile	2021-07-09 10:33:24.808268042 +0530
+++ samples/2_Cookbook/16_assembly_to_executable/Makefile	2021-07-09 10:28:19.000000000 +0530
@@ -18,11 +18,17 @@
 # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 # THE SOFTWARE.
 
-HIP_PATH?= $(wildcard /opt/rocm/hip)
 ifeq (,$(HIP_PATH))
-	HIP_PATH=../../..
+  HIP_PATH?= $(wildcard /opt/rocm/hip)
+  ifeq (,$(HIP_PATH))
+        HIP_PATH=../../..
+  endif
 endif
 
+HIP_PLATFORM=$(shell $(HIP_PATH)/bin/hipconfig --platform)
+HIP_COMPILER=$(shell $(HIP_PATH)/bin/hipconfig --compiler)
+HIP_RUNTIME=$(shell $(HIP_PATH)/bin/hipconfig --runtime)
+
 HIPCC=$(HIP_PATH)/bin/hipcc
 CLANG=$(HIP_PATH)/../llvm/bin/clang
 LLVM_MC=$(HIP_PATH)/../llvm/bin/llvm-mc
@@ -44,7 +50,13 @@
 
 .PHONY: test
 
+all:
+ifneq (amd, $(HIP_PLATFORM))
+all:
+  $(info Not supported for platform $(HIP_PLATFORM)!)
+else
 all: src_to_asm asm_to_exec
+endif
 
 src_to_asm:
 	$(HIPCC) -c -S --cuda-host-only -target x86_64-linux-gnu -o $(SQ_HOST_ASM) $(SRCS)
diff -ruN HIP/samples/2_Cookbook/17_llvm_ir_to_executable/Makefile samples/2_Cookbook/17_llvm_ir_to_executable/Makefile
--- HIP/samples/2_Cookbook/17_llvm_ir_to_executable/Makefile	2021-07-09 10:33:24.808268042 +0530
+++ samples/2_Cookbook/17_llvm_ir_to_executable/Makefile	2021-07-09 10:28:19.000000000 +0530
@@ -18,11 +18,17 @@
 # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 # THE SOFTWARE.
 
-HIP_PATH?= $(wildcard /opt/rocm/hip)
 ifeq (,$(HIP_PATH))
-	HIP_PATH=../../..
+  HIP_PATH?= $(wildcard /opt/rocm/hip)
+  ifeq (,$(HIP_PATH))
+        HIP_PATH=../../..
+  endif
 endif
 
+HIP_PLATFORM=$(shell $(HIP_PATH)/bin/hipconfig --platform)
+HIP_COMPILER=$(shell $(HIP_PATH)/bin/hipconfig --compiler)
+HIP_RUNTIME=$(shell $(HIP_PATH)/bin/hipconfig --runtime)
+
 HIPCC=$(HIP_PATH)/bin/hipcc
 CLANG=$(HIP_PATH)/../llvm/bin/clang
 LLVM_MC=$(HIP_PATH)/../llvm/bin/llvm-mc
@@ -47,7 +53,13 @@
 
 .PHONY: test
 
+all:
+ifneq (amd, $(HIP_PLATFORM))
+all:
+  $(info Not supported for platform $(HIP_PLATFORM)!)
+else
 all: src_to_ir bc_to_ll ll_to_bc ir_to_exec
+endif
 
 src_to_ir:
 	$(HIPCC) -c -emit-llvm --cuda-host-only -target x86_64-linux-gnu -o $(SQ_HOST_BC) $(SRCS)
diff -ruN HIP/samples/2_Cookbook/1_hipEvent/Makefile samples/2_Cookbook/1_hipEvent/Makefile
--- HIP/samples/2_Cookbook/1_hipEvent/Makefile	2021-07-09 10:33:24.808268042 +0530
+++ samples/2_Cookbook/1_hipEvent/Makefile	2021-07-09 10:28:19.000000000 +0530
@@ -18,12 +18,17 @@
 # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 # THE SOFTWARE.
 
-HIP_PATH?= $(wildcard /opt/rocm/hip)
 ifeq (,$(HIP_PATH))
-	HIP_PATH=../../..
+  HIP_PATH?= $(wildcard /opt/rocm/hip)
+  ifeq (,$(HIP_PATH))
+        HIP_PATH=../../..
+  endif
 endif
 
 HIPCC=$(HIP_PATH)/bin/hipcc
+HIP_PLATFORM=$(shell $(HIP_PATH)/bin/hipconfig --platform)
+HIP_COMPILER=$(shell $(HIP_PATH)/bin/hipconfig --compiler)
+HIP_RUNTIME=$(shell $(HIP_PATH)/bin/hipconfig --runtime)
 
 TARGET=hcc
 
diff -ruN HIP/samples/2_Cookbook/3_shared_memory/Makefile samples/2_Cookbook/3_shared_memory/Makefile
--- HIP/samples/2_Cookbook/3_shared_memory/Makefile	2021-07-09 10:33:24.808268042 +0530
+++ samples/2_Cookbook/3_shared_memory/Makefile	2021-07-09 10:28:19.000000000 +0530
@@ -18,12 +18,17 @@
 # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 # THE SOFTWARE.
 
-HIP_PATH?= $(wildcard /opt/rocm/hip)
 ifeq (,$(HIP_PATH))
-	HIP_PATH=../../..
+  HIP_PATH?= $(wildcard /opt/rocm/hip)
+  ifeq (,$(HIP_PATH))
+        HIP_PATH=../../..
+  endif
 endif
 
 HIPCC=$(HIP_PATH)/bin/hipcc
+HIP_PLATFORM=$(shell $(HIP_PATH)/bin/hipconfig --platform)
+HIP_COMPILER=$(shell $(HIP_PATH)/bin/hipconfig --compiler)
+HIP_RUNTIME=$(shell $(HIP_PATH)/bin/hipconfig --runtime)
 
 TARGET=hcc
 
diff -ruN HIP/samples/2_Cookbook/4_shfl/Makefile samples/2_Cookbook/4_shfl/Makefile
--- HIP/samples/2_Cookbook/4_shfl/Makefile	2021-07-09 10:33:24.808268042 +0530
+++ samples/2_Cookbook/4_shfl/Makefile	2021-07-09 10:28:19.000000000 +0530
@@ -18,17 +18,22 @@
 # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 # THE SOFTWARE.
 
-HIP_PATH?= $(wildcard /opt/rocm/hip)
 ifeq (,$(HIP_PATH))
-	HIP_PATH=../../..
+  HIP_PATH?= $(wildcard /opt/rocm/hip)
+  ifeq (,$(HIP_PATH))
+        HIP_PATH=../../..
+  endif
 endif
 
+HIPCC=$(HIP_PATH)/bin/hipcc
+HIP_PLATFORM=$(shell $(HIP_PATH)/bin/hipconfig --platform)
+HIP_COMPILER=$(shell $(HIP_PATH)/bin/hipconfig --compiler)
+HIP_RUNTIME=$(shell $(HIP_PATH)/bin/hipconfig --runtime)
+
 ifeq (gfx701, $(findstring gfx701,$(HCC_AMDGPU_TARGET)))
 	$(error gfx701 is not a supported device for this sample)
 endif
 
-HIPCC=$(HIP_PATH)/bin/hipcc
-
 TARGET=hcc
 
 SOURCES = shfl.cpp
diff -ruN HIP/samples/2_Cookbook/5_2dshfl/Makefile samples/2_Cookbook/5_2dshfl/Makefile
--- HIP/samples/2_Cookbook/5_2dshfl/Makefile	2021-07-09 10:33:24.808268042 +0530
+++ samples/2_Cookbook/5_2dshfl/Makefile	2021-07-09 10:28:19.000000000 +0530
@@ -18,17 +18,22 @@
 # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 # THE SOFTWARE.
 
-HIP_PATH?= $(wildcard /opt/rocm/hip)
 ifeq (,$(HIP_PATH))
-	HIP_PATH=../../..
+  HIP_PATH?= $(wildcard /opt/rocm/hip)
+  ifeq (,$(HIP_PATH))
+        HIP_PATH=../../..
+  endif
 endif
 
+HIPCC=$(HIP_PATH)/bin/hipcc
+HIP_PLATFORM=$(shell $(HIP_PATH)/bin/hipconfig --platform)
+HIP_COMPILER=$(shell $(HIP_PATH)/bin/hipconfig --compiler)
+HIP_RUNTIME=$(shell $(HIP_PATH)/bin/hipconfig --runtime)
+
 ifeq (gfx701, $(findstring gfx701,$(HCC_AMDGPU_TARGET)))
 	$(error gfx701 is not a supported device for this sample)
 endif
 
-HIPCC=$(HIP_PATH)/bin/hipcc
-
 TARGET=hcc
 
 SOURCES = 2dshfl.cpp
diff -ruN HIP/samples/2_Cookbook/6_dynamic_shared/Makefile samples/2_Cookbook/6_dynamic_shared/Makefile
--- HIP/samples/2_Cookbook/6_dynamic_shared/Makefile	2021-07-09 10:33:24.808268042 +0530
+++ samples/2_Cookbook/6_dynamic_shared/Makefile	2021-07-09 10:28:19.000000000 +0530
@@ -18,12 +18,17 @@
 # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 # THE SOFTWARE.
 
-HIP_PATH?= $(wildcard /opt/rocm/hip)
 ifeq (,$(HIP_PATH))
-	HIP_PATH=../../..
+  HIP_PATH?= $(wildcard /opt/rocm/hip)
+  ifeq (,$(HIP_PATH))
+        HIP_PATH=../../..
+  endif
 endif
 
 HIPCC=$(HIP_PATH)/bin/hipcc
+HIP_PLATFORM=$(shell $(HIP_PATH)/bin/hipconfig --platform)
+HIP_COMPILER=$(shell $(HIP_PATH)/bin/hipconfig --compiler)
+HIP_RUNTIME=$(shell $(HIP_PATH)/bin/hipconfig --runtime)
 
 TARGET=hcc
 
diff -ruN HIP/samples/2_Cookbook/7_streams/Makefile samples/2_Cookbook/7_streams/Makefile
--- HIP/samples/2_Cookbook/7_streams/Makefile	2021-07-09 10:33:24.808268042 +0530
+++ samples/2_Cookbook/7_streams/Makefile	2021-07-09 10:28:19.000000000 +0530
@@ -18,12 +18,17 @@
 # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 # THE SOFTWARE.
 
-HIP_PATH?= $(wildcard /opt/rocm/hip)
 ifeq (,$(HIP_PATH))
-	HIP_PATH=../../..
+  HIP_PATH?= $(wildcard /opt/rocm/hip)
+  ifeq (,$(HIP_PATH))
+        HIP_PATH=../../..
+  endif
 endif
 
 HIPCC=$(HIP_PATH)/bin/hipcc
+HIP_PLATFORM=$(shell $(HIP_PATH)/bin/hipconfig --platform)
+HIP_COMPILER=$(shell $(HIP_PATH)/bin/hipconfig --compiler)
+HIP_RUNTIME=$(shell $(HIP_PATH)/bin/hipconfig --runtime)
 
 TARGET=hcc
 
diff -ruN HIP/samples/2_Cookbook/8_peer2peer/Makefile samples/2_Cookbook/8_peer2peer/Makefile
--- HIP/samples/2_Cookbook/8_peer2peer/Makefile	2021-07-09 10:33:24.808268042 +0530
+++ samples/2_Cookbook/8_peer2peer/Makefile	2021-07-09 10:28:19.000000000 +0530
@@ -18,12 +18,17 @@
 # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 # THE SOFTWARE.
 
-HIP_PATH?= $(wildcard /opt/rocm/hip)
 ifeq (,$(HIP_PATH))
-	HIP_PATH=../../..
+  HIP_PATH?= $(wildcard /opt/rocm/hip)
+  ifeq (,$(HIP_PATH))
+        HIP_PATH=../../..
+  endif
 endif
 
 HIPCC=$(HIP_PATH)/bin/hipcc
+HIP_PLATFORM=$(shell $(HIP_PATH)/bin/hipconfig --platform)
+HIP_COMPILER=$(shell $(HIP_PATH)/bin/hipconfig --compiler)
+HIP_RUNTIME=$(shell $(HIP_PATH)/bin/hipconfig --runtime)
 
 TARGET=hcc
 
diff -ruN HIP/samples/2_Cookbook/9_unroll/Makefile samples/2_Cookbook/9_unroll/Makefile
--- HIP/samples/2_Cookbook/9_unroll/Makefile	2021-07-09 10:33:24.808268042 +0530
+++ samples/2_Cookbook/9_unroll/Makefile	2021-07-09 10:28:19.000000000 +0530
@@ -18,17 +18,22 @@
 # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 # THE SOFTWARE.
 
-HIP_PATH?= $(wildcard /opt/rocm/hip)
 ifeq (,$(HIP_PATH))
-	HIP_PATH=../../..
+  HIP_PATH?= $(wildcard /opt/rocm/hip)
+  ifeq (,$(HIP_PATH))
+        HIP_PATH=../../..
+  endif
 endif
 
+HIPCC=$(HIP_PATH)/bin/hipcc
+HIP_PLATFORM=$(shell $(HIP_PATH)/bin/hipconfig --platform)
+HIP_COMPILER=$(shell $(HIP_PATH)/bin/hipconfig --compiler)
+HIP_RUNTIME=$(shell $(HIP_PATH)/bin/hipconfig --runtime)
+
 ifeq (gfx701, $(findstring gfx701,$(HCC_AMDGPU_TARGET)))
 	$(error gfx701 is not a supported device for this sample)
 endif
 
-HIPCC=$(HIP_PATH)/bin/hipcc
-
 TARGET=hcc
 
 SOURCES = unroll.cpp
