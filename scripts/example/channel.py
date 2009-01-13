'''Hello World Example'''

if 'hello' in msg:
    irc.msg(channel, 'Hello, World (and %s)!' % sender)

# Persistent counter
if 'counter' not in locals():
    counter = 0
else:
    counter += 1

if argv[0] == ".count":
    irc.msg(channel, ("%d events have happened since I've joined "
                      "or since this script has been modified!") % counter)
