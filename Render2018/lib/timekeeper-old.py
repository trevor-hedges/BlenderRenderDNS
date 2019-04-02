from lib.dircheck import check_make
import time

class time_keeper():
    scripts_start = time.time()
    dir_id = 0
    while True:
        if check_make("time/" + str(dir_id)) == False:
            break
        dir_id += 1

    def __init__(self):
        self.time_start = time.time()

    def end_time(self, file_str):

        with open("time/" + str(time_keeper.dir_id) + "/" + file_str, "w") as time_file:
            time_file.write("Time interval: " + str(time.time() - self.time_start) + "\n")
            time_file.write("Recorded at: " + str(time.time() - time_keeper.scripts_start) + " after scripts started\n")
