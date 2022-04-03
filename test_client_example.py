#!/usr/bin/env python3
import argparse
import json
import sys
import requests
import os
from datetime import datetime

from eologger.eologger import EOLogger, LogLevel

# Class for interacting with bots.
class CompetitionBot:
    def __init__(
        self,
        team_name,
        address, 
        logger: EOLogger,
        dir_to_write,
    ):
        self.team_name = team_name
        self.address = address
        self.logger = logger
        self.is_sane = False
        self.dir_to_write = dir_to_write
        self.answer_csv_file_path = os.path.join(
            self.dir_to_write,
            "{}.csv".format(self.team_name)
        )

    def _bot_log(self, message, log_level: LogLevel = LogLevel.INFO):
        self.logger.log(
            message=message,
            log_level=log_level,
            source=self.team_name
        )

    def check_sanity(self):
        sanity_url = "http://{0}/sanity".format(self.address)
        try:
            response = requests.get(
                url=sanity_url,
                timeout=60
            )
        except requests.Timeout:
            self._bot_log("Sanity request timed out.", log_level=LogLevel.ERROR)
        except requests.exceptions.ConnectionError:
            self._bot_log("Error connecting to bot, possible server not started or disconnected.", log_level=LogLevel.ERROR)
        except Exception as exception:
            self._bot_log("An exception occured in the request: ", log_level=LogLevel.ERROR)
            print(exception)
        
        if response.status_code == 200:
            return True
        else:
            self._bot_log("Bot sanity was not 200 OK, instead got: {}".format(response.status_code), log_level=LogLevel.ERROR)
            return False
    
    def send_question(self, question, question_id, expected_answer):
        url = "http://{0}/question".format(self.address)
        try:
            response = requests.post(
                url=url,
                json=question,
                timeout=60,
            )
        except requests.exceptions.Timeout:
            self._bot_log("question request timed out.", log_level=LogLevel.ERROR)
            return (self.team_name, None)
        except requests.exceptions.ConnectionError:
            self._bot_log("Error connecting to bot, possible server not started or disconnected.", log_level=LogLevel.ERROR)
            return (self.team_name, None)
        except Exception as exception:
            self._bot_log("An exception occured in the request: ", log_level=LogLevel.ERROR)
            print(exception)
            return (self.team_name, None)
        else:
            question_answer = response.json()["answer"]
            if question_answer is not None and response.status_code == 200:
                self.log_csv_answer(question_id, expected_answer, question_answer)
                return (self.team_name, question_answer)
            else:
                self._bot_log("No answer in body or wrong status code.", log_level=LogLevel.ERROR)
                return (self.team_name, None)

    def log_csv_answer(self, question_id, expected_answer, answer):
        f = open(self.answer_csv_file_path, "a")
        f.write("{},{},{}\n".format(question_id, expected_answer, answer))
        f.close()


# Class representing a test instance.
class TestInstance:
    def __init__(self, args, outputs_path):
        self.logger = EOLogger()
        self.test_bots_file_path = args.test_bots
        self.question_set_file_path = args.question_set
        self.bots = []
        self.current_question_index = 0
        self.answers = []
        self.outputs_path = outputs_path
        self.test_instance_outputs_path = os.path.join(
            self.outputs_path,
            "test_{}".format(self._build_folder_name())
        )
        
        if not os.path.isdir(self.test_instance_outputs_path):
            os.mkdir(self.test_instance_outputs_path)

        self._read_resources()
        self._create_bots()

    def _build_folder_name(self):
        now = datetime.now()
        return "{}_{}_{}_{}_{}_{}".format(
            now.hour,
            now.minute,
            now.second,
            now.day,
            now.month,
            now.year,
        )

    def _read_resources(self):
        if not os.path.exists(self.test_bots_file_path):
            self.logger.log(
                "Could not find tests_bots file at path: {}".format((self.test_bots_file_path)),
                log_level=LogLevel.ERROR
            )
            exit(1)
        else:
            
            with open(self.test_bots_file_path, "r") as f:
                self.team_bots_data = json.load(f)

        if not os.path.exists(self.question_set_file_path):
            self.logger.log(
                "Could not find question_set file at path: {}".format((self.question_set_file_path)),
                log_level=LogLevel.ERROR
            )
            exit(1)
        else:
            
            with open(self.question_set_file_path, "r") as f:
                question_data = json.load(f)
                self.question_set = question_data["questions"]

    def _create_bots(self):
        all_bots = self.team_bots_data["bots"]
        for bot in all_bots:
            self.bots.append(
                CompetitionBot(
                    team_name=bot["team_name"],
                    address=bot["address"],
                    logger=self.logger,
                    dir_to_write=self.test_instance_outputs_path,
                )
            )

    def send_all_questions(self):
        for question_instance in self.question_set:
            question_id = question_instance["question_id"]
            expected_answer = question_instance["answer"]
            question_contents = question_instance["question"]
            self.logger.log(message="---- Question {} ----".format(question_id))
            for bot in self.bots:
                bot.send_question(question_contents, question_id, expected_answer)

def add_arguments(argument_parser: argparse.ArgumentParser):
    argument_parser.add_argument("--test-bots",action="store", help="Path to the json file containing all the bots included in this test.", required=True)
    argument_parser.add_argument("--question-set", action="store", help="Path to the json file containing all the questions", required=True)
    return argument_parser.parse_args()

def main():
    print("Hello EESTEC Olympics!")
    argument_parser = argparse.ArgumentParser()
    args = add_arguments(argument_parser)
    current_dir_path = sys.path[0]
    # Check if outputs directory exists
    outputs_path = os.path.join(current_dir_path, "outputs")
    if not os.path.isdir(outputs_path):
        os.mkdir(outputs_path)
    
    test_instance = TestInstance(args, outputs_path)
    test_instance.send_all_questions()

if __name__ == "__main__":
    main()
