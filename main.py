import os
import time
import threading
from multiprocessing import Process, Queue
from queue import Queue as ThreadQueue
from collections import defaultdict


def search_keywords_in_file(file_path, keywords):
    results = defaultdict(list)
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            for keyword in keywords:
                if keyword in content:
                    results[keyword].append(file_path)
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
    return results


# Threading
def process_files_threading(files, keywords):
    def worker(files, keywords, result_queue):
        for file in files:
            result_queue.put(search_keywords_in_file(file, keywords))

    threads = []
    result_queue = ThreadQueue()
    results = defaultdict(list)

    # Поділ файлів на блоки для кожного потоку
    num_threads = min(len(files), 4)
    chunk_size = len(files) // num_threads
    file_chunks = [files[i:i + chunk_size]
                   for i in range(0, len(files), chunk_size)]

    for chunk in file_chunks:
        thread = threading.Thread(
            target=worker, args=(chunk, keywords, result_queue))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    while not result_queue.empty():
        result = result_queue.get()
        for keyword, files in result.items():
            results[keyword].extend(files)

    return results


# Multiprocessing
def worker_multiprocessing(files, keywords, result_queue):
    for file in files:
        result_queue.put(search_keywords_in_file(file, keywords))


def process_files_multiprocessing(files, keywords):
    processes = []
    result_queue = Queue()
    results = defaultdict(list)

    # Поділ файлів на блоки для кожного процесу
    num_processes = min(len(files), 4)
    chunk_size = len(files) // num_processes
    file_chunks = [files[i:i + chunk_size]
                   for i in range(0, len(files), chunk_size)]

    for chunk in file_chunks:
        process = Process(target=worker_multiprocessing,
                          args=(chunk, keywords, result_queue))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    while not result_queue.empty():
        result = result_queue.get()
        for keyword, files in result.items():
            results[keyword].extend(files)

    return results


def main():
    directory = input("Enter the directory containing text files: ")
    print("Test word: one")
    keywords = input(
        "Enter the keywords to search for (comma-separated): ").split(',')
    keywords = [k.strip() for k in keywords]

    try:
        files = [os.path.join(directory, f)
                 for f in os.listdir(directory) if f.endswith('.txt')]
        if not files:
            print("No text files found in the directory.")
            return
    except Exception as e:
        print(f"Error reading directory: {e}")
        return

    # Threading
    start_time = time.time()
    threading_results = process_files_threading(files, keywords)
    threading_time = time.time() - start_time
    print(f"Threading Results: {threading_results}")
    print(f"Threading Execution Time: {threading_time:.2f} seconds")

    # Multiprocessing
    start_time = time.time()
    multiprocessing_results = process_files_multiprocessing(files, keywords)
    multiprocessing_time = time.time() - start_time
    print(f"Multiprocessing Results: {multiprocessing_results}")
    print(f"Multiprocessing Execution Time: {
          multiprocessing_time:.2f} seconds")


if __name__ == "__main__":
    main()
