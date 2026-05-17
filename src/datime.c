
#include <stdio.h>
#include <stdlib.h>
#ifdef AMIGA
#define _TIME_
#include "exec/types.h"
#include "intuition/intuition.h"

#define INTUITIONREV 1

struct IntuitionBase *IntuitionBase = NULL;

void fDATIME(int *X, int *Y) {
  static int GOTX = 0, GOTY;
  if (GOTX == 0) {
    IntuitionBase =
        (struct IntuitionBase *)OpenLibrary("intuition.library", INTUITIONREV);
    if (IntuitionBase == NULL) {
      printf("Can't open library.\n");
      exit(FALSE);
    }
    CurrentTime(&GOTX, &GOTY);
    CloseLibrary(IntuitionBase);
  }
  GOTY += 654321;
  if (GOTY >= 1000000) {
    GOTX += 1;
    GOTY -= 1000000;
  }
  *X = GOTX;
  *Y = GOTY;
}
#endif

#ifdef __MSDOS__
#define _TIME_
#include "time.h"

void fDATIME(long *X, long *Y) {
  time(X);
  time(Y);
  *Y /= 2;
  /* it would be even better if the two numbers were totally
   * unrelated, like if 'time' returned 64 bits of data */
}
#endif

#ifndef _TIME_
#if defined(_WIN32) || defined(_WIN64)
#include <time.h>
void fDATIME(long *X, long *Y) {
  time_t now = time(NULL);
  *X = (long)now;
  *Y = 0;
}
#else
#include <sys/time.h>
void fDATIME(long *X, long *Y) {
  struct timeval now;
  gettimeofday(&now, 0);
  *X = now.tv_sec;
  *Y = now.tv_usec;
}
#endif
#endif
