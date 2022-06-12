:start
cls

set "REQUIREMENTS_DIRECTORY=%cd:\=/%"
echo "%cd%"
echo "REQUIREMENTS_DIRECTORY=%REQUIREMENTS_DIRECTORY%"

:: python get-pip.py

.\env\Scripts\python -m pip install --upgrade pip

.\env\Scripts\python -m pip install -r ./requirements.txt
