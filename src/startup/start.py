# isort:maintain_block
import sys  # isort: skip
from pathlib import Path  # isort: skip
import os  # isort: skip

PATH_PROJECT_FOLDER_EC2 = "/home/ubuntu/jnj/demand_forecasting"  # NOQA: E402

if os.path.exists(PATH_PROJECT_FOLDER_EC2):  # NOQA: E402
    path_project_folder = PATH_PROJECT_FOLDER_EC2  # NOQA: E402
else:  # NOQA: E402
    raise FileNotFoundError("path_project_folder not found")  # NOQA: E402

PROJECT_PATH = Path(path_project_folder)  # NOQA: E402
SRC_PATH = PROJECT_PATH / "src"  # NOQA: E402
REQUIREMENTS_PATH = PROJECT_PATH / "requirements.txt"  # NOQA: E402

sys.path.append(str(SRC_PATH))  # NOQA: E402
# isort:end_maintain_block

# isort:imports-stdlib
import sys
import warnings
from pathlib import Path

# isort:imports-thirdparty
import matplotlib.pyplot as plt
import pandas as pd
from IPython import get_ipython

# isort:import-localfolder


# isort:imports-firstparty
from utils import check_package_versions, check_python_version


# plt.style.use('ggplot')

# Set font family for Korean
try:
    path = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"
    fontprop = fm.FontProperties(fname=path, size=18)
    plt.rcParams["font.family"] = "NanumGothic"
except:
    pass

INSTALL_MISSING_PACKAGES = False

# Check python version
python_version_passed = check_python_version()

# Check package versions
package_versions_passed = check_package_versions()
if package_versions_passed is False:
    if INSTALL_MISSING_PACKAGES is True:
        cmd = (
            "cat "
            + str(REQUIREMENTS_PATH)
            + r" | sed -e '/^\s*#.$$/d' -e '/^\s$$/d' | xargs -n 1 python3 -m pip install"
        )
        os.system(cmd)
        package_versions_passed = check_package_versions()
    else:
        pass

# Pandas options
pd.options.display.max_columns = 30
pd.options.display.max_rows = 20
pd.set_option("display.float_format", lambda x: "%.3f" % x)

# Filter warning
warnings.filterwarnings("ignore")


try:
    ipython = get_ipython()
    # If in ipython, load autoreload extension
    if "ipython" in globals():
        print("\nWelcome to IPython!")
        ipython.magic("load_ext autoreload")
        ipython.magic("autoreload 2")

except:
    pass

STARTUP_SCRIPT_DONE = True
