/*
 * DO NOT EDIT THIS FILE.
 * Automatically generated from /home/RTDNdb-man/PIW/uploads/ccl/AELM/AELM_2_2.ccl at 16:51:06 16/08/21 by astephen
 * via program ccl4rtdn version 1 SU 21331
 * for the AELM system
 * RTDN ID version:- 488000002
 * RTDN version:- 2
 * aelmPkt metadata version:- 2
 */

#ifndef _aelmPkt_H
#define _aelmPkt_H

#include <stdrtdn.h>



/**
 * AELM RTDN packet.
 */

typedef struct {
    uint32 sequenceNo;
    uint32 sampleTime;
    uint32 available[3];
    uint32 saturated[5];
    float32 RFdevHz[488];
    float32 AEfreq;
    float32 DampingRaw;
    float32 DampingNorm;
    float32 TimeDamping;
    uint32 RFdevHz_sta;
    uint32 AEfreq_sta;
    uint32 DampingRaw_sta;
    uint32 DampingNorm_sta;
    uint32 TimeDamping_sta;
    uint32 aelmPkt_488000002;
} aelmPkt;

#define RTDN_aelmPkt_PVC 488

#define RTDN_aelmPkt_ID 488000002

#define RTDN_aelmPkt_VERSION 2

#define AELM_aelmPkt_METADATA 2

#define GET_RTDN_aelmPkt_ID(p) ((p)->aelmPkt_488000002)
#define SET_RTDN_aelmPkt_ID(p) ((p)->aelmPkt_488000002 = 488000002)
#define IS_RTDN_aelmPkt_PKT(p) ((p)->aelmPkt_488000002 == 488000002)

#endif /* _aelmPkt_H */