import os
import yaml
import logging
from typing import List

from medperf.ui import UI
from medperf import config
from medperf.comms import Comms
from medperf.utils import storage_path, approval_prompt, dict_pretty_print, results_ids


class Result:
    """
    Class representing a Result entry

    Results are obtained after successfully running a benchmark
    execution flow. They contain information regarding the 
    components involved in obtaining metrics results, as well as the
    results themselves. This class provides methods for working with
    benchmark results and how to upload them to the backend.
    """

    def __init__(
        self, result_path: str, benchmark_uid: str, dataset_uid: str, model_uid: str,
    ):
        """Creates a new result instance

        Args:
            result_path (str): Location of the reuslts.yaml file.
            benchmark_uid (str): UID of the executed benchmark.
            dataset_uid (str): UID of the dataset used.
            model_uid (str): UID of the model used.
        """
        self.path = result_path
        self.benchmark_uid = benchmark_uid
        self.dataset_uid = dataset_uid
        self.model_uid = model_uid
        self.status = "PENDING"
        self.results = {}
        self.get_results()
        self.uid = self.results.get("uid", None)

    @classmethod
    def all(cls, ui: UI) -> List["Result"]:
        """Gets and creates instances of all the 
        """
        logging.info("Retrieving all results")
        results_ids_tuple = results_ids(ui)
        results_storage = storage_path(config.results_storage)
        results = []
        for result_ids in results_ids_tuple:
            b_id, m_id, d_id = result_ids
            results_file = os.path.join(
                results_storage, b_id, m_id, d_id, config.results_filename
            )
            results.append(cls(results_file, b_id, d_id, m_id))

        return results

    def todict(self):
        with open(self.path, "r") as f:
            results = yaml.safe_load(f)

        result_dict = {
            "name": f"{self.benchmark_uid}_{self.model_uid}_{self.dataset_uid}",
            "results": results,
            "metadata": {},
            "approval_status": self.status,
            "benchmark": self.benchmark_uid,
            "model": self.model_uid,
            "dataset": self.dataset_uid,
        }
        return result_dict

    def request_approval(self, ui: UI) -> bool:
        """Prompts the user for approval concerning uploading the results to the comms

        Returns:
            bool: Wether the user gave consent or not
        """
        if self.status == "APPROVED":
            return True

        dict_pretty_print(self.todict(), ui)
        ui.print("Above are the results generated by the model")

        approved = approval_prompt(
            "Do you approve uploading the presented results to the MLCommons comms? [Y/n]",
            ui,
        )

        return approved

    def upload(self, comms: Comms):
        """Uploads the results to the comms

        Args:
            comms (Comms): Instance of the communications interface.
        """
        result_uid = comms.upload_results(self.todict())
        self.uid = result_uid
        self.results["uid"] = result_uid
        self.set_results()

    def set_results(self):
        write_access = os.access(self.path, os.W_OK)
        logging.debug(f"file has write access? {write_access}")
        if not write_access:
            logging.debug(f"removing outdated and inaccessible results")
            os.remove(self.path)
        with open(self.path, "w") as f:
            yaml.dump(self.results, f)

    def get_results(self):
        with open(self.path, "r") as f:
            self.results = yaml.safe_load(f)
