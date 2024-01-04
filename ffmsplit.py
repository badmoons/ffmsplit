"""
Provide a source audio/video file and a `timestamp.txt` file with timestamps.
Timestamps are read line by line.
Timestamps may need to be edited to fit the scripts
"""

import sys, subprocess

argsCount = 2

if len(sys.argv) < argsCount:
    print("ERROR: Not enough arguments. Expected", argsCount-1, "args, recived", len(sys.argv)-1, file=sys.stderr)
    sys.exit(1)

if len(sys.argv) > argsCount+1:
    sys.exit("Too many argumetns i guess");

sourceName = sys.argv[1] # Name of the input media file
timestamps = sys.argv[2] # File with timestamps

startTime = []
endTime = []
resultName = []


def get_length(filename):
    """Get the lentgh of the audio file and convert it
    into a formatted timecode string (1:23:23)"""
    # INFO: if the file is >9 hours long, it will probably break stuff
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
print(sourceDuration)


with open(timestamps, 'r', encoding="utf-8") as f:
    for line in f:
        startTime.append(line.split()[0]) # Starting timestamp, from which file would be cut
        resultName.append(" ".join(line.split()[2:])) # sys.argv[4] # Name of the resulting file, produced by ffmpeg
        lineNumber += 1

        print("------------------------------------------")
        print(lineNumber)
        print(line.split()[0])
        print(line.split())

i = 0
while i < lineNumber:
    print(i)
    if i != lineNumber-1:
        endTime = startTime[i+1]
    elif i == lineNumber-1:
        endTime = sourceDuration

    trackLength = str(tcode_to_int(endTime) - tcode_to_int(startTime[i])) 
    FfmpegCommand = ["ffmpeg",\
                     "-ss", startTime[i], "-i", sourceName,\
                     "-to", trackLength, "-c", "copy", f"{resultName[i]}.opus"]

    print("------------------------------------------")    
    print("Resulting ffmpeg command:", FfmpegCommand)
    print("Everything after timestamps:", f"{resultName[i]}.opus")
    subprocess.run(FfmpegCommand)
    i += 1

# TODO: Remove unnecessary stuff,
# TODO: check if thacks are correct length,
# TODO: do proper description
# TODO: fix filepaths
# TODO: examples
