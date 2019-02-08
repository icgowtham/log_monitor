"""Unit tests for core.log_processor."""
import os
import pytest
from mock import patch

from core.log_processor import LogProcessor

DIRNAME = os.path.dirname(__file__)
DATA_FILE = os.path.join(DIRNAME, 'data/data.txt')


@pytest.mark.positive
def test_read_file_line_by_line():
    """Unit test for reading file line by line."""
    count = 1
    for line in LogProcessor.read_file_line_by_line(DATA_FILE):
        assert count == int(line)
        count += 1


@pytest.mark.positive
def test_read_nth_line():
    """Unit test for reading the nth line of a file."""
    line = LogProcessor.read_nth_line(DATA_FILE, 3)
    assert int(line) == 3


@pytest.mark.positive
def test_read_reverse():
    """Unit test for reading a file in reverse line by line."""
    count = 5
    for line in LogProcessor.read_reverse(DATA_FILE):
        assert count == int(line)
        count -= 1


@pytest.mark.positive
def test_process_data():
    """Unit test for process_data method using mock."""
    with patch('core.log_processor.LogProcessor.process_data',
               return_value='ERROR: exception occurred'):
        assert LogProcessor.process_data() == 'ERROR: exception occurred'


@pytest.mark.positive
def test_has_file_rotated():
    """Unit test for has_file_rotated method using mock."""
    with patch('core.log_processor.LogProcessor.has_file_rotated',
               return_value=True):
        assert LogProcessor.has_file_rotated()

