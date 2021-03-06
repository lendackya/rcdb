import rcdb.config_parser
from rcdb.config_parser import ConfigFileParseResult, ConfigSection

import logging

from rcdb.log_format import BraceMessage as F


# Setup logger
log = logging.getLogger('rcdb.halld.main_config_parser')         # create run configuration standard logger


section_names = ["TRIGGER", "GLOBAL", "FCAL","BCAL","TOF","ST","TAGH", "TAGM", "PS", "PSC", "TPOL", "CDC", "FDC"]


class HallDMainConfigParseResult(object):

    def __init__(self, config_parse_result):
        assert isinstance(config_parse_result, ConfigFileParseResult)
        self.config_parse_result = config_parse_result

        self.trigger_eq = []
        self.trigger_type = []
        self.trigger_ts_type = None
        self.trigger_ts_gtp_pres = None     # TS_GTP_PRES Prescaling factors for each line
        self.trigger_ts_coin_wind=None      # --type int --description "TS_COIN_WIND Trigger merging window"
        self.trigger_ts_sync_int =None      # --type int --description "TS_SYNC_INT Period for SYNC events"
        self.trigger_block_level =None      # --type int --description "BLOCKLEVEL"
        self.trigger_buffer_level=None      # --type int --description "BUFFERLEVEL from TRIGGER section"
        self.fcal_fadc250_mode   =None      # FADC250_MODE from FCAL run config section
        self.fcal_fadc250_params =None      # some FADC250_* parameters from FCAL section of run config
        self.bcal_fadc250_mode   =None      # int FADC250_MODE from BCAL run config section
        self.bcal_fadc250_params =None      # some FADC250_* parameters from BCAL section of run config
        self.cdc_fadc125_mode = -1
        self.cdc_fadc125_params = None  # some FADC125_* parameters from CDC section of run config




         # --type json --description "some FADC250_* parameters from FCAL section of run config"



def parse_file(file_name):
    parse_result = rcdb.config_parser.parse_file(file_name, section_names)
    return _process_parse_result(parse_result, file_name)


def parse_content(content):
    parse_result = rcdb.config_parser.parse_content(content, section_names)
    return _process_parse_result(parse_result)


def _process_parse_result(parse_result, file_name=""):

    result = HallDMainConfigParseResult(parse_result)

    # TRIGGER section
    if 'TRIGGER' in parse_result.found_section_names:
        trigger_section = parse_result.sections["TRIGGER"]
        assert isinstance(trigger_section, ConfigSection)

        # Find all TRIG_EQ lines
        result.trigger_eq = [row[1:] for row in trigger_section.rows if row[0] == 'TRIG_EQ']

        # Find all TRIG_TYPE lines
        result.trigger_type = [row[1:] for row in trigger_section.rows if row[0] == 'TRIG_TYPE']

    else:
        log.warning(F("TRIGGER section is not found in '{}'", file_name))

    # CDC section
    if 'CDC' in parse_result.found_section_names:
        cdc_section = parse_result.sections["CDC"]
        assert isinstance(cdc_section, ConfigSection)

        if 'FADC125_MODE' in cdc_section.entities:
            try:
                result.cdc_fadc125_mode = int(cdc_section.entities['FADC125_MODE'])
            except ValueError as ex:
                log.warning(F("Cant convert CDC:FADC125_MODE value '{}' to int", cdc_section.entities['FADC125_MODE']))
    else:
        log.warning(F("CDC section is not found in '{}'", file_name))

    return result








