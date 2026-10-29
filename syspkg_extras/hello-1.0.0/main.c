#include <stdio.h>
#include <errno.h>

int main() {
    int pcode = printf("Hello, world!\n");
    if (pcode < 0) {
        return errno;
    }

    return 0;
}
