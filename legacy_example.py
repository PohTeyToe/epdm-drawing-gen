"""
LEGACY DRAWING NUMBER GENERATOR (BEFORE MODERNIZATION)
=======================================================
This file demonstrates the "before" state of a typical EPDM backend script.
Characteristics of legacy code shown here:
  - Global mutable state
  - No type hints
  - No input validation
  - String concatenation instead of structured models
  - No error handling
  - No tests possible (tightly coupled)
  - Magic numbers and hardcoded values
  - No configuration management
  - print() for everything

DO NOT USE THIS IN PRODUCTION. See drawing_generator/ for the modernized version.
"""

# Global state — impossible to test or reset
counter_e = 0
counter_m = 0
counter_s = 0
counter_o = 0
all_drawings = []

def get_next_num(disc):
    global counter_e, counter_m, counter_s, counter_o
    if disc == "E":
        counter_e = counter_e + 1
        return counter_e
    elif disc == "M":
        counter_m = counter_m + 1
        return counter_m
    elif disc == "S":
        counter_s = counter_s + 1
        return counter_s
    elif disc == "O":
        counter_o = counter_o + 1
        return counter_o
    else:
        return -1  # Error? Who knows

def make_drawing_num(project, disc, rev):
    num = get_next_num(disc)
    if num == -1:
        print("ERROR: bad discipline")
        return None
    # String concatenation, no padding guarantee in older scripts
    result = project + "-" + disc + "-" + str(num).zfill(4) + "-" + rev
    all_drawings.append(result)
    return result

def make_revision(drawing_str):
    # Just manipulate the string directly — what could go wrong?
    parts = drawing_str.split("-")
    old_rev = parts[3]
    new_rev = chr(ord(old_rev) + 1)  # No bounds check for 'Z'
    parts[3] = new_rev
    new_drawing = "-".join(parts)
    all_drawings.append(new_drawing)
    return new_drawing

def print_all():
    print("===== ALL DRAWINGS =====")
    for d in all_drawings:
        print(d)
    print("========================")


# "Main" block that runs on import — classic legacy pattern
if __name__ == "__main__":
    print("Morgan Solar Drawing Generator v0.1")
    print("------------------------------------")

    d1 = make_drawing_num("MS", "E", "A")
    print("Created: " + str(d1))

    d2 = make_drawing_num("MS", "E", "A")
    print("Created: " + str(d2))

    d3 = make_drawing_num("MS", "M", "A")
    print("Created: " + str(d3))

    # Revise first drawing
    d1_rev = make_revision(d1)
    print("Revised: " + str(d1_rev))

    # This will silently "work" but produce garbage
    bad = make_drawing_num("MS", "X", "A")
    print("Bad result: " + str(bad))  # None — no real error handling

    print_all()
