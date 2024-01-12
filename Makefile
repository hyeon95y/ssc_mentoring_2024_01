#
# Variables
#
TARGET_DIRECTORY_NOTEBOOKS = notebooks
TARGET_DIRECTORY_PY = src test
TARGET_DIRECTORY_DATA = data/experiment_config/*.yaml data/notebook_header.md
TARGET_DIRECTORY_CONFIGURATION = README.md .coveragerc .envrc pytest.ini Makefile requirements.txt requirements_unlisted.txt requirements_listed.txt setup.sh Dockerfile startup_sagemaker.sh

PACKAGE_NAMES_CODE_FORMATTER = pipreqs pip-tools isort black autopep8 autoflake pyupgrade-directories nbqa monkeytype
PACKAGE_NAMES_PYTEST_PLUGINS = pytest pytest-sugar pytest-icdiff pytest-html pytest-timeout pytest-cov pytest-xdist pytest-timeout pytest-monkeytype
PACKAGE_NAMES_DOCUMENTATION = interrogate flake8-html genbadge

help: ## Show this help
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

#
# Find, replacing text
#

find: ## Find given string
	grep -Rn '$(str)' $(dir)

find_replace: ## Find and replace given string
	sed -i 's/$(str1)/$(str2)/g' $(dir)/**/*.py

find_replace_filepath: ## Find and replace given string
	sed -i 's/$(str1)/$(str2)/g' $(dir)
	
#
# Setup
#

setup: ## Install python packages
	$(MAKE) setup_aws
	$(MAKE) setup_code_formatter
	$(MAKE) setup_pytest
	$(MAKE) setup_documentation
	$(MAKE) setup_startup_script
	pip3 install --upgrade setuptools
	cat requirements.txt | sed -e '/^\s*#.$$/d' -e '/^\s$$/d' | xargs -n 1 python3 -m pip install

setup_aws: ## Install awscli
	pip3 install awscli

setup_code_formatter: ## Install python code formatter
	pip3 install $(PACKAGE_NAMES_CODE_FORMATTER)

setup_pytest: ## Install pytest and related packages
	pip3 install $(PACKAGE_NAMES_PYTEST_PLUGINS)

setup_documentation: ## Install documentation related packages
	pip3 install $(PACKAGE_NAMES_DOCUMENTATION)

setup_startup_script: ## Set notebook configuration
	cp src/common/startup/start.py ~/.ipython/profile_default/startup

remove_startup_script: ## Set notebook configuration
	rm ~/.ipython/profile_default/startup/start.py

#
# Formatting code
#

format_py: ## Format python files
	isort --multi-line=3 --trailing-comma -force-grid-wrap=0 --use-parentheses --line-width=120 --float-to-top .
	black src test
	autopep8 --in-place -r .
	autoflake --in-place -r --remove-unused-variables --remove-all-unused-imports .
	pyup_dirs src test --recursive --py37-plus

format_py_dir: ## Format python files
	isort --multi-line=3 --trailing-comma -force-grid-wrap=0 --use-parentheses --line-width=120 --float-to-top $(dir)
	black $(dir)
	autopep8 --in-place -r $(dir)
	autoflake --in-place -r --remove-unused-variables --remove-all-unused-imports $(dir)
	pyup_dirs $(dir) test --recursive --py37-plus

format_nb: ## Format notebook files
	nbqa isort notebooks --multi-line=3 --trailing-comma -force-grid-wrap=0 --use-parentheses --line-width=120 --float-to-top
	nbqa black notebooks
	nbqa autopep8 notebooks --in-place -r
	nbqa autoflake notebooks --in-place -r --remove-unused-variables --remove-all-unused-imports
	nbqa pyupgrade notebooks --py37-plus

format_nb_dir: ## Format notebook files
	nbqa isort $(dir) --multi-line=3 --trailing-comma -force-grid-wrap=0 --use-parentheses --line-width=120 --float-to-top
	nbqa black $(dir)
	nbqa autopep8 $(dir) --in-place -r
	nbqa autoflake $(dir) --in-place -r --remove-unused-variables --remove-all-unused-imports
	nbqa pyupgrade $(dir) --py37-plus

generate_typehint: ## Generate typehint
	$(MAKE) test_dir_generate_monkeytype dir=$(dir) -i
	echo $(subst /,.,$(subst .py,,$(subst test_,,$(subst test/unit/,,$(dir)))))
	monkeytype stub $(subst /,.,$(subst .py,,$(subst test_,,$(subst test/unit/,,$(dir))))) --ignore-existing-annotations
	monkeytype apply $(subst /,.,$(subst .py,,$(subst test_,,$(subst test/unit/,,$(dir)))))

AUTO_DOCSTRING_PATH = '/home/ubuntu/jnj/auto_docstring/src/generator.py'

generate_docstring_postfix: ## Geneate docstring
	python3 $(AUTO_DOCSTRING_PATH) --filepath=$(filepath) --filename_postfix='_docstring' --ignore_init=False --n_jobs=1

generate_docstring: ## Geneate docstring
	python3 $(AUTO_DOCSTRING_PATH) --filepath=$(filepath) --ignore_init=False --inplace=True --n_jobs=-1

generate_docstring_n_jobs_1: ## Geneate docstring
	python3 $(AUTO_DOCSTRING_PATH) --filepath=$(filepath) --ignore_init=False --inplace=True --n_jobs=1



#
# Generating requirements.txt
#

get_requirements: ## Generate requirements.txt with pipreqs, targeting /src
	pipreqs src --force
	mv src/requirements.txt requirements_listed.txt
	echo 'scikit-learn==1.0.2' >> requirements_listed.txt
	sed -i "/scikit_learn/d" requirements_listed.txt
	sed -i "/ipython/d" requirements_listed.txt
	sed -i "/pytz/d" requirements_listed.txt
	if rm requirements.txt; then \
		echo "Removed requirements.txt (old)"; \
	else \
		echo "No requirements.txt exists"; \
	fi
	cat requirements_unlisted.txt requirements_listed.txt >> requirements.txt


#
# Docker
#

docker_clear: ## Clear all docker elements with given container_id
	sudo docker stop ${container_id}
	sudo docker rm $$(docker ps -a -q)
	sudo docker system prune -a

docker_build_and_run: ## Build docker image as test:test001 and run
	$(MAKE) git_commit commit_msg='Docker build'
	cp /home/ubuntu/.aws/config config
	cp /home/ubuntu/.aws/credentials credentials
	docker build --no-cache -t test:test001 .
	rm config credentials
	docker run -it -d test:test001

#
# Pytest
#
PYTEST_PARAMETERS_XDIST = -n auto 
PYTEST_PARAMETERS_REPORT_UNIT_TEST = --capture=tee-sys --html=test_result_unit.html --self-contained-html

test_key: ## Run test with given key/function name
	$(MAKE) clear_all_cache
	pytest -k $(key) -vv $(PYTEST_PARAMETERS_XDIST) $(PYTEST_PARAMETERS_REPORT_UNIT_TEST)

test_dir: ## Run test with given directory
	$(MAKE) clear_all_cache
	pytest $(dir) -vv $(PYTEST_PARAMETERS_XDIST) $(PYTEST_PARAMETERS_REPORT_UNIT_TEST)



#
# Documentation
#

document_coverage: ## Geneate document coverage report
	interrogate -v src

generate_readme: ## Update README.md with readme-md-generator
	rm README.md
	npx readme-md-generator -y

generate_coverage_badge: ## Generate coverage badge for README.md
	coverage report
	coverage xml
	coverage html
	mv coverage.xml reports/coverage/coverage.xml
	genbadge coverage

generate_test_badge: ## Generate test badge for README.md
	$(MAKE) test_coverage -i
	genbadge tests
	mv tests-badge.svg reports/junit/tests-badge.svg

generate_flake8_badge: ## Generate flake8 badge for README.md
	flake8 src --exit-zero --format=html --htmldir ./reports/flake8 --statistics --tee --output-file flake8stats.txt
	mv flake8stats.txt reports/flake8/flake8stats.txt
	genbadge flake8
	mv flake8-badge.svg reports/flake8/flake8-badge.svg

update_readme: ## Update README.md with updated stats
	$(MAKE) generate_coverage_badge
	$(MAKE) generate_test_badge
	$(MAKE) generate_flake8_badge

#
# Clear cache
# 

clear_all_cache: ## Clear all cache
	$(MAKE) clear_pycache
	# $(MAKE) clear_cached_data

clear_cached_data: ## Clear cached data
	if rm -r data/cached; then \
		echo "Cleared cached data"; \
	else \
		echo "No cached data exists"; \
	fi

	mkdir data/cached

clear_pycache: ## Remove all __pycache__, .ipynb_checkpoints
	find . -regex '^.*\(__pycache__\|\.py[co]\)$$' -delete
	rm -rf `find -type d -name .ipynb_checkpoints`

kill_python: ## Kill all python process
	sudo pkill -9 python

