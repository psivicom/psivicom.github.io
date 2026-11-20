#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>
#include <dirent.h>
#include <dlfcn.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <fcntl.h>

#define MUTATION_DIR "mutations"
#define WAL_FILE "zulu.wal"

void log_zulu(int fd, const char* event) {
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    struct tm t;
    gmtime_r(&ts.tv_sec, &t);
    char buf[256];
    int len = snprintf(buf, sizeof(buf), "[%04d-%02d-%02dT%02d:%02d:%02d.%03ldZ] %s\n",
        t.tm_year + 1900, t.tm_mon + 1, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec, ts.tv_nsec / 1000000, event);
    write(fd, buf, len);
}

int main() {
    mkdir(MUTATION_DIR, 0755);
    int wal_fd = open(WAL_FILE, O_WRONLY | O_CREAT | O_APPEND, 0644);
    log_zulu(wal_fd, "WENDY_SOVEREIGN_BOOT");

    while (1) {
        DIR *dir = opendir(MUTATION_DIR);
        if (dir) {
            struct dirent *ent;
            while ((ent = readdir(dir)) != NULL) {
                // Volunteer LLM drops a C file
                if (strstr(ent->d_name, ".c")) {
                    char src_path[512], so_path[512];
                    snprintf(src_path, sizeof(src_path), "%s/%s", MUTATION_DIR, ent->d_name);
                    snprintf(so_path, sizeof(so_path), "%s/%s.so", MUTATION_DIR, ent->d_name);
                    
                    // Secure compilation via fork/exec (No shell injection risk)
                    pid_t pid = fork();
                    if (pid == 0) {
                        execl("/usr/bin/gcc", "gcc", "-shared", "-fPIC", "-O3", "-s", "-o", so_path, src_path, NULL);
                        exit(1);
                    }
                    
                    int status;
                    waitpid(pid, &status, 0);
                    
                    if (WIFEXITED(status) && WEXITSTATUS(status) == 0) {
                        void *handle = dlopen(so_path, RTLD_NOW);
                        if (handle) {
                            void (*cognitive_expansion)(void) = dlsym(handle, "wendy_expand");
                            if (cognitive_expansion) {
                                cognitive_expansion(); // Execute new logic live
                                log_zulu(wal_fd, "INTEGRATED_VOLUNTEER_LOGIC");
                            }
                            dlclose(handle);
                        }
                    } else {
                        log_zulu(wal_fd, "REJECTED_MALFORMED_LOGIC");
                    }
                    unlink(src_path); // Clean up source
                    unlink(so_path);  // Clean up binary
                }
            }
            closedir(dir);
        }
        usleep(1000000); // 1 second autonomous poll
    }
    return 0;
}
