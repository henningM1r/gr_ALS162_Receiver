# gr_ALS162_Receiver
![Pipeline](https://github.com/henningM1r/gr_ALS162_Receiver/actions/workflows/docker-ci.yml/badge.svg)

This is a basic ALS162 time signal receiver for GNURadio, containing:
1. signal demodulation and detection of the ALS162 signal with an SDR using GNURadio (and Python modules)
2. a simple live decoder of received bits provided by the GNURadio ALS162 receiver
3. and additional tools for testing the receiver (especially, if no SDR hardware is available):
+ a simulated ALS162 transmitter
+ a simulated ALS162 channel (AWGN)

The __French time signal ALS162__ (ALS = Allouis transmitter, 162 = frequency: 162 kHz) was also formerly known as TéléDiffusion de France (TDF):
+ https://en.wikipedia.org/wiki/ALS162_time_signal


### Overview
The __flowgraph__ is provided in the `examples` folder:
+ `ALS162_Transmitter.grc`
    + only for simulation
+ `ALS162_Channel.grc`
    + only for simulation
+ `ALS162_Receiver_ExtDetection.grc`
    + for SDR reception and for simulation, incl. position symbols

Supplementary tools are provided in the `python` folder:
+ `DecodeALS162.py` decodes the received bits from a specified ZMQ server upon receiving them. It shows the current time, date, weekday, etc. at each new minute.


### Requirements
The ALS162 receiver was tested with:
+ gnuradio & GNURadio Companion 3.10.1.1 (Linux)
+ Radioconda 2023.02.24 & gnuradio & GNURadio Companion 3.10.5.1 (Windows)
+ Python 3.10.6
    + PyQt5 5.15.7
    + pyzmq 23.1.0
    + gnuradio-osmosdr 0.2.0
+ An SDR receiver capable of receiving in the range of at least 1 kHz - 1 MHz, e.g. an _Airspy Discovery HF+_ is configured and used for this project.
+ An antenna that provides a sufficiently clear ALS162 signal, e.g. a simple _YouLoop_ loop antenna was used for this project. Indoor reception should probably be possible if you are close enough (<1000 km) to the ALS162 transmitter in Allouis, France. You should mount the antenna close to a window or outside.
+ The user might also need some antenna cables and adapters to connect the SDR with the antenna.
+ This project has been successfully tested in:
    + Ubuntu 22.04.2 LTS (recommended)
    + Windows 11


### Instructions/Setup

#### Simulation
+ Open all 3 flowcharts (ALS162_Transmitter.grc, ALS162_Channel.grc, ALS162_Receiver.grc) in GNURadio Companion.
+ Generate the python files with the "Generate the flowgraph"-button.
+ Open 4 separate terminals (e.g.: T1, T2, T3, T4).
    + Change to your cloned repository in all 4 terminals.
+ T1: Go to ```/examples/ALS162_Transmitter/```
+ Run transmitter with: `python3 ALS162_Transmitter.py`
    + It should be run in the 1st step.
    + A GUI should appear.
    + The terminal should provide additional information continuously.
+ T2: Go to ```/examples/ALS162_Channel/```
+ Run Channel with: `python3 ALS162_Channel.py`
    + It should be run in the 2nd step.
    + A GUI should appear.
        + You can enable/disable the fading effect with the push button
            * you can adjust slower and faster fading with _fading_freq_
        + You can enable/disable the interference effect  with the push button
            * you can adjust the gain of interference with _interference_gain_
            * you can adjust the number of occurrences of interference signals with _impulse_thres_
    + you can adjust noise with _noise_gain_
+ T3: Go to ```/examples/ALS162_Receiver/```
+ Run Receiver with: `python3 ALS162_Receiver_ExtDetection.py`
    + It should be run in the 3rd step.
    + A GUI should appear.
        + for further adjustments see "Signal REception with SDR"
+ T4: (compare above) go to ```/examples/ALS162_Receiver/```
+ Run the decoder with: `python3 DecodeALS162.py`
    + It should be run in the 4th step.
    + The terminal T4 should provide received bits continuously, and a time & date message each minute.
    + NOTE: Decoding the very first received minute might fail as some initial bits are lost. Decoding subsequent minutes should work fine.


#### Signal Reception with SDR
+ Set up your SDR with your computer.
+ Ensure that the raw ALS162 signal reception at 162.0 kHz is good enough, e.g. using gqrx or another signal analysis tool.
+ To start the ALS162 receiver, open the flowchart in `/examples/ALS162_Receiver/ALS162_Receiver_ExtDetection.grc` with GNURadio Companion.
    + Press `run` button.
    + First, deactivate the following auxiliary signals in the plot for now (Derivative, +2, +1, 0, -1, -2), and keep the remaining signals (Phase, Symbols, avg. Phase).
    + Wait a few seconds until the Phase signal in the _Phase Drift Compensation_ plot roughly aligns at 0 between the values -1 and 1. If the transient phase of the control loop is still too erratic, reduce the _shift step_ slider slightly (and increase it again later on).
    + reactivate the auxiliary signal _Derivative_ and set the _diff_gain_ slider values so that the amplitudes of _Derivative"_ are roughly at +/-2000 and +/-4000, respectively.
    + Only adjust the sliders for the _thresholds_, if really needed. You should rather avoid to change them.
    + After sufficient parameter adjustment, the GNURadio Companion debug console should show a debug message each second with either '0' or '1' or '2' (for a new minute). And the plot should indicate these symbols with tags, given _symbols_ is activated.
    + Optionally,
        + you can adjust zoom the signal amplitude of the plot with _zoom_.
        + you can investigate the results of the _threshold values_ on the derivative of the phase signal by activating +2,+1, 0,-1,-2, respectively.

+ Next, open a terminal or Powershell.
    + Change to your cloned repository.
    + Run the DecodeALS162 script with ```python3 ./python/DecodeALS162.py```.
    + The terminal should show the received bits together with a sequence of indices.
    + after approximately 2 minutes, DecodeALS162 should be synchronized with the transmitter. It should provide the current time, date, etc. each minute.
    + NOTE: sometimes a bit can not be decoded correctly, e.g. due to interference or noise or a weak signal. Then the current frame of the minute is corrupted and will attempt to re-synchronize.


### REMARKS
+ :warning: Please note that the ALS162 transmitter in Allouis, France, is __sometimes offline due to maintenance work, e.g. every Tuesday morning from 08:00 to 12:00__.
+ This project has __not__ been tested with other SDR receivers.
+ This project has __not__ been tested with a receiver setup using a sound card.
+ This project has __not__ been tested with other antennas (e.g. a ferrite antenna).
+ A Low Noise Amplifier (LNA) is not needed.
+ The simulation of the transmitter channel and receiver does __not__ run at the same speed as ordinary seconds, but rather a little bit faster.
+ The SDR project provides the decoded ALS162 signal more or less in real-time, but it is probably __not__ accurate in terms of milliseconds and it is also delayed by approximately 2 seconds.
