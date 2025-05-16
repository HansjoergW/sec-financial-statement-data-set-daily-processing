from secdaily.SecDaily import Configuration, SecDailyOrchestrator

if __name__ == "__main__":
    workdir_default = "d:/secprocessing2/"

    configuration = Configuration(workdir=workdir_default)

    orchestrator = SecDailyOrchestrator(configuration=configuration)

    orchestrator.process(start_year=2024, start_qrtr=4)
