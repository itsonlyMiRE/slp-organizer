# slp-organizer
## Description
Organize your thousands of .slp files into subfolders based on date, match outcome, user character, or opponent character. Retrieves this data using [py-slippi](https://github.com/hohav/py-slippi). I'm not claiming it's a super useful application; I just wanted to get my feet wet with parsing .slp replay data. See Notes section for more info.

## Setup
The program is written in Python3. The only third-party dependency can be installed with ``pip install py-slippi``.

## Usage
Run the program, and follow the instructions it prints.

## Notes
Now compatible for both Linux and Windows. It's a bit of a resource hog and will probably push your CPU to 100% utilization. But, it's not unbearably slow, really depends on your CPU (some of my tests returned ~2176 files/minute, ~36.26 files/second on my Ryzen 5 3600X, 6 cores 12 threads).
