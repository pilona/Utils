#include <stdio.h>
#include <stdlib.h>
#include <errno.h>

int main(int argc, char* argv[]) {
    if (argc != 2) {
        fputs("usage: errno <error number>\n", stderr);
        return EXIT_FAILURE;
    }

    char* endptr;
    char* nptr = argv[1];

    errno = strtol(nptr, &endptr, 10);
    if (!(nptr[0] != '\0' && endptr[0] == '\0')) {
        errno = EINVAL;
        perror(NULL);
        return EXIT_FAILURE;
    }

    perror(nptr);

    return EXIT_SUCCESS;
}
