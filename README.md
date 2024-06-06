# MManager

## This project is a desktop python app to manage malwares source code and connections

### This app is only for educational propouses. I'm not responsible for the bad or harmful use you give to all the information provided within this project, so use at your own risk!


# Requirements
Windows 10 or newer

Python >= 3.12 (I didn't tested other versions)

MinGW GCC

# Optional
WSL - Ubuntu (only to use the compiler for linux)


# Install
```
git clone https://github.com/MaaSantos45/mmanager.git
cd mmanager
python -m venv venv
.\venv\Scripts\activate
pip install .
```

# Run main code
```
python .\main\client\client.py
```

# Build the .EXE
***After the installation. On root project directory ( mmanager/ )***
```
python .\main\build.py [<output name>]
```
Output name is optional [Default: client]
