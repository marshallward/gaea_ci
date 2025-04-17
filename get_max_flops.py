import shlex
import subprocess
import tarfile

perf_tar_filename = '05000101.ascii_out.tar'

perf_tar = tarfile.open(perf_tar_filename, 'r')
perf_files = [
        f for f in perf_tar.getnames()
        if f.startswith('./05000101.extra.results/perf.data.')
]
print(perf_files[:20])

metrics = {}

## testing
#pname = perf_files[0]
#pfile = perf_tar.extractfile(pname)

for pname in perf_files[:10]:
    cmd = shlex.split('perf report --stdio -i {}'.format(pname))
    proc = subprocess.run(cmd, capture_output=True, text=True)


    event = None
    for line in proc.stdout.splitlines():
        if "# Samples" in line:
            event = line.split()[-1]

        elif event and "# Event count" in line:
            count = int(line.split()[-1])

            # TODO: use defaultdict?
            try:
                metrics[event].append(count)
            except KeyError:
                metrics[event] = [count]

            event = None


print(metrics)

## CRUD loop
#for pfile in perf_files:
#
#    # Extract the file
#    # Read perf data
#    continue
