import subprocess


class Terraform:
    def __init__(self, work_dir):
        self.work_dir = work_dir

    def init(self, backend_config, variables):
        return subprocess.check_call(
            [
                "terraform",
                "init",
                f"--backend-config={backend_config}",
                f"--var-file={variables}",
            ],
            cwd=self.work_dir,
        )

    def plan(self, variables):
        return subprocess.check_call(
            [
                "terraform",
                "plan",
                f"--var-file={variables}",
            ],
            cwd=self.work_dir,
        )

    def apply(self, variables):
        return subprocess.check_call(
        [
            "terraform",
            "apply",
            f"--var-file={variables}",
            "--auto-approve"
        ],
        cwd=self.work_dir,
    )