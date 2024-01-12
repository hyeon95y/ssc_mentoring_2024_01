from pathlib import Path

PROJECT_PATH = Path(__file__).parent.parent
DATA_PATH = PROJECT_PATH / "data"
ARTIFACTS_ROOT = DATA_PATH / "artifacts"
CACHED_PATH = DATA_PATH / "cached"
SRC_PATH = PROJECT_PATH / "src"
TEST_PATH = PROJECT_PATH / "test"
REQUIREMENTS_PATH = PROJECT_PATH / "requirements.txt"
PREDICTIONS_PATH = DATA_PATH / "predictions"
FIGURES_PATH = DATA_PATH / "figures"
