#include <errno.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>

int main(int argc, char **argv) {
    struct stat st;
    if (argc != 2) {
        fprintf(stderr, "usage: %s <path>\n", argv[0]);
        return 2;
    }

    if (stat(argv[1], &st) != 0) {
        fprintf(stderr, "path-check: %s: %s\n", argv[1], strerror(errno));
        return 1;
    }

    if (!(st.st_mode & S_IFDIR)) {
        fprintf(stderr, "path-check: %s is not a directory\n", argv[1]);
        return 1;
    }

    printf("ok: %s\n", argv[1]);
    return 0;
}
