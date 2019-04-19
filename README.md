# Coursera Dump

The app "Coursers Dump" takes a few random courses from [coursera.org](www.coursera.org) and pushes them to Excel file.
By default, amount of random courses is _20_ and name of Excel file to save is _courses.xlsx_.
The file will be saved to the app folder. You may change this options before the app starts.

# How to Install

Python 3.5 should be already installed. Then use pip (or pip3 if there is a conflict with old Python 2 setup) to install dependencies:

```bash
$ pip install -r requirements.txt # alternatively try pip3
```

# Quickstart

To use run the app from command line. By default, 20 random courses info will be safed to _courses.xlsx_.
To change default values use options _--amount_ and _--path_ (or short ones _-a_ and _-p_)

```bash
$ python coursera.py --amount 30 --path my_courses.xlsx
30 courses have been safed to my_courses.xlsx
```

# Project Goals

The code is written for educational purposes. Training course for web-developers - [DEVMAN.org](https://devman.org)
