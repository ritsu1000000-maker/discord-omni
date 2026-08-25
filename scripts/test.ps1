$ErrorActionPreference = "Stop"
$env:PYTHONPATH = (Get-Location).Path
python -m unittest discover -s tests -v
