"""Log Processor class."""

import configparser
import os
import time

import zmq

__author__ = 'Ishwarachandra Gowtham'
__email__ = 'ic.gowtham@gmail.com'


class LogProcessor:
    """Class for handling the log processing functions."""

    # The text file containing the last read file position.
    CTRL_FILE_PATH = os.path.abspath('ctrl.db.txt')

    def __init__(self):
        """
        Initialization method.

        :param: None
        :return: None
        """
        # Read all the required configurations from the config file.
        self._config = configparser.ConfigParser()
        self._config.read(os.path.abspath('config.ini'))
        self._current_file = self._config['DEFAULT']['LOG_FILE']
        self._previous_file = self._config['DEFAULT']['ROTATED_LOG_FILE']
        self._pattern = self._config['DEFAULT']['PATTERN']
        # Check whether our control file exists.
        if not os.path.exists(LogProcessor.CTRL_FILE_PATH):
            self._last_read_file_pos = 0
        else:
            with open(LogProcessor.CTRL_FILE_PATH, 'r') as store:
                self._last_read_file_pos = int(store.readline())
        # Here we are using ZeroMQ as the queue.
        # Below are the ZeroMQ related configuration which are required.
        self._context = zmq.Context()
        # This application is the 'publisher' which publishes the data onto the queue.
        self._connector = self._context.socket(zmq.PUB)  # pylint: disable=maybe-no-member
        # Connect to a higher numbered port.
        self._connector.bind('tcp://*:25647')

    def has_file_rotated(self):
        """
        Method to check whether the log file has been rotated.

        :return: Boolean
        """
        # Using getsize to make this platform independent. But there might be a
        # case where the log file rotation has taken place and the size is equal
        # to the last read file position. For that on Unix based systems we can
        # make use of the 'inode' of the file to check. But that might not work
        # as expected on non-Unix based platforms.
        # TODO: Need to figure out a way to handle this case.  # pylint: disable=fixme
        if self._last_read_file_pos > os.path.getsize(self._current_file):
            return True
        # elif os.fstat(current_file_handler.fileno()).st_ino != \
        #         os.fstat(previous_file_handler.fileno()).st_ino:
        #     return True
        return False

    def process_file(self):
        """
        Method to read the contents of the log file.

        This method tries to determine whether the log has been rotated or not.
        If the log file is rotated, it will first read the contents of the rotated log
        file first from the last read location. Then, it will attempt to read the contents
        of the current log file.

        :param: None
        :return: None
        """
        # If the file has been rotated, then we need to read the previous log file from the
        # last read position till end and then read the current log file from the beginning.
        # TODO: For simplicity, at present, we are assuming that there will be a  # pylint: disable=fixme
        #  single rotated log file. Normally there will be more than one rotated log file.
        #  Need to figure out to handle that as well.
        if self.has_file_rotated():
            print('The file has been rotated, first reading file: ', self._previous_file)
            self.process_data(self._previous_file, False)
            # Reset for the new file and read from the beginning.
            self._last_read_file_pos = 0
        self.process_data(self._current_file, True)

    def process_data(self, file_name, is_store_last_read_position):
        """
        Method to process the data of the log file and place the information onto the queue.

        This method tries to read the contents of the log file line by line and if the line
        contains the pattern which we are looking for, then it places that line onto the queue (zmq).

        :param file_name: str
            The name of the log file (along with path).
        :param is_store_last_read_position: Boolean
            Flag to indicate whether to record the last read position of the file onto the control file.
        :return: None
        """
        try:
            # TODO: There maybe a case where this application would be  # pylint: disable=fixme
            #  in the middle of reading the log file, while log rotation
            #  takes place. Need to figure out to handle this case.
            with open(file_name) as file_handle:
                file_handle.seek(self._last_read_file_pos, 0)
                for line in self.__get_lines(file_handle):
                    # Get the line matching the pattern and place it onto the queue for
                    # further processing.
                    self._connector.send_string(line)
                    print('Sending: ', line)
        finally:
            # Record the last read position of the log file for use with the next run.
            if is_store_last_read_position:
                with open(LogProcessor.CTRL_FILE_PATH, 'w') as store:
                    store.write(str(self._last_read_file_pos))

    def __get_lines(self, file_handle):
        """
        Private method to generate the log file lines on by one.

        :param file_handle: object
            The file handle object for the log file.
        :return: str
        """
        while True:
            line = file_handle.readline()
            if line:
                self._last_read_file_pos = file_handle.tell()
                if self._pattern in line:
                    yield line
            else:
                break

    @staticmethod
    def read_file_line_by_line(file_name):
        """
        Function to read a file line by line.

        :param file_name: str
            Name of the file to be read.
        :return: str
            Contents of the file, one line at a time.
        """
        with open(file_name) as file_handle:
            while True:
                content = file_handle.readline()
                if not content:
                    break
                yield content

    @staticmethod
    def read_nth_line(file_name, line_no=1):
        """
        Function to return the contents of the nth line of a file.

        :param file_name: str
            Name of the file to be read.
        :param line_no: int
            The line number to read.
        :return: str
            Contents of the nth line (as indicated by line_no).
        """
        ret_val = None
        with open(file_name) as file_handle:
            for ln_num, content in enumerate(file_handle):
                if ln_num == (line_no - 1):
                    ret_val = content
                    break
        return ret_val

    @staticmethod
    def read_reverse(file_name):
        """
        Function to read a file backwards.

        This function reads a file backwards, word by word and line by line.
        :param file_name: str
            Name of the file to be read backwards.
        :return: str
            Reversed contents of the file, one line at a time.
        """
        with open(file_name) as file_handle:
            # Go to the last of the file.
            file_handle.seek(0, os.SEEK_END)
            # Capture the current position of the cursor.
            current_pos = file_handle.tell()
            line = ''
            while current_pos >= 0:
                file_handle.seek(current_pos)
                # Read a single character of the current line.
                next_char = file_handle.read(1)
                # Check if it is the line break character.
                if next_char == '\n':
                    # 'yield' the line.
                    if line:
                        yield line[::-1]
                    line = ''
                else:
                    line += next_char
                current_pos -= 1
            yield line[::-1]


if __name__ == '__main__':
    processor = LogProcessor()
    # Sleep so that the zmq connection is established.
    time.sleep(5)
    processor.process_file()
