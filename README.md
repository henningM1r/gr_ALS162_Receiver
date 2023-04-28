# gr_ALS162_Receiver
This is a basic ALS162 time signal receiver for GNURadio, containing:
1. signal demodulation and detection of the ALS162 signal with an SDR using GNURadio (and Python modules)
2. a simple live decoder of received bits provided by the GNURadio ALS162 receiver


### Overview
The __flowgraph__ is provided in the `examples` folder:
+ `ALS162_receiver.grc`
    + for both SDR reception

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
    + Ubuntu 22.04.2 LTS


### Instructions/Setup

#### Signal Reception with SDR
+ Set up your SDR with your computer.
+ Ensure that the raw ALS162 signal reception at 162.0 kHz is good enough, e.g. using gqrx or another signal analysis tool.
+ To start the ALS162 receiver, open the flowchart in `/examples/ALS162_receiver.grc` with GNURadio Companion
    + Press `run` button.
    + First, deactivate the following auxiliary signals in the plot for now (Derivative, +2, +1, 0, -1, -2), and keep the remaining signals (Phase, Symbols, avg. Phase).
    + Wait a few seconds until the Phase signal in the _Phase Drift Compensation_ plot roughly aligns at 0 between the values -1 and 1. If the transient phase of the control loop is still too jumpy, reduce the _shift step_ slider slightly.
    + reactivate the auxiliary signal _Derivative_ and set the _diff_gain_ slider values so that the amplitudes of _Derivative"_ are roughly at +/-3000 and +/-6000, respectively.
    + Only adjust the sliders for the _thresholds_, if really needed. You should rather avoid to change them.
    + After sufficient parameter adjustment, the GNURadio Companion debug console should show a debug message each second with either '0' or '1' or '2' (for a new minute). And the plot should indicate these symbols with tags, given _symbols_ is activated.
    + Optionally,
        + you can adjust zoom the signal amplitude of the plot with _zoom_.
        + you can investigate the results of the _threshold values_ on the Derivated phase signal by activating +2,+1,0,-1,-2, respectively.

+ Next, open a terminal or Powershell.
    + Change to your cloned repository.
    + Run the DecodeALS162 with ```python3 ./python/DecodeALS162.py```.
    + The terminal should show the received bits together with a sequence of indices.
    + after approximately 2 minutes, DecodeALS162 should be synchronized with the transmitter. It should provide the current time, date, etc. each minute.
    + NOTE: sometimes a bit can not be decoded correctly, e.g. due to bad reception. Then the current frame of the minute is corrupted and will attempt to re-synchronize.


### REMARKS
+ This project has __not__ been tested with other SDR receivers.
+ This project has __not__ been tested with a receiver setup using a sound card.
+ This project has __not__ been tested with other antennas (e.g. a ferrite antenna).
+ A Low Noise Amplifier (LNA) is not needed.
+ Even a single lost bit during reception causes the synchronization of a full minute to fail. Additional resilience of the decoder has __not__ been implemented yet.
