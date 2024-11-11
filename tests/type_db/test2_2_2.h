
#ifndef _test2_H
#define _test2_H

#include <std_import.h>


typedef struct {
    uint32 sequenceNo;
    uint32 sampleTime;
} test2;

#define RT_test2_PVC 488

#define RT_test2_ID 488000002

#define RT_test2_VERSION 2

#define TEST2_test2_METADATA 2

#define GET_RT_test2_ID(p) ((p)->test2_488000002)
#define SET_RT_test2_ID(p) ((p)->test2_488000002 = 488000002)
#define IS_RT_test2_PKT(p) ((p)->test2_488000002 == 488000002)

#endif /* _test2_H */
