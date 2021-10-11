# slp-organizer
## Description
Organize your thousands of .slp files into subfolders based on date, match outcome, user character, or opponent character. I'm not claiming it's a super useful application; I just wanted to get my feet wet with parsing .slp replay data. See Notes section for more info.

## Setup
The program is written in Python3. The only third-party dependency can be installed with ``pip install py-slippi``.

## Usage
Run the program, and follow the instructions it prints.

## Notes
It's a bit of a resource hog and will probably push your CPU to 100% utilization. But, it's decently fast (~2176 files/minute, ~36.26 files/second). Also, use this in a controlled environment! In the state it's in now, I would advise you don't feed it the wrong path to your .slp files, because it will completely change the folder system of whatever directory you input. I will probably change that to make it a little more forgiving and less destructive.