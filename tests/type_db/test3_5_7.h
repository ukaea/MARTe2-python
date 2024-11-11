#ifndef _test3_H
#define _test3_H

#include <std_import.h>


typedef struct {
    uint32 sequenceNo;
    uint32 sampleTime;
    float32 C2E_UPZE1;
    float32 C2E_UNZE1;
    float32 C2E_UPZE2;
    float32 C2E_UNZE2;
    float32 C2E_UPZE3;
    uint32 test3_416000005;
} test3;

#define RT_test3_PVC 416

#define RT_test3_ID 416000005

#define RT_test3_VERSION 5

#define TEST3_test3_METADATA 7

#define GET_RT_test3_ID(p) ((p)->test3_416000005)
#define SET_RT_test3_ID(p) ((p)->test3_416000005 = 416000005)
#define IS_RT_test3_PKT(p) ((p)->test3_416000005 == 416000005)

#endif /* _test3_H */
