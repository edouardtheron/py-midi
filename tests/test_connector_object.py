from unittest.mock import patch, call, Mock

import pytest

from midi.midi import MidiConnector, Message
from midi.types import NoteOff


def get_bytes(integer):
    assert isinstance(integer, int)
    return integer.to_bytes(1, 'big')

@pytest.fixture
def message():
    note_off = NoteOff(35, 127)
    return Message(note_off, 1)


@pytest.fixture
def midi_bytes():
    values = [220, 100, 35]
    return [get_bytes(value) for value in values]


@patch('midi.midi.Serial', autospec=True)
def test_write(mock_serial, message):
    """Check if 'write' method from serial.Serial is called as expected."""
    conn = MidiConnector('/path/to/serial/port')

    conn.write(message)

    expected_calls = [call().write(data) for data in message.bytes_content]
    assert mock_serial.method_calls == expected_calls


@patch('midi.midi.Serial', autospec=True)
def test_read_standard(mock_serial):
    """3 bytes expected"""
    reader = Mock()
    reader.side_effect = [bytes([value]) for value in [128, 35, 65]]
    conn = MidiConnector('/path/to/serial/port', test=True, read_func=reader)

    message = conn.read()

    assert isinstance(message, Message)
    assert isinstance(message.type, NoteOff)
    assert message.channel == 1
    assert message.note_number == 35
    assert message.velocity == 65