import time
import math

bag_timers = {}

DIST_THRESHOLD = 150   # pixels
TIME_THRESHOLD = 1     # seconds

def get_center(box):
    x1, y1, x2, y2 = box
    return ((x1+x2)//2, (y1+y2)//2)

def distance(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

def check_unattended(bags, persons):
    alerts = []

    current_time = time.time()

    for i, bag in enumerate(bags):
        bag_center = get_center(bag)

        near_person = False
        for person in persons:
            person_center = get_center(person)
            if distance(bag_center, person_center) < DIST_THRESHOLD:
                near_person = True
                break

        if not near_person:
            if i not in bag_timers:
                bag_timers[i] = current_time
            else:
                elapsed = current_time - bag_timers[i]
                if elapsed > TIME_THRESHOLD:
                    alerts.append("⚠️ Unattended Bag Detected")
        else:
            if i in bag_timers:
                del bag_timers[i]

    return alerts