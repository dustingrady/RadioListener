# Author: Dustin Grady
# Purpose: Detect signal strength for a given frequency
# Status: In development

from rtlsdr import RtlSdr
from pylab import *
import datetime
import threading


class Listener:
    def __init__(self, target_freqs={'None': 0}, debug=False):
        self.sdr = RtlSdr()
        self.sdr.sample_rate = 2.4e6  # MHz
        self.target_freqs = target_freqs
        self.debug = debug
        self.sdr.gain = 2  # Initially 4
        self.tolerance = -28  # dB

    def start_thread(self):
        for freq in self.target_freqs.values():
            thread = threading.Thread(target=self.collect_samples, kwargs=dict(tar_freq=freq))
            thread.start()
            time.sleep(0.1)

    def collect_samples(self, tar_freq):
        print('Now listening for frequencies: {}'.format(tar_freq))
        while True:
            samples = self.sdr.read_samples(256*1024)
            # self.sdr.close()

            # Use matplotlib to estimate and plot the PSD
            self.sdr.center_freq = tar_freq * 10 ** 6  # MHz
            pwr, freqs = psd(samples, NFFT=1024, Fs=self.sdr.sample_rate/1e6, Fc=tar_freq)

            # Todo: Find a way to display these outside of loop
            if self.debug:
                xlabel('Frequency (MHz)')
                ylabel('Relative power (dB)')
                show()

            amplitude_dB = 10 * np.log10(np.abs(pwr))  # Use the 'power' formula for dB (10*log10(X))
            power_dict = dict(zip(freqs, amplitude_dB))
            try:
                # if power_dict[self.sdr.center_freq/1e6] > self.tolerance:  # Prone to KeyErrors :(
                #     print('{} -- Signal detected -- {} MHz at {} dB!'.format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.sdr.center_freq/1e6, power_dict[self.sdr.center_freq/1e6]))
                if power_dict[tar_freq] > self.tolerance:  # Prone to KeyErrors :(
                    print('{} -- Signal detected -- {} MHz at {} dB!'.format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), tar_freq, power_dict[tar_freq]))

            except KeyError:
                print('Dictionary Key Error D:')


def execute():
    """
    Driver for Listener class
    """
    target_freqs = {
        'usa': 433,
        'jap': 315,
        'radio': 106.5
    }

    # Listener(target_freqs).collect_samples()
    Listener(target_freqs).start_thread()


execute()
