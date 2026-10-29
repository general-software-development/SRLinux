#include <unistd.h>

int main() {
    execvp("clear", (char*[]){"/usr/bin/clear", NULL});

    return 1;
}
