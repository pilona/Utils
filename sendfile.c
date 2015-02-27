#include <string.h>
#include <stdlib.h>
#include <stdio.h>

#include <unistd.h>
#include <fcntl.h>

#include <sys/sendfile.h>
#include <sys/stat.h>

// TODO: GNU getopt_long and append mode

int main(int argc, char* argv[]) {
    if (argc != 3) {
        FILE* out;
        int ret;
        if (argc == 2 &&
            (!strcmp(argv[1], "-h") ||
             !strcmp(argv[1], "--help"))) {
            out = stdout;
            ret = EXIT_SUCCESS;
        } else {
            out = stderr;
            ret = EXIT_FAILURE;
        }
        fprintf(out, "usage: %s <source_file> <target_file>\n", argv[0]);
        return ret;
    }

    int in_fd = open(argv[1], O_RDONLY);
    if (in_fd == -1) {
        perror("Couldn't open source file for reading");
        return EXIT_FAILURE;
    }

    int out_fd = open(argv[2], O_WRONLY | O_CREAT | O_TRUNC, 0666);
    if (out_fd == -1) {
        perror("Couldn't open target file for writing");
        return EXIT_FAILURE;
    }

    struct stat st;
    if (fstat(in_fd, &st) == -1) {
        perror("Couldn't stat source file");
        return EXIT_FAILURE;
    }
    size_t remaining = st.st_size;
    ssize_t transfered;

    while (remaining > 0 &&
           (transfered = sendfile(out_fd, in_fd, NULL, remaining)) > 0)
        remaining -= transfered;
    if (transfered == -1) {
        perror("Couldn't transfer data between files");
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
