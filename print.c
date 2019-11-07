/* print.c */
/* This must be compiled along with LLVM output to produce an
   executable */

#include <stdio.h>
void _print_int(int val) {
    printf("%i\n", val);
}
void _print_float(double val) {
    printf("%lf\n", val);
}
