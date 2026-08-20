from scripts.check_task_dependencies import pip_dependencies


def test_pip_dependencies_ignores_requirement_file():
    instruction = "RUN pip install -r requirements.lock"

    assert pip_dependencies(instruction) == []


def test_pip_dependencies_ignores_absolute_requirement_file():
    instruction = "RUN pip install -r /tmp/requirements.txt"

    assert pip_dependencies(instruction) == []


def test_pip_dependencies_returns_pinned_packages():
    instruction = "RUN pip install numpy==2.0.0 scipy==1.14.0"

    assert pip_dependencies(instruction) == [
        "numpy==2.0.0",
        "scipy==1.14.0",
    ]


def test_pip_dependencies_returns_unpinned_package():
    instruction = "RUN pip install numpy"

    assert pip_dependencies(instruction) == ["numpy"]


def test_pip_dependencies_ignores_constraint_files():
    instruction = (
        "RUN pip install "
        "-c constraints.txt "
        "--requirement requirements.txt"
    )

    assert pip_dependencies(instruction) == []
