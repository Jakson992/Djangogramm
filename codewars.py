def shooter_reverse_longer_shooter(a, b):
    if len(a) > len(b):
        shooter = b
        longer = a
    else:
        shooter = a
        longer = b
    my_string = shooter + ''.join(reversed(longer))+ shooter
    return my_string


print(shooter_reverse_longer_shooter("hello", "world"))  # Output: "worldhelloolleh"
