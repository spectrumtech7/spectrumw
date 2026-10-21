import re

JUNK_NAMES = {
    'abc', 'abcd', 'xyz', 'abc xyz', 'xyz abc', 'test', 'testing', 'tester',
    'demo', 'name', 'your name', 'none', 'na', 'nil', 'null', 'admin', 'user',
    'dummy', 'sample', 'fake', 'asdf', 'qwerty', 'unknown', 'customer', 'xxx',
}

SEQUENCES = (
    'abcdefghijklmnopqrstuvwxyz',
    'qwertyuiop', 'asdfghjkl', 'zxcvbnm',
)


def _has_sequence(text, size=4):
    for seq in SEQUENCES:
        for i in range(len(seq) - size + 1):
            window = seq[i:i + size]
            if window in text or window[::-1] in text:
                return True
    return False


def clean_name(raw):
    """Return (name, error). error is '' when the name is acceptable."""
    name = re.sub(r'\s+', ' ', (raw or '').strip())
    letters = re.sub(r'[^a-z]', '', name.lower())
    error = 'Please enter your real name (letters only, at least 3 letters).'

    if not re.fullmatch(r"[A-Za-z][A-Za-z .'\-]*", name):
        return None, error
    if len(letters) < 3:
        return None, error
    if name.lower() in JUNK_NAMES or letters in JUNK_NAMES:
        return None, error
    if not re.search(r'[aeiouy]', letters):
        return None, error
    if re.search(r'(.)\1{2,}', letters):
        return None, error
    if _has_sequence(letters):
        return None, error
    return name, ''


def clean_phone(raw):
    """Return (10-digit number, error). Format: optional +91 / 91, then 6-9 and 9 digits."""
    text = re.sub(r'[\s\-]', '', raw or '')
    match = re.fullmatch(r'(?:\+91|91)?([6-9]\d{9})', text)
    error = 'Please enter a valid 10-digit Indian mobile number.'
    if not match:
        return None, error
    number = match.group(1)

    if len(set(number)) <= 3:
        return None, error

    diffs = [int(b) - int(a) for a, b in zip(number, number[1:])]
    for step in (1, -1):
        run = 0
        for d in diffs:
            run = run + 1 if d == step else 0
            if run >= 5:
                return None, error
    return number, ''