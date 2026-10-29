#include <stdio.h>

int main() {
    execve("/usr/bin/clear", (char*[]){"/usr/bin/clear", NULL}, (char*[]){ NULL });

    return 1;
}
