import multiprocessing


def RunSchedule(schedule):
    # TODO : improve process queue
    # TODO : support subnet
    max_process = multiprocessing.cpu_count() - 1 or 1
    processes = []

    while (schedule):
        alives = []

        for p, b in processes:
            if p.is_alive():
                alives.append((p, b))
            else:
                b.terminate()

        if len(alives) >= max_process:
            continue

        next_bloc = None
        while (True):
            bloc = schedule.pop(0)
            if bloc.isTerminated() or bloc.isWorking():
                continue

            suspend = False

            for up in bloc.upstream(inScope=True):
                if up.isWaiting():
                    suspend = True
                    break

            if suspend:
                schedule.append(bloc)
                continue

            next_bloc = bloc
            break

        next_bloc.activate()
        p = multiprocessing.Process(target=next_bloc.run)
        p.daemon = True
        p.start()
        alives.append((p, next_bloc))
        processes = alives

    while (True):
        working = False
        for p, b in processes:
            if p.is_alive():
                working = True
            else:
                if not b.isTerminated():
                    b.terminate()

        if not working:
            break
