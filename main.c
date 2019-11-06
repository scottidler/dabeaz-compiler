#include <stdio.h>

extern int hellollvm();

int main() {
    printf("hellollvm() returned %i\n", hellollvm());
}
