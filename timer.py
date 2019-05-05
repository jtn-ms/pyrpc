# written by junying, 2019-04-30

from multiprocessing import Pool
from eth.timer import eth_timer
def task_container(cls_instance):
    return cls_instance.run_task()

def main():
    task_list = []
    task_list.append(eth_timer)
    #task_list.append(up_timer)
    #task_list.append(owt_timer)
    
    pool = Pool(processes=len(task_list))
    for task in task_list: pool.apply_async(task)
    pool.close(); pool.join()

if __name__ == "__main__":
    main()
