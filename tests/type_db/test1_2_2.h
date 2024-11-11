
#ifndef _test1_H
#define _test1_H

#include <std_import.h>


typedef struct {
    uint32 sequenceNo;
    uint32 sampleTime;
    uint32 available;
    uint32 saturated;
    float32 devHz;
    float32 freq;
    float32 DampingRaw;
    float32 DampingNorm;
    float32 TimeDamping;
    uint32 devHz_sta;
    uint32 freq_sta;
    uint32 DampingRaw_sta;
    uint32 DampingNorm_sta;
    uint32 TimeDamping_sta;
    uint32 test1Pkt_488000002;
} test1;

#define RT_test1_PVC 488

#define RT_test1_ID 488000002

#define RT_test1_VERSION 2

#define TEST1_test1_METADATA 2

#define GET_RT_test1_ID(p) ((p)->test1_488000002)
#define SET_RT_test1_ID(p) ((p)->test1_488000002 = 488000002)
#define IS_RT_test1_PKT(p) ((p)->test1_488000002 == 488000002)

#endif /* _test1_H */
