import serial
import threading
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO

class Arduino(threading.Thread):
    times = []
    values = []
    datafile = 'data.csv'

    def __init__(self):
        super(Arduino, self).__init__()
        self.stop_event = threading.Event()
        self.lock1 = threading.Lock()
        self.lock2 = threading.Lock()

    def stop(self):
        self.stop_event.set()
    def run(self):
        self.ser= serial.Serial("COM4", 9600)
        time.sleep(1)
        self.ser.write(b"3")
        self.times = []
        self.values = []
        stime = time.time()
        while not self.stop_event.is_set():
            with self.lock1:
                line = self.ser.readline()
            lined = line.decode().strip()
            val= float(lined.split(',')[1])
            with self.lock2:
                self.times.append(time.time() -stime)
                self.values.append(val)
        self.stop_cy()
        self.ser.close()
        df= pd.DataFrame({'times': self.times, 'values': self.values})
        df.to_csv(self.datafile)

    def cycle(self):
        print('cycle')
        with self.lock1:
            self.ser.write(b"1")

    def reset(self):
        with self.lock1:
            self.ser.write(b"2")

    def stop_cy(self):
        with self.lock1:
            self.ser.write(b"3")

    def get_frame(self):
        with self.lock2:
            plt.plot(self.times, self.values)
        buf = BytesIO()
        plt.savefig(buf, format='jpeg', bbox_inches='tight')
        frame = buf.getvalue()
        buf.close()
        plt.close()
        return frame

    @staticmethod
    def plot_data():
        try:
            df = pd.read_csv(Arduino.datafile)
            plt.plot(df['times'], df['values'])
            buf = BytesIO()
            plt.savefig(buf, format='svg', bbox_inches='tight')
            frame = buf.getvalue()
            buf.close()
            plt.close()
            return frame
        except:
            return None
