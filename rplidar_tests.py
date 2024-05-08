from rplidar import RPLidar
from time import sleep
lidar = RPLidar('/dev/ttyUSB0')
lidar.stop_motor()

scans = []
def mathy(fn=sum, n=0, normalize = True):
    return fn([s[n] for s in scans]) / (len(scans) if normalize else 1)

def get_some_scans(scan_points=20):
    lidar.start_motor()
    print("spin up...")
    sleep(1.0)
    
    for i, scan in enumerate(lidar.iter_scans()):
        print('%d: Got %d measurments' % (i, len(scan)))
        scans.extend(scan)
        if i > scan_points:
            break
    print("done")
    lidar.stop_motor()

if __name__ == '__main__':
    get_some_scans()
    for s in scans:
        print(s)
