 import threading
import time
def finish():
    print threading.currentThread().getName(), 'Lanzado'
    time.sleep(2)
    print threading.currentThread().getName(), 'Deteniendo'
def start():
    print threading.currentThread().getName(), 'Lanzado'
    print threading.currentThread().getName(), 'Deteniendo'
t = threading.Thread(target=finish, name='Finish')
w = threading.Thread(target=start, name='Start')
t.start()
w.start()
