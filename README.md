# Colored Logcat PID

Colored Logcat PID is a fork of [Jeff Sharkey Colored Logcat](http://jsharkey.org/blog/2009/04/22/modifying-the-android-logcat-stream-for-full-color-debugging/) python script which "reformats the logcat output into a colorful stream".

Colored Logcat PID adding filter by Android name package.

Last version : 1.3 (jan 19, 2013)

## How to use it :
make it executable :

    $ chmod +x coloredlogcatpid.py 

launch it :

    $ coloredlogcatpid.py -p com.example.name
or

    $ adb logcat | coloredlogcatpid.py -p com.example.name

## Options :

    -e  or  --exclude  : Exclude tag from logcat (you can exclude several tags)
    -p  or  --package  : Filter by Android package name
    -h  or  --help     : Print Help (this message) and exit
    -v  or  --version  : Print version and exit

## Screenshot :

![coloredlogcatpid.py](https://bitbucket.org/GBouerat/colored-logcat-pid/raw/ca882f7a8af2/Colored%20Logcat%20PID.png)

## Change Log :

  - v1.3 : Fix bug with bluetooth log and show log from other pid containing package name
  - v1.2 : Add tag exclusion
  - v1.1 : Fix bug on linux

## Contact :

You can find me on [Google+](https://plus.google.com/u/0/112136052387869387989), [Twitter](https://twitter.com/GBouerat) and [GitHub](https://github.com/GBouerat).