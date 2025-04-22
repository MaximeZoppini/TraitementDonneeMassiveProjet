import subprocess
from wikidata_utils import build_sparql_query, run_sparql_query
import os

from multiprocessing import Process

NB_WORKERS = 2
TOTAL_IMAGES = 250

def run_container(start, end, volume_path):
    print(f"[+] Démarrage container pour images {start} à {end-1}")
    subprocess.run([
        "docker", "run", "--rm",
        "-v", f"{volume_path}:/app/images",
        "image_downloader",
        "--start", str(start),
        "--end", str(end)
    ])

def main():
    query = build_sparql_query(limit=TOTAL_IMAGES)
    results = run_sparql_query(query)
    images_per_worker = TOTAL_IMAGES // NB_WORKERS
    abs_path = os.path.abspath("images")
    os.makedirs(abs_path, exist_ok=True)

    jobs = []
    for i in range(NB_WORKERS):
        start = i * images_per_worker
        end = (i + 1) * images_per_worker
        p = Process(target=run_container, args=(start, end, abs_path))
        p.start()
        jobs.append(p)

    for job in jobs:
        job.join()

if __name__ == "__main__":
    main()
