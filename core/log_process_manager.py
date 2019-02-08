"""Log process mananger class."""

import re

import pandas as pd
import zmq

__author__ = 'Ishwarachandra Gowtham'
__email__ = 'ic.gowtham@gmail.com'


class LogProcessManager:  # pylint: disable=too-few-public-methods
    """Class for managing the log processing functions."""

    def __init__(self):
        """
        Initialization method.

        :param: None
        :return: None
        """
        self._context = zmq.Context()
        # This application is the 'subscriber' for the data in the queue.
        self._connector = self._context.socket(zmq.SUB)  # pylint: disable=maybe-no-member
        self._connector.connect('tcp://localhost:25647')
        self._connector.setsockopt_string(zmq.SUBSCRIBE, "")  # pylint: disable=maybe-no-member

    def monitor(self):
        """
        Method to monitor the queue for new data.

        This method monitors the queue for any new data.

        :return: None
        """
        data_list = []
        while True:
            message = self._connector.recv()
            message_str = message.decode('utf-8')
            temp = re.split('- -', message_str)
            ip_field = temp[0].rstrip()
            timestamp_field = temp[1][temp[1].find('[') + 1:temp[1].find(']')]
            log_message_field = temp[1][temp[1].find(']') + 1:].lstrip()
            data_list.append([timestamp_field, ip_field, log_message_field])

            if len(data_list) > 50:
                # print(message_str) # or send e-mail.
                # Store in Pandas data frame
                df_obj = pd.DataFrame(data_list,
                                      columns=['Time', 'IP', 'Message'])
                data_list.clear()
                grouped_msg = df_obj.groupby('Message')
                # TODO: The report is not coming as expected.  # pylint: disable=fixme
                #  Need to figure this out.
                print(grouped_msg.describe())
                df_obj = None


if __name__ == '__main__':
    manager = LogProcessManager()
    manager.monitor()
