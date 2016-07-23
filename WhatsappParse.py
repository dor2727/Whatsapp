import re

USERMESSAGE_FORMAT = '\d{2}/\d{2}/\d{4}, \d{2}:\d{2} - (.*?)\:'
SYSMESSAGE_FORMAT = '\d{2}/\d{2}/\d{4}, \d{2}:\d{2} - ([^:]*?)$'


def parse_line(line):
    """
    Reads a single line of text and separates its parts.

    Args:
        line (string): A line of text from an archived Whatsapp chat.
    Returns:
        tuple: (date, user, message)
    """

    time, rest = line.split('-', 1)
    
    if ':' in rest:
      user, message = rest.split(':', 1)
    else:
      user = 'system'
      message = rest

    time = time.strip()
    user = user.strip()
    message = message.strip()
    return time, user, message


def parse_convo(text):
    """
    Parse a chunk of conversation text to get messages.

    Args:
        text (string): Text to parse in the format of a Whatsapp archived chat.
    Returns:
        list: A list of messages represented in tuples.
    """
    text = text.strip()

    messages = list()
    for line in text.split('\n'):
        # Skip system messages
        if re.match(USERMESSAGE_FORMAT, line):
            messages.append(parse_line(line))

    return messages
    
def parse_sysmsg(text):
    """
    Parse a chunk of conversation text to get system messages.

    Args:
        text (string): Text to parse in the format of a Whatsapp archived chat.
    Returns:
        list: A list of system messages represented in tuples.
    """
    text = text.strip()

    messages = list()
    for line in text.split('\n'):
        # Find system messages
        if re.match(SYSMESSAGE_FORMAT, line):
            messages.append(parse_line(line))

    return messages
  

