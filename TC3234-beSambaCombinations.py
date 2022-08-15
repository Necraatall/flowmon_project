"""Test of setup Samba in all available combinations
    with data load and configuration check
"""
import datetime
import os
import re
import pytest
from lxml import etree
from common.runner import Runner
from common.remote_storage import RemoteStorage
from common.common_functions import CommonFunctions


PATH_LOCAL_XML = "sources/external_storage/"
PATH_FOS = "/tmp/proxy_test/"
PATH_SAMBA_ROOT = "/mnt/external/"

XML_SAMBA_ENABLED = os.path.join(PATH_LOCAL_XML, "192.168.4.156.xml")
XML_SAMBA_ENABLED_COPY = os.path.join(PATH_LOCAL_XML, "192.168.4.156_copy.xml")
PATH_BACKEND_STORAGE = os.path.join("/etc/flowmon/", "remote-storage.cfg")
PATH_BACKEND_REPORT = os.path.join("/etc/flowmon/", "flowmon_remote_report.cifs")
PATH_BACKEND_CREDENTIALS = os.path.join("/root/", ".flowmon_remote_report_credentials")

HARDCODED_STRING = "abcd123"
HARDCODED_MESSAGE = "File has different content. file content is: "
SAMBA_PASSWORD_CLEAR = 'qa'

def gen_unique_date() -> str:
    """Generate a unique date string"""
    return datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S_%s')


def copy_to_samba(_runvm1: Runner, local_filename: str):
    """Copy file to samba

    :param local_filename: absolute path of the file
    """
    ec, msg, _ = _runvm1.exec(f"sudo remote_storage -T -S {local_filename} -D {os.path.basename(local_filename)}")
    assert CommonFunctions.get_file_size(_runvm1, os.path.join(PATH_SAMBA_ROOT, os.path.basename(local_filename))) > 0


def copy_from_samba(_runvm1: Runner, samba_file: str) -> str:
    """Copy file from samba, save it with unique filename to PATH_FOS"""
    unique_date = gen_unique_date()
    downloaded_file = os.path.join(PATH_FOS, unique_date)
    ec, msg, _ = _runvm1.exec(f"sudo remote_storage -F -S {os.path.basename(samba_file)} -D {downloaded_file}")
    return downloaded_file


def remove_from_samba(_runvm1: Runner, samba_file: str):
    """Remove file from samba"""
    ec, msg, _ = _runvm1.exec(f"sudo remote_storage -E {os.path.basename(samba_file)}")
    assert not CommonFunctions.check_file_exists(_runvm1, samba_file), \
        f"File {samba_file} on samba exists, but it should not"


def assert_file_content(_runvm1: Runner, fname: str):
    """Compare file content in comparation with hardcoded string"""
    ec, msg, _ = _runvm1.exec(f"cat {fname}")
    assert msg.strip() == HARDCODED_STRING, f"{HARDCODED_MESSAGE} {msg}"


def check_storage_content(_runvm1: Runner, param_auth: bool, content: dict):
    """ Checks file (see PATH_BACKEND_STORAGE) content
        Checks file is on Flowmon
        Loads and checks file content is not null
        Assert all values
    :param _runvm1: Runner : See Class Runner
    :param param_auth: bool: Test Case parametrization for not/authorized way
    :param content: dict: Data from stored xml contain
    """
    hardcoded_enabled = "ENABLED="
    hardcoded_protocol = "PROTOCOL="
    hardcoded_protocol_version = "PROTOCOL_VERSION="
    hardcoded_authentication = "AUTHENTICATION="
    hardcoded_ip = "IP="
    hardcoded_port = "PORT="
    hardcoded_root_dir = "ROOT_DIR="
    hardcoded_domain = "DOMAIN="
    hardcoded_user = "USER="

    # Checks file is on Flowmon
    assert CommonFunctions.get_file_size(_runvm1, PATH_BACKEND_STORAGE) > 0

    # Loads and checks file content is not null
    ec, msg, _ = _runvm1.root_exec(f"cat {PATH_BACKEND_STORAGE}")
    file_content = msg

    # Assert all values
    # Assert enabled
    regex_string = f"(?<={hardcoded_enabled}\").*?(?=\")"
    assert re.search(regex_string, file_content).group() == content["enabled"], f"{HARDCODED_MESSAGE} {file_content}"
    # Assert protocol
    regex_string = f"(?<={hardcoded_protocol}\").*?(?=\")"
    assert re.search(regex_string, file_content).group() == content["protocol"], f"{HARDCODED_MESSAGE} {file_content}"
    # Assert protocolVersion
    regex_string = f"(?<={hardcoded_protocol_version}\").*?(?=\")"
    assert re.search(regex_string, file_content).group() == content["protocolVersion"], f"{HARDCODED_MESSAGE} {file_content}"
    # Assert authentication
    regex_string = f"(?<={hardcoded_authentication}\").*?(?=\")"
    assert re.search(regex_string, file_content).group() == content["authentication"], f"{HARDCODED_MESSAGE} {file_content}"
    # Assert ip
    regex_string = f"(?<={hardcoded_ip}\").*?(?=\")"
    assert re.search(regex_string, file_content).group() == content["ip"], f"{HARDCODED_MESSAGE} {file_content}"
    # Assert port
    regex_string = f"(?<={hardcoded_port}\").*?(?=\")"
    assert re.search(regex_string, file_content).group() == content["port"], f"{HARDCODED_MESSAGE} {file_content}"
    # Assert root
    regex_string = f"(?<={hardcoded_root_dir}\").*?(?=\")"
    assert re.search(regex_string, file_content).group() == content["root"], f"{HARDCODED_MESSAGE} {file_content}"
    # Assert domain
    regex_string = f"(?<={hardcoded_domain}\").*?(?=\")"
    assert re.search(regex_string, file_content).group() == content["domain"], f"{HARDCODED_MESSAGE} {file_content}"
    # Assert USER/login
    if param_auth:
        regex_string = f"(?<={hardcoded_user}\").*?(?=\")"
        assert re.search(regex_string, file_content).group() == content["domain"], f"{HARDCODED_MESSAGE} {file_content}"


def check_report_content(_runvm1: Runner, content: dict):
    """ Checks file (see PATH_BACKEND_REPORT) content
        Checks file is on Flowmon
        Loads and checks file content is not null
        Assert all values
    :param _runvm1: Runner : See Class Runner
    :param param_auth: bool: Test Case parametrization for not/authorized way
    :param content: dict: Data from stored xml contain
    """
    hardcoded_protocol = "-fstype="
    hardcoded_protocol_version = "vers="
    hardcoded_authentication = "sec="
    hardcoded_ip = "://"
    hardcoded_port = "port="
    hardcoded_root_dir = "/"

    # Checks file is on Flowmon
    assert CommonFunctions.get_file_size(_runvm1, PATH_BACKEND_REPORT) > 0

    # Loads and checks file content is not null
    ec, msg, _ = _runvm1.root_exec(f"cat {PATH_BACKEND_REPORT}")
    file_content = msg
    # Assert values
    # Assert protocol
    regex_string = f"(?<={hardcoded_protocol}).*?(?=,)"
    assert re.search(regex_string, file_content).group() == content["protocol"], f"{HARDCODED_MESSAGE} {file_content}"
    # Assert protocolVersion
    regex_string = f"(?<={hardcoded_protocol_version}).*?(?=,)"
    assert re.search(regex_string, file_content).group() == content["protocolVersion"], f"{HARDCODED_MESSAGE} {file_content}"
    # Assert authentication
    regex_string = f"(?<={hardcoded_authentication}).*?(?=,)"
    assert re.search(regex_string, file_content).group() == content["authentication"], f"{HARDCODED_MESSAGE} {file_content}"
    # Assert ip
    regex_string = f"(?<={hardcoded_ip}).*?(?=/)"
    ip_value = re.search(regex_string, file_content).group()
    assert ip_value == content["ip"], f"{HARDCODED_MESSAGE} {file_content}"
    # Assert port
    regex_string = f"(?<={hardcoded_port}).*?(?=,)"
    assert re.search(regex_string, file_content).group() == content["port"], f"{HARDCODED_MESSAGE} {file_content}"
    # Assert root
    regex_string = f"(?<={ip_value}{hardcoded_root_dir}).*?(?=\n)"
    assert re.search(regex_string, file_content).group() == content["root"], f"{HARDCODED_MESSAGE} {file_content}"


def check_credential_content(_runvm1: Runner, param_auth: bool, content: dict):
    """ Checks file (see PATH_BACKEND_CREDENTIALS) content
        Checks file is on Flowmon
        Loads and checks file content is not null
        Assert all values
    :param _runvm1: Runner : See Class Runner
    :param param_auth: bool: Test Case parametrization for not/authorized way
    :param content: dict: Data from stored xml contain
    """
    hardcoded_domain = "domain="
    hardcoded_username = "username="
    hardcoded_password = "password="

    # Checks file is on Flowmon
    assert CommonFunctions.get_file_size(_runvm1, PATH_BACKEND_CREDENTIALS) > 0

    # Loads and checks file content is not null
    ec, msg, _ = _runvm1.root_exec(f"cat {PATH_BACKEND_CREDENTIALS}")
    file_content = msg

    # Assert all values
    # Assert domain
    regex_string = f"(?<={hardcoded_domain}).*?(?=\n)"
    assert re.search(regex_string, file_content).group() == content["domain"], f"{HARDCODED_MESSAGE} {file_content}"

    if param_auth:
        # Assert username
        regex_string = f"(?<={hardcoded_username}).*?(?=\n)"
        assert re.search(regex_string, file_content).group() == content["domain"], f"{HARDCODED_MESSAGE} {file_content}"
        # Assert password
        regex_string = f"(?<={hardcoded_password}).*?(?=\n)"
        assert re.search(regex_string, file_content).group() == SAMBA_PASSWORD_CLEAR, f"{HARDCODED_MESSAGE} {file_content}"


def check_backend_configs(_runvm1: Runner, param_auth: bool):
    """ Read Xml on Flowmon
        assert all values in files:
        PATH_BACKEND_STORAGE
        PATH_BACKEND_REPORT
        PATH_BACKEND_CREDENTIALS
    :param param_auth: Bool of authentizated true or not
    - output from test parametrization
    """
    xml_conf_data_file = {
            "enabled":"",
            "protocol":"",
            "protocolVersion":"",
            "authentication":"",
            "ip":"",
            "port":"",
            "root":"",
            "domain":"",
            "login":"",
    }

    doc_content = etree.parse(XML_SAMBA_ENABLED_COPY)
    # from lxml import data into xml_conf_data_file
    for each in xml_conf_data_file:
        xcontent = doc_content.xpath(f'//{each}/text()')
        # part for formating from list into string
        if xcontent:
            xml_conf_data_file.update({each: xcontent[0]})
        else:
            xml_conf_data_file.update({each: ''})

    check_storage_content(_runvm1, param_auth, xml_conf_data_file)
    check_report_content(_runvm1, xml_conf_data_file)
    check_credential_content(_runvm1, param_auth, xml_conf_data_file)


def setup_samba(_runvm1: Runner):
    """ Disable Samba
        Configure Samba
        Checks state of remote
        Copy the xml file to Flowmon
        Assert that uploaded xml is not empty
    :param _runvm1: Runner : See Class Runner
    """
    # disable Samba
    RemoteStorage.disable_rs(_runvm1)

    # Copy the xml file to Flowmon
    CommonFunctions.upload_and_import(_runvm1, XML_SAMBA_ENABLED_COPY)
    RemoteStorage.rs_state(_runvm1, True)


test_data = [
    ("1.0", "ntlm", "445"),
    ("1.0", "ntlmv2", "446"),
    ("2.0", "ntlmv2", "447"),
    ("2.1", "ntlmv2", "448"),
    ("3.0", "ntlmv2", "449"),
]

test_data_auth = [
    True,
    False
]


@pytest.mark.timeout(300)
@pytest.mark.parametrize("param_auth", test_data_auth)
@pytest.mark.parametrize("param_v, param_a, param_p", test_data)
def test_samba_combinations(_runvm1: Runner, param_v: str, param_a: str, param_p: str, param_auth: bool):
    """Testing Samba configuration Flowmon
    Steps
    1. xml values preparation
    2. generate unique filename with hardcoded string
    3. copy file to Samba
    4. disable Samba and configure it again
    5. check that file on Samba still exists and contains correct data
    6. check directly via backend - Linux
    7. check via remote_storage binary - download and check file
    8. cleanup - files on Flowmon and on Samba
    """
    # XML values preparation
    os.system(f"cp -f {XML_SAMBA_ENABLED} {XML_SAMBA_ENABLED_COPY}")

    if not param_auth:
        # remove <login> and <password> tags, </login> does not work!
        os.system(f"sed -i '/<login>*/d' {XML_SAMBA_ENABLED_COPY}")
        os.system(f"sed -i '/<password>*/d' {XML_SAMBA_ENABLED_COPY}")

    os.system(f"sed -i 's%<protocolVersion>.*</protocolVersion>%<protocolVersion>{param_v}</protocolVersion>%' {XML_SAMBA_ENABLED_COPY}")
    os.system(f"sed -i 's%<authentication>.*</authentication>%<authentication>{param_a}</authentication>%' {XML_SAMBA_ENABLED_COPY}")
    os.system(f"sed -i 's%<port>.*</port>%<port>{param_p}</port>%' {XML_SAMBA_ENABLED_COPY}")

    setup_samba(_runvm1)
    check_backend_configs(_runvm1, param_auth)

    # generate unique filename with hardcoded string
    remote_text_name = f"platformautotests_{gen_unique_date()}"
    remote_text_path = os.path.join(PATH_FOS, remote_text_name)
    ec, msg, _ = _runvm1.exec(f'mkdir -p {PATH_FOS}')
    ec, msg, _ = _runvm1.exec(f'echo "{HARDCODED_STRING}" > {remote_text_path}')

    # copy file to Samba
    setup_samba(_runvm1)
    copy_to_samba(_runvm1, remote_text_path)

    # disable Samba and configure it again
    RemoteStorage.disable_rs(_runvm1)
    CommonFunctions.upload_and_import(_runvm1, XML_SAMBA_ENABLED_COPY)

    # check that file on Samba still exists and contains correct data
    samba_file = os.path.join(PATH_SAMBA_ROOT, remote_text_name)
    # check directly via backend - Linux
    assert_file_content(_runvm1, samba_file)
    # check via remote_storage binary - download and check file
    downloaded_samba_file = copy_from_samba(_runvm1, samba_file)
    assert_file_content(_runvm1, downloaded_samba_file)

    # cleanup - files on Flowmon and on Samba
    ec, msg, _ = _runvm1.exec(f'rm -rf {PATH_FOS}')
    remove_from_samba(_runvm1, samba_file)
    os.system(f"rm -f {XML_SAMBA_ENABLED_COPY}")
