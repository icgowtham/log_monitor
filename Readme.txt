Log Monitor - Python based application to monitor log files.

Introduction:
This is a Python based application for monitoring rotating log files. It is roughly based on a publisher-subscriber model, where in one application checks for a particular error pattern in the log files and places that information onto a queue (ZMQ). Another application waits for the information to be available on the queue and uses it.

Bootstrapping Steps:
1. Create a temporary folder. For e.g.:
mkdir -p gow_test/log_monitor

2. Copy the contents of the zip file to the newly created directory.

3. Change to the newly created directory. For e.g.:
cd gow_test/log_monitor

4. Create a Python virtual environment. This can be either done manually using:
virtualenv -p python3 env3
or by typing:
make setup-env

5. Activate the virtual environment. For e.g.
source env3/bin/activate

6. Install the application requirements using:
pip3 install -r requirements.txt

7. Set PYTHONPATH using:
export PYTHONPATH=.

8. A sample log simulator application is provided for testing. It can be run using:
python3 utils/log_simulator.py
Let it run for some 5-10 mins. Stop the application using Ctrl-C.

9. On one terminal run the manager application first:
python3 core/log_process_manager.py

10. On another terminal run the log processor application:
python3 core/log_processor.py
