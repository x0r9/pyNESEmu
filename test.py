import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--simple", help="outputs one instruction per line",
                    action="store_true")
parser.add_argument('binpath', nargs=1, default=[], help='path to binary to disassemble')

args = parser.parse_args()

if args.simple:
    print "yes Simple"
else:
    print "no simple"
print "binpath", args.binpath 

