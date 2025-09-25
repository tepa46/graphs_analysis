#!/usr/bin/env python3
import os
import json

LOG_DIR = "/home/pavlusha/Documents/Spbu/graphs_analysis/logs"


def analyze_events():
    total_exec_s = 0.0
    total_cpu_s = 0.0
    total_fetch_wait_s = 0.0
    total_shuffle_write_s = 0.0
    total_shuffle_read_s = 0.0
    total_gc_s = 0.0
    total_deser_s = 0.0
    total_ser_s = 0.0
    tasks = 0

    for fname in os.listdir(LOG_DIR):
        path = os.path.join(LOG_DIR, fname)
        if not os.path.isfile(path):
            continue
        with open(path) as f:
            for line in f:
                try:
                    ev = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if ev.get("Event") != "SparkListenerTaskEnd":
                    continue

                m = ev.get("Task Metrics", {})

                exec_ms = m.get("Executor Run Time", 0)
                cpu_ns = m.get("Executor CPU Time", 0)
                gc_ms = m.get("JVM GC Time", 0)
                deser_ms = m.get("Executor Deserialize Time", 0)
                ser_ms = m.get("Result Serialization Time", 0)

                read_metrics = m.get("Shuffle Read Metrics", {})
                fetch_ms = read_metrics.get("Fetch Wait Time", 0)
                read_ms = read_metrics.get(
                    "Total Records Read", 0
                )  # just for visibility
                total_read_time_ms = read_metrics.get("Total Block Fetch Time", 0) or 0
                _ = read_ms
                write_ns = m.get("Shuffle Write Metrics", {}).get(
                    "Shuffle Write Time", 0
                )

                # Перевод в секунды сразу
                exec_s = exec_ms / 1_000
                cpu_s = cpu_ns / 1_000_000_000
                fetch_s = fetch_ms / 1_000
                write_s = write_ns / 1_000_000_000
                gc_s = gc_ms / 1_000
                deser_s = deser_ms / 1_000
                ser_s = ser_ms / 1_000
                shuffle_read_s = total_read_time_ms / 1_000

                total_exec_s += exec_s
                total_cpu_s += cpu_s
                total_fetch_wait_s += fetch_s
                total_shuffle_write_s += write_s
                total_shuffle_read_s += shuffle_read_s
                total_gc_s += gc_s
                total_deser_s += deser_s
                total_ser_s += ser_s

                tasks += 1

    if tasks == 0:
        print("Нет ни одного SparkListenerTaskEnd.")
        return

    print(f"Tasks counted: {tasks}")
    print(f"Executor run time (incl. fetch): {total_exec_s:.3f} s")
    print(f"  – CPU time:                   {total_cpu_s:.3f} s")
    print(f"  – JVM GC time:                {total_gc_s:.3f} s")
    print(f"  – Deserialize time:           {total_deser_s:.3f} s")
    print(f"  – Result serialization time:  {total_ser_s:.3f} s")
    print(f"Fetch wait time:               {total_fetch_wait_s:.3f} s")
    print(f"Shuffle read time:             {total_shuffle_read_s:.3f} s")
    print(f"Shuffle write time:            {total_shuffle_write_s:.3f} s")

    # Расчёт «чистых вычислений» и долей
    compute_only = max(total_exec_s - total_fetch_wait_s, 0.0)
    total_measured = compute_only + total_fetch_wait_s + total_shuffle_write_s

    print("\nComponent breakdown:")
    print(
        f"  Compute only:        {compute_only:.3f} s ({100 * compute_only / total_measured:.1f}%)"
    )
    print(
        f"  Fetch wait:          {total_fetch_wait_s:.3f} s ({100 * total_fetch_wait_s / total_measured:.1f}%)"
    )
    print(
        f"  Shuffle write:       {total_shuffle_write_s:.3f} s ({100 * total_shuffle_write_s / total_measured:.1f}%)"
    )
    print(f"  Sum of components:   {total_measured:.3f} s")


if __name__ == "__main__":
    analyze_events()
