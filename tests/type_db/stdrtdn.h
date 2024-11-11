/*
 * Generic include file for auto generated RTDN packet definitions
 *
 * $Log: stdrtdn.h,v $
 * Revision 1.3  2011/01/31 10:59:32  agood
 * Added common rtpsStatus BitField definitions.
 *
 * Revision 1.2  2011/01/28 10:58:01  agood
 * Added BitField type and multiple include protection.
 *
 * Revision 1.1  2010/10/04 13:13:56  agood
 * Initial revision
 *
 */

#ifndef __stdrtdn_h__
#define __stdrtdn_h__

#ifndef __vxworks__
#ifndef __UINT32__
#define __UINT32__
#ifdef _WIN32
typedef unsigned __int32 UINT32;
#else
#include <sys/types.h>
#ifdef __linux__
typedef u_int32_t UINT32;
#elif defined(__sun__)
typedef uint32_t UINT32;
#endif /* A UNIX */
#endif /* _WIN32 */
#endif /* __UINT32__ */
#endif /* __vxworks__ */

typedef UINT32 BitField;

/*
 * Common RTPS BitField flags that occupy the first 16 bits of rtpsStatus.
 */
#define RTPS_STAT_UNDEFINED  0x00 /* System considered to be not operational */
#define RTPS_STAT_NORMAL     0x01 /* System is in normal running mode */
#define RTPS_STAT_CONTROLLED 0x02 /* System running RTPS requested command */
#define RTPS_STAT_UNABLE     0x04 /* System is unable to run RTPS command */
#define RTPS_STAT_BLIND      0x08 /* System is not receiving RTPS messages */
#define RTPS_STAT_BAD        0x10 /* System is not operational */

#endif /* __stdrtdn_h__ */
