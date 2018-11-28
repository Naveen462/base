from test_logger import MyLogger, FileLogger
from test_cases.KALI.kali import Kali
from test_cases.KALI.define import TestCases
from argparse import ArgumentParser
import configparser
from lib.helpers import check_ip
import os
import sys
import importlib
from define import OTS_LABEL, BANNER, SETUP, RUNNING, RESULT, TEST_FOLDER, ROOT_FOLDER, SKIP_ITEMS, CONFIG_FILE


def import_test(test_path):
    """
    Import the KaliTest class from a given test file

    Params:
        test_path(str): path where test case is stored

    Returns:
        (class): KaliTest class

    Raises:
        AttributeError if cannot find KaliTest class
    """
    test_path_l = test_path.split(os.sep)
    suite = test_path_l[-3]
    chapter = test_path_l[-2]
    test = test_path_l[-1].split('.')[0]
    module = '.'.join(['tests', suite, chapter, test])
    module = importlib.import_module(module)
    try:
        return getattr(module, 'KaliTest')
    except AttributeError as e:
        raise e


class TestSuite:
    """
    TestSuite class definition

    Params:
        path: abs path of the test suite
    """
    def __init__(self, path):
        self.name = path.split(os.sep)[-1]
        self.path = path
        self.chapters = []

    def add(self, chapter):
        """
        Add a chapter to the test suite

        Params:
            chapter(obj): TestChapter object

        Raises:
            TypeError if wrong type chapter
        """
        if isinstance(chapter, TestChapter):
            self.chapters.append(chapter)
        else:
            raise TypeError("Invalid type passed")

    def run(self):
        """
        Execute each chapter in the test suite
        """
        for chapter in self.chapters:
            chapter.run()


class TestChapter:
    """
       TestChapter class definition

       Params:
           path: abs path of the test chapter
       """
    def __init__(self, kali, path):
        self.kali = kali
        self.name = path.split(os.sep)[-1]
        self.path = path
        self.tests = []

    def add(self, test):
        """
        Add a test case to the chapter

        Params:
            chapter(obj): KaliTestCase object (or subclass)
        """
        self.tests.append(test)

    def run(self):
        """
        Execute each test in the chapter
        """
        for test in self.tests:
            test_obj = test(self.kali, self.kali.logger)
            self.kali.info(BANNER % (test_obj.test_title, test_obj.test_number, self.path))
            self.kali.run(test, ots_label=OTS_LABEL)


class TestLauncher:
    """
    TestLauncher class definition

    Params:
        kali(obj): Kali object
        ip(str): OTS ip
        port(int): OTS port
        addons_required(bool): True if all addons are required, False otherwise
        max_duration(int): max duration for each test case
    """
    def __init__(self, kali, ip='172.20.100.254', port=10000, addons_required=False, max_duration=None):
        self.kali = kali
        self.kali.info(SETUP)
        self.path = TEST_FOLDER
        sys.path.append(ROOT_FOLDER)
        self.ip = ip
        self.port = port
        self.addons_required = addons_required
        self.max_duration = max_duration
        self.test_suites = []
        self.kali.start_connection_ots(OTS_LABEL, ip, port)
        if addons_required:
            self.setup_all_addons()
        self.set_tags()

    def setup_all_addons(self):
        """
        Setup all needed addons
        """
        self.kali.add_omnia_bash_addon('bash', ots_label=OTS_LABEL)
        self.kali.add_omnia_dbus_addon('dbus', ots_label=OTS_LABEL)
        self.kali.add_omnia_main_addon('main', ots_label=OTS_LABEL)
        self.kali.add_omnia_webui_addon('webui', ip=self.ip)

    def set_tags(self):
        """
        Set tags on Kali read from config file
        """
        self.kali.info("Setting up test tags")
        config = configparser.ConfigParser()
        try:
            config.read(CONFIG_FILE)
            self.set_tag_rules(config)
        except KeyError:
            self.kali.error("Invalid config file")

    def set_tag_rules(self, config):
        refused_tags = config["RULES"]["deny"].split(',')
        accepted_tags = config["RULES"]["allow"].split(',')
        if refused_tags[0] != '':
            refused_tags = [TestCases[tag] for tag in refused_tags]
            self.kali.refused_tags = refused_tags
        if accepted_tags[0] != '':
            accepted_tags = [TestCases[tag] for tag in accepted_tags] + self.get_default_tags(config)
            self.kali.accepted_tags = accepted_tags
        else:
            self.kali.accepted_tags = self.get_default_tags(config)

    def get_default_tags(self, config):
        tags = []
        for key, tag in config["TEST_INFO"].items():
            if tag != '':
                tags.append(tag)
        return tags

    def run(self):
        """
        Execute each test suite
        """
        self.create_test_suite_structure()
        self.kali.info(RUNNING)
        for ts in self.test_suites:
            try:
                self.kali.info('RUNNING TEST SUITE: ' + ts.name)
                ts.run()
            except KeyboardInterrupt:
                self.kali.failed('Check failed!')
                self.kali.info('Tests execution interrupted. Exiting...')
                self.kali._cur_test_case.add_failed()
                self.kali.end_test_case()
                self.kali.info(self.kali.prettyprint_test_cases_result())
                sys.exit()
            except Exception as e:
                self.kali.error(e)
                self.kali._cur_test_case.add_failed()
                self.kali.failed('Check failed!')
                self.kali.end_test_case()
        self.kali.info(RESULT)
        try:
            self.kali.info(self.kali.prettyprint_test_cases_result())
        except Exception as e:
            self.kali.error(e)

    def create_test_suite_structure(self):
        """
        Iterate over tests directory to find all available test suites
        """
        _dir = os.fsencode(self.path)
        for suite_name in os.listdir(_dir):
            suite_name = os.fsdecode(suite_name)
            suite_path = os.path.join(self.path, suite_name)
            if os.path.isdir(suite_path) and suite_name not in SKIP_ITEMS:
                test_suite = TestSuite(suite_path)
                self.kali.info('New Test Suite found: ' + test_suite.name)
                self.test_suites.append(test_suite)
                self.create_test_chapter_structure(suite_path, test_suite)

    def create_test_chapter_structure(self, suite_path, test_suite):
        """
        Iterate over test suite directory to find all chapters

        Params:
            suite_path(str): path where test suite is stored
            test_suite(obj): TestSuite object
        """
        for chapter_name in os.listdir(os.fsencode(suite_path)):
            chapter_name = os.fsdecode(chapter_name)
            chapter_path = os.path.join(suite_path, chapter_name)
            if os.path.isdir(chapter_path) and chapter_name not in SKIP_ITEMS:
                test_chapter = TestChapter(self.kali, chapter_path)
                test_suite.add(test_chapter)
                self.kali.info('Adding %s chapter to %s test suite' % (test_chapter.name, test_suite.name))
                self.create_tests_structure(chapter_path, test_chapter)

    def create_tests_structure(self, chapter_path, test_chapter):
        """
        Iterate over chapter directory to find all available tests

        Params:
            chapter_path(str): path where chapter is stored
            test_chapter(obj): TestChapter object
        """
        for test_name in os.listdir(os.fsencode(chapter_path)):
            test_name = os.fsdecode(test_name)
            test_path = os.path.join(chapter_path, test_name)
            if test_name not in SKIP_ITEMS:
                try:
                    test = import_test(test_path)
                    test_chapter.add(test)
                except AttributeError:
                    self.kali.warning("Skipped file: " + str(test_name))
                    break


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-i', '--ip', type=str, help='OTS ip address', default='172.20.100.254')
    parser.add_argument('-p', '--port', type=int, help='OTS port', default=10000)
    parser.add_argument('-o', '--out-path', type=str, help='Path where store logs', default=None)
    parser.add_argument('-a', '--addons', action='store_true', help='Instance all addons')
    parser.add_argument('-m', '--max-duration', type=int, help='Max duration for each test case', default=None)
    parser.add_argument('-v', '--version', type=str, help='OMNIA version label', default=None)
    args = parser.parse_args()

    k = Kali()

    if args.out_path:
        l = FileLogger(args.out_path)
    else:
        l = MyLogger()
    k.set_logger(l)

    if check_ip(args.ip):
        k.info('Running test cases...')
        launcher = TestLauncher(k, args.ip, args.port, args.addons, args.max_duration)
        launcher.run()
    else:
        k.error('Invalid arguments')
l