"""Checks IO priority on processes is highest"""
import pytest
from common.runner import Runner

test_data = [
    "sfcapd",
    "xfcapd-streamd",
    "nfcapd",
]

def io_priority_set(_runvm1: Runner, content: str, io_priority: int):
    """ Change IO prio by the prio arg
    On this Test Case it is firstly:
    "3"
    and after:
    "0"
    :param _runvm1: Runner : See Class Runner
    :param content: str : content is string of pid
    :param io_priority: str : priority for setup io priority
    """
    # Reconfig prio to io_priority value
    for pid_value in content.splitlines():

        ec, msg, _ = _runvm1.root_exec(f"ionice -p {pid_value} -n {io_priority}")
        ec, msg, _ = _runvm1.root_exec(f"ionice -p {pid_value}")
        assert msg.strip() == f"best-effort: prio {io_priority}"


@pytest.mark.timeout(30)
@pytest.mark.parametrize("test_io_data", test_data)
def test_of_io_data(_runvm1: Runner, test_io_data: str):
    """Set higher IO priority for collector processes
     so they are preferred over nfdump queries etc.
    AC:
    nfcapd, sfcapd, xfcapd-streamd
    are running as be/0 (see using iotop or ionice)

    In all test_data values
    1. Gets pid value
    2. Prepares content for change
    3. Prepare io prio of value 3
    4. Prepare io prio of value 0
    :param _runvm1: Runner : See Class Runner
    :param content: str : content is string of pid
    """
    # Gets pid value
    ec, content, _ = _runvm1.root_exec(f"ps -C {test_io_data} -o pid=")

    # Prepare io prio of value 3
    io_priority_set(_runvm1, content, 3)

    # Prepare io prio of value 0
    io_priority_set(_runvm1, content, 0)
