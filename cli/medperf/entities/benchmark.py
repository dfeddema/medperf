from typing import List

from medperf.comms import Comms


class Benchmark:
    """
    Class representing a Benchmark

    a benchmark is a bundle of assets that enables quantitative 
    measurement of the performance of AI models for a specific 
    clinical problem. A Benchmark instance contains information
    regarding how to prepare datasets for execution, as well as
    what models to run and how to evaluate them.
    """

    def __init__(self, uid: str, benchmark_dict: dict):
        """Creates a new benchmark instance

        Args:
            uid (str): The benchmark UID
            benchmark_dict (dict): key-value representation of the benchmark.
        """
        self.uid = uid
        self.name = benchmark_dict["name"]
        self.description = benchmark_dict["description"]
        self.docs_url = benchmark_dict["docs_url"]
        self.created_at = benchmark_dict["created_at"]
        self.modified_at = benchmark_dict["modified_at"]
        self.owner = benchmark_dict["owner"]
        self.data_preparation = benchmark_dict["data_preparation_mlcube"]
        self.reference_model = benchmark_dict["reference_model_mlcube"]
        self.models = benchmark_dict["models"]
        self.evaluator = benchmark_dict["data_evaluator_mlcube"]

    @classmethod
    def get(cls, benchmark_uid: str, comms: Comms) -> "Benchmark":
        """Retrieves and creates a Benchmark instance from the server

        Args:
            benchmark_uid (str): UID of the benchmark.
            comms (Comms): Instance of a communication interface.

        Returns:
            Benchmark: a Benchmark instance with the retrieved data.
        """
        benchmark_dict = comms.get_benchmark(benchmark_uid)
        ref_model = benchmark_dict["reference_model_mlcube"]
        add_models = cls.get_models_uids(benchmark_uid, comms)
        benchmark_dict["models"] = [ref_model] + add_models
        return cls(benchmark_uid, benchmark_dict)

    @classmethod
    def get_models_uids(cls, benchmark_uid: str, comms: Comms) -> List[str]:
        """Retrieves the list of models associated to the benchmark

        Args:
            benchmark_uid (str): UID of the benchmark.
            comms (Comms): Instance of the communications interface.

        Returns:
            List[str]: List of mlcube uids
        """
        return comms.get_benchmark_models(benchmark_uid)
