#!/usr/bin/python

'''
    Copyright 2009, The Android Open Source Project

    Licensed under the Apache License, Version 2.0 (the "License"); 
    you may not use this file except in compliance with the License. 
    You may obtain a copy of the License at 

        http://www.apache.org/licenses/LICENSE-2.0 

    Unless required by applicable law or agreed to in writing, software 
    distributed under the License is distributed on an "AS IS" BASIS, 
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. 
    See the License for the specific language governing permissions and 
    limitations under the License.
'''

# script to highlight adb logcat output for console
# written by jeff sharkey, http://jsharkey.org/
# piping detection and popen() added by other android team members
# filter by Android package name added by Guillaume BOUERAT, https://github.com/GBouerat

import os, sys, getopt, re
import fcntl, termios, struct

try:
    import StringIO         # Python2
except:
    from io import StringIO # Python3

# unpack the current terminal width/height
data = fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, '1234')
HEIGHT, WIDTH = struct.unpack('hh',data)

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

def format(fg=None, bg=None, bright=False, bold=False, dim=False, reset=False):
    # manually derived from http://en.wikipedia.org/wiki/ANSI_escape_code#Codes
    codes = []
    if reset: codes.append("0")
    else:
        if not fg is None: codes.append("3%d" % (fg))
        if not bg is None:
            if not bright: codes.append("4%d" % (bg))
            else: codes.append("10%d" % (bg))
        if bold: codes.append("1")
        elif dim: codes.append("2")
        else: codes.append("22")
    return "\033[%sm" % (";".join(codes))


def indent_wrap(message, indent=0, width=80):
    wrap_area = width - indent
    messagebuf = StringIO.StringIO()
    current = 0
    while current < len(message):
        next = min(current + wrap_area, len(message))
        messagebuf.write(message[current:next])
        if next < len(message):
            messagebuf.write("\n%s" % (" " * indent))
        current = next
    return messagebuf.getvalue()


LAST_USED = [RED,GREEN,YELLOW,BLUE,MAGENTA,CYAN,WHITE]
KNOWN_TAGS = {
    "dalvikvm": BLUE,
    "Process": BLUE,
    "ActivityManager": CYAN,
    "ActivityThread": CYAN,
}

def allocate_color(tag):
    # this will allocate a unique format for the given tag
    # since we dont have very many colors, we always keep track of the LRU
    if not tag in KNOWN_TAGS:
        KNOWN_TAGS[tag] = LAST_USED[0]
    color = KNOWN_TAGS[tag]
    LAST_USED.remove(color)
    LAST_USED.append(color)
    return color

VERSION = "1.4"

def version():
    print("Colored Logcat PID version " + VERSION)
    print("https://github.com/GBouerat/ColoredLogcatPID")

def usage():
    version()
    print
    print("Usage : coloredlogcatpid.py -p com.example.name")
    print("   or : coloredlogcatpid.py -x tagname")
    print("   or : coloredlogcatpid.py -x tagname1 -x tagname2 ...")
    print("   or : adb logcat | coloredlogcatpid.py -p com.example.name")
    print("   or : adb logcat | coloredlogcatpid.py -p com.example.name -x tagname1")
    print("   or : adb logcat | coloredlogcatpid.py -p com.example.name -x tagname1 -x tagname2 ...")
    print
    print("Arguments :")
    print("  -d  or  --device    : see adb -d")
    print("  -e  or  --emulator  : see adb -e")
    print("  -s  or  --serial    : see adb -s")
    print("  -x  or  --exclude   : Exclude tag from logcat (you can exclude several tags)")
    print("  -p  or  --package   : Filter by Android package name")
    print("  -h  or  --help      : Print Help (this message) and exit")
    print("  -v  or  --version   : Print version and exit")

RULES = {
    #re.compile(r"([\w\.@]+)=([\w\.@]+)"): r"%s\1%s=%s\2%s" % (format(fg=BLUE), format(fg=GREEN), format(fg=BLUE), format(reset=True)),
}

TAGTYPE_WIDTH = 3
TAG_WIDTH = 20
PROCESS_WIDTH = 7 # 8 or -1
HEADER_SIZE = TAGTYPE_WIDTH + 1 + TAG_WIDTH + 1 + PROCESS_WIDTH + 1

TAGTYPES = {
    "V": "%s%s%s " % (format(fg=WHITE, bg=BLACK),   "V".center(TAGTYPE_WIDTH), format(reset=True)),
    "D": "%s%s%s " % (format(fg=BLACK, bg=BLUE),    "D".center(TAGTYPE_WIDTH), format(reset=True)),
    "I": "%s%s%s " % (format(fg=BLACK, bg=GREEN),   "I".center(TAGTYPE_WIDTH), format(reset=True)),
    "W": "%s%s%s " % (format(fg=BLACK, bg=YELLOW),  "W".center(TAGTYPE_WIDTH), format(reset=True)),
    "E": "%s%s%s " % (format(fg=BLACK, bg=RED),     "E".center(TAGTYPE_WIDTH), format(reset=True)),
}

pid = "-1"
package = None
exclude = None
adb_args = None

argv = sys.argv[1:]
try:
    opts, args = getopt.getopt(argv, "hvp:x:s:de", ["help", "version", "package=", "exclude=", "serial=", "device", "emulator"])
except (getopt.GetoptError, err):
    print(str(err))
    print
    usage()
    sys.exit(2)
for opt, arg in opts:
    if opt in ("-h", "--help"):
        usage()
        sys.exit()
    elif opt in ("-v", "--version"):
        version()
        sys.exit()
    elif opt in ("-p", "--package"):
        if arg is None:
            usage()
            sys.exit()
        package = arg
    elif opt in ("-s", "--serial"):
        if arg is None:
            usage()
            sys.exit()
        adb_args = '-s ' + arg
    elif opt in ("-d", "--device"):
        adb_args = '-d'
    elif opt in ("-e", "--emulator"):
        adb_args = '-e'
    elif opt in ("-x", "--exclude"):
        if not arg is None:
            if exclude is None:
                exclude = [arg]
            else:
                exclude.append(arg)

# if someone is piping in to us, use stdin as input.  if not, invoke adb logcat
if os.isatty(sys.stdin.fileno()):
    if adb_args is None:
        input = os.popen("adb logcat")
    else:
        input = os.popen("adb %s logcat" % adb_args)
else:
    input = sys.stdin

if not package is None:
    repid = re.compile("^Start proc " + package + " for .*pid=([0-9]+).*$")

retag = re.compile("^([A-Z])/(.*)\(([ 0-9]{5})\): (.*)$")

while True:
    try:
        line = input.readline()
    except KeyboardInterrupt:
        break

    match = retag.match(line)

    if not match is None:
        tagtype, tag, owner, message = match.groups()

        if not package is None:
            if tag == "ActivityManager":
                matchpid = repid.match(message)
                if not matchpid is None:
                    pid = matchpid.group(1)
                elif message.find(package) == -1:
                    continue
            elif not owner.strip() == pid:
                if message.find(package) == -1:
                    continue

        if not exclude is None:
            if tag.strip() in exclude:
                continue

        linebuf = StringIO.StringIO()

        # center process info
        if PROCESS_WIDTH > 0:
            owner = owner.strip().center(PROCESS_WIDTH)
            linebuf.write("%s%s%s " % (format(fg=BLACK, bg=BLACK, bright=True), owner, format(reset=True)))

        # right-align tag title and allocate color if needed
        tag = tag.strip()
        color = allocate_color(tag)
        tag = tag[-TAG_WIDTH:].rjust(TAG_WIDTH)
        linebuf.write("%s%s %s" % (format(fg=color, dim=False), tag, format(reset=True)))

        # write out tagtype colored edge
        if not tagtype in TAGTYPES: break
        linebuf.write(TAGTYPES[tagtype])

        # insert line wrapping as needed
        message = indent_wrap(message, HEADER_SIZE, WIDTH)

        # format tag message using rules
        for matcher in RULES:
            replace = RULES[matcher]
            message = matcher.sub(replace, message)

        linebuf.write(message)
        line = linebuf.getvalue()

    print(line)
    if len(line) == 0: break

