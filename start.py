import os

application_root = os.path.abspath(".")
python_root = os.path.join(application_root, "Python")
python_packages = os.path.join(python_root, "Lib", "site-packages")
os.environ["PYTHONPATH"] = python_root
os.system("{}/python.exe ./Application/app.py".format(python_root))
