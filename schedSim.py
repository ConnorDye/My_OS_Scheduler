import sys
import copy
# note the default algorithim is FIFO



def main():
    supported_algs = ["SRTN", "FIFO", "RR"]
    algorithm = "FIFO" 
    quantum = 1

    if (len(sys.argv) < 2 ):
        raise Exception("schedSim must be given a file.")
    elif(len(sys.argv) == 2):
        file = sys.argv[1] # The first command line argument
    elif(len(sys.argv) == 4):
        file = sys.argv[1] # The first command line argument
        #disregard quantum if its any algorithm other than RR
        if (sys.argv[2] == "-p"):
            if sys.argv[3] in supported_algs:
                algorithm = sys.argv[3]
            else:
                algorithm = "FIFO" #use if invalid algorithm is given
    elif(len(sys.argv) == 6):
        file = sys.argv[1] # The first command line argument
        if (sys.argv[2] == "-p"):
            if sys.argv[3] in supported_algs:
                algorithm = sys.argv[3]
            else:
                algorithm = "FIFO" #use if invalid algorithm is given
        if (sys.argv[4] == "-q") and (algorithm == "RR"):
            quantum = sys.argv[5]

        if (sys.argv[4] == "-p"):
            if sys.argv[5] in supported_algs:
                algorithm = sys.argv[5]
            else:
                algorithm = "FIFO" #use if invalid algorithm is given
        if (sys.argv[2] == "-q") and (algorithm == "RR"):
            quantum = sys.argv[3]


    print("Filename is: ", file, "Algorithm is: ", algorithm, "Quantum is", quantum)
    job_list = []
    with open(file, 'r') as f:
        for line in f:
            num1, num2 = map(int, line.split())
            pair = tuple([num1, num2])
            job_list.append(pair)
            # Do something with num1 and num2 here
    # print(job_list)
    if(algorithm == "FIFO"):
        FIFO(job_list)
    elif(algorithm == "SRTN"):
        # print(algorithm)
        SRTN(job_list)
    elif(algorithm == "RR"):
        quantum = int(quantum)
        RR(job_list, quantum)


def FIFO(job_list):
    # print("fifo")

    
    # print(job_list)
    scheduled_jobs = sorted(job_list, key=lambda x: x[1])

    # print(scheduled_jobs)
    
    job = 0
    current_time = 0
    for tup in scheduled_jobs:

        # wait time: execution time of previous job - arrival time of the current job
        wait_time = current_time - tup[1]
        
        # if wait time is less than 0 wait time is 0
        if wait_time < 0:
            wait_time = 0

        # turnaround time 
        turnaround_time = tup[0] + wait_time

        # current time
        current_time += tup[0]

        print("Job %3d -- Turnaround %3.2f  Wait %3.2f" % (job, turnaround_time, wait_time))
        job = job + 1

class Process:
    def __init__(self, burstTime, arrival, job_number):   
        self.arrival_time = arrival
        self.burst_time = burstTime
        self.remaining_burst_time = burstTime
        self.job_number = job_number
    def print(self):
        print("ArrivalTime: ", self.arrival_time, "BurstTime: ", self.burst_time, "RemainingBurstTime: ", self.remaining_burst_time)

def RR(job_list, quantum):
    process_list = []
    BURST_TIME = 0
    ARRIVAL_TIME = 1
    current_time = 0
    job_list = sorted(job_list, key=lambda x: x[1]) #sort by arrival time
    job_num = 0
    for x in job_list:  
        process_list.append(Process(x[BURST_TIME], x[ARRIVAL_TIME], job_num))
        job_num += 1

    done = False
    jobs_done = 0
    total_jobs_to_run = len(process_list)

    statements = {}
    while not done:
        for process in process_list:
            # if the process process has arrived and it has some burst time left to run
            if (process.arrival_time <= current_time) and (process.remaining_burst_time > 0):
                # this is where our process is scheduled
                # if the process remaining burst time is greater than the quantum we know if will run for the entire 
                # quantum so we adjust current time accordingly so it's correct for our calculations
                if process.remaining_burst_time >= quantum:
                    process.remaining_burst_time = process.remaining_burst_time - quantum 
                    current_time += quantum
                #if the remaining_burst_time is less than the quantum, we know a job is done in between the quantum time so we need to adjust our current time accordingly
                else:
                    process.remaining_burst_time = process.remaining_burst_time - quantum 
                    current_time = current_time + quantum + process.remaining_burst_time #adjust current_time by adding negative burst time as we don't remain idle we immediately schedule
                # print(current_time)
                if process.remaining_burst_time <= 0:
                    turnaround_time = current_time - process.arrival_time
                    wait_time = turnaround_time - process.burst_time
                    # print("Job %3d -- Turnaround %3.2f  Wait %3.2f" % (process.job_number, current_time - process.arrival_time,  turnaround_time - process.burst_time))
                    statement =  f"Job {process.job_number:3d} -- Turnaround {turnaround_time:3.2f}  Wait {wait_time:3.2f}"
                    statements[process.job_number] = statement
                    jobs_done += 1
                    if jobs_done == total_jobs_to_run:
                        done = True
    # Print the statements in sorted order
    sorted_statements = sorted(statements.items(), key=lambda x: x[0]) 
    for job_number, statement in sorted_statements:
        print(statement)
                    


def SRTN(job_list):
    job_list = sorted(job_list, key=lambda x: x[1]) #sort by arrival time
    REMAINING_BURST_TIME = 0
    ARRIVAL_TIME = 1
    
    queue = []
    current_scheduled = None
    current_time = 0
    
    # create a list of processes to be ran
    process_list = []
    job_num = 0
    for x in job_list:  
        process_list.append(Process(x[REMAINING_BURST_TIME], x[ARRIVAL_TIME], job_num))
        job_num += 1

    statements = {}
    while True:
        #if all of our processes are done exit
        if not process_list:
            break
         
        #if a job arrived at the current time, add it to the queue
        for process in process_list:
            if process.arrival_time == current_time:
                queue.append(process)

        shortest_remaining_burst = None
        if len(queue) > 0:
            # get process with shortest remaining burst time
            shortest_remaining_burst = min(queue, key=lambda x: x.remaining_burst_time) 
            
            #pre-empt current job if theres a shorter job
            if (current_scheduled is None) or shortest_remaining_burst.remaining_burst_time < current_scheduled.remaining_burst_time:
                current_scheduled = shortest_remaining_burst
        else: #if there's no jobs in the queue, just increment the time
            current_time += 1
            continue
        
        # print("current time is", current_time)
        # print("scheduled", current_scheduled)
        current_time += 1 # run the job for one second

        if current_scheduled.remaining_burst_time == 1: #if the job is done, remove it and set the current scheduled to 
            turnaround_time = current_time - current_scheduled.arrival_time
            wait_time = turnaround_time - current_scheduled.burst_time
            # print("Job %3d -- Turnaround %3.2f  Wait %3.2f" % (current_scheduled.job_number, turnaround_time, wait_time))
            statement = f"Job {current_scheduled.job_number:3d} -- Turnaround {turnaround_time:3.2f}  Wait {wait_time:3.2f}"
            statements[current_scheduled.job_number] = statement
            process_list.remove(current_scheduled)
            queue.remove(current_scheduled)
            current_scheduled = None
            
        else: #else modify the current burst time of the scheduled item
            current_scheduled.remaining_burst_time -= 1
    
    # Print the statements in sorted order
    sorted_statements = sorted(statements.items(), key=lambda x: x[0]) 
    for job_number, statement in sorted_statements:
        print(statement)

main()


# def SRTN_backup_copy(job_list):
#     job_list = sorted(job_list, key=lambda x: x[1]) #sort by arrival time
#     REMAINING_BURST_TIME = 0
#     ARRIVAL_TIME = 1
    
#     queue = []
#     current_scheduled = None
#     current_time = 0
#     job_number = 0
#     first_arrived = [] #to calculate wait times
#     while True:
#         #if all of our processes are done exit
#         if not job_list:
#             break
         
#         #if a job arrived at the current time, add it to the queue
#         for job in job_list:
#             if job[ARRIVAL_TIME] == current_time:
#                 queue.append(job)

#         shortest_remaining_burst = None
#         if len(queue) > 0:
#             # get process with shortest remaining burst time
#             shortest_remaining_burst = min(queue, key=lambda x: x[0]) 
            
#             #pre-empt current job if theres a shorter job
#             if (current_scheduled is None) or shortest_remaining_burst[REMAINING_BURST_TIME] < current_scheduled[REMAINING_BURST_TIME]:
#                 current_scheduled = shortest_remaining_burst
#                 first_arrived.append([current_scheduled[REMAINING_BURST_TIME], current_scheduled]) #store original burst time for wait time calculation
#         else: #if there's no jobs in the queue, just increment the time
#             current_time += 1
#             continue
        
#         # print("current time is", current_time)
#         # print("scheduled", current_scheduled)
#         current_time += 1 # run the job for one second
       
    
#         if current_scheduled[REMAINING_BURST_TIME] == 1: #if the job is done, remove it and set the current scheduled to 
#             wait_time = 0
#             turnaround_time = current_time - current_scheduled[ARRIVAL_TIME]
#             # print(first_arrived)
#             for x in first_arrived:
#                 if x[1] == current_scheduled:
#                     # print(x[1])
#                     wait_time = turnaround_time - x[0]
#                     # print(x[0])
#                     break
                    
#                     # remove_item = x
#                     # break
#             # first_arrived.remove(remove_item)
#             print("Job %3d -- Turnaround %3.2f  Wait %3.2f" % (job_number, current_time - current_scheduled[ARRIVAL_TIME], wait_time))
#             job_number = job_number + 1
#             job_list.remove(current_scheduled)
#             queue.remove(current_scheduled)
#             current_scheduled = None
#         else: #else modify the current burst time of the scheduled item
#             updated_burst_time_tuple = tuple([(current_scheduled[REMAINING_BURST_TIME] - 1), current_scheduled[ARRIVAL_TIME]]) 
#             for x in first_arrived:
#                 if x[1] == current_scheduled:
#                     x[1] = updated_burst_time_tuple
#             job_list.remove(current_scheduled)
#             queue.remove(current_scheduled)
#             queue.append(updated_burst_time_tuple)
#             job_list.append(updated_burst_time_tuple)
#             current_scheduled = updated_burst_time_tuple
        
        


