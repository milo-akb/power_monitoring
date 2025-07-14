#define _GNU_SOURCE
#include <pthread.h>
#include <sched.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>

//gcc -O2 -pthread load_generator.c -o load_generator
//./load_generator


#define MIN_LOAD 40
#define MAX_LOAD 50
#define CYCLE_NS 100000000L  // 100ms cycle (in nanoseconds)

void* load_on_core(void* arg) {
    int core_id = *(int*)arg;
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(core_id, &cpuset);
    pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);

    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    srand(time(NULL) + core_id);  // unique seed per thread

    while (1) {
        // Random load percent between MIN_LOAD and MAX_LOAD
        int load_percent = MIN_LOAD + rand() % (MAX_LOAD - MIN_LOAD + 1);
        long busy_ns = CYCLE_NS * load_percent / 100;
        long idle_ns = CYCLE_NS - busy_ns;

        // Busy loop for busy_ns
        struct timespec start, now;
        clock_gettime(CLOCK_MONOTONIC, &start);
        do {
            clock_gettime(CLOCK_MONOTONIC, &now);
        } while (((now.tv_sec - start.tv_sec) * 1000000000L +
                  (now.tv_nsec - start.tv_nsec)) < busy_ns);

        // Wait until next absolute time
        t.tv_nsec += CYCLE_NS;
        while (t.tv_nsec >= 1000000000L) {
            t.tv_nsec -= 1000000000L;
            t.tv_sec++;
        }
        clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &t, NULL);
    }

    return NULL;
}

int main() {
    int num_cores = sysconf(_SC_NPROCESSORS_ONLN);
    printf("Generating fluctuating CPU load (random 40–50%% every 100ms) on %d cores...\n", num_cores);

    pthread_t threads[num_cores];
    int core_ids[num_cores];

    for (int i = 0; i < num_cores; i++) {
        core_ids[i] = i;
        pthread_create(&threads[i], NULL, load_on_core, &core_ids[i]);
        usleep(10000);  // slight delay to avoid race condition on core_ids
    }

    for (int i = 0; i < num_cores; i++) {
        pthread_join(threads[i], NULL);
    }

    return 0;
}
