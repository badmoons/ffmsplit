"""
Provide a source audio/video file and a `timestamp.txt` file with timestamps.
Timestamps are read line by line.
Timestamps may need to be edited to fit the scripts
"""

import sys, subprocess
from typing import List

argsCount = 3

def printUsage():
    print("Usage:")
    print("     $ python3 ffmsplit.py <audio_source_file> <timestamps_file> <genre>\n")
    print("Timespamps format example:")
    print("           00:00 - Long Artist_name - Some silly song name")
    print("           01:12 - artist15 - Track 2")
    print("           ... ")
    print("           02:32:54 - End.")


if len(sys.argv) < argsCount:
    print("ERROR: Not enough arguments. Expected", argsCount-1, "args, recived", len(sys.argv)-1, file=sys.stderr)
    printUsage();
    sys.exit(1)

if len(sys.argv) > argsCount+1:
    printUsage();
    sys.exit("ERROR: Too many argumetns i guess")

sourceName = sys.argv[1] # Name of the input media file
timestamps = sys.argv[2] # file with timestamps
genreName  = sys.argv[3]

startTime = []
endtime = list[int]

albumName = sourceName.lstrip("./.\\") # try to remove .\ or ./ at the start of the file name
albumName = albumName.rsplit(".",1)[0]

titleName  = []
artistName = []
resultName = []



def get_length(filename):
    """Get the lentgh of the audio file and convert it
    into a formatted timecode string (1:23:23). This function should not exit as it is only used once, but I copy pasted from stack overflow, so I don't care really."""
    # FIXME: if the file is >9 hours long, it will probably break stuff
    length = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)

    t = float(length.stdout) # source duration
    hours   = int(t // 3600)
    minutes = int((t % 3600) // 60)
    seconds = int((t % 3600) % 60)
    result = f"{hours}:{minutes:02}:{seconds:02}"
    return result

def tcode_to_int(tcode):
    """Converts time code (like 23:23) to seconds"""
    t = tcode.split(':')
    if len(t) == 3:
        result = (float(t[0]) * 3600) + (float(t[1]) * 60) + float(t[2])
    if len(t) == 2:
        result = (float(t[0]) * 60) + float(t[1])
    return int(result)

sourceDuration = get_length(sourceName)
# print("INFO:",sourceDuration)


lineNumber = 0
with open(timestamps, 'r', encoding="utf-8") as f:
    for line in f:
        startTime.append(line.split()[0]) # Starting timestamp, from which file would be cut

        artistName.append(line.split(" - ")[1])
        titleName.append(line.split(" - ")[2].rstrip())
        resultName.append(" ".join(line.split()[2:])) # Name of the resulting file, produced by ffmpeg
        
        lineNumber += 1

        # print("/------------------------------------------/")
        # print("INFO: Artist:", artistName)
        # print("INFO: Title:", titleName)        
        # print("INFO:",line.split()[0])
        # print("INFO:",line.split())

i = 0
while i < lineNumber:
    # print("INFO: Line (track) number:",i)
    if i != lineNumber-1:
        endTime = startTime[i+1]
    elif i == lineNumber-1:
        endTime = sourceDuration

    trackLength = str(tcode_to_int(endTime) - tcode_to_int(startTime[i]))
    FfmpegCommand = ['ffmpeg', '-hide_banner',\
                     '-ss', startTime[i], '-i', sourceName,\
                     '-to', trackLength, '-c', 'copy',\
                     '-metadata', f'title={titleName[i]}',\
                     '-metadata', f'artist={artistName[i]}',\
                     '-metadata', f'genre={genreName}',\
                     '-metadata', f'album={albumName}',\
                     f'{resultName[i]}.opus']

    # print("------------------------------------------")
    # print("INFO: Resulting ffmpeg command:", FfmpegCommand)
    # print("INFO: Resulting File Name:", f"{resultName[i]}.opus")
    subprocess.run(FfmpegCommand)
    i += 1
