import sys
import Parser
import os.path


if 3 > len(sys.argv):
    print "Usage: " + sys.argv[0] + " indir outdir [prefix]"
    quit()
    
indir = os.path.abspath(sys.argv[1])
outdir = os.path.abspath(sys.argv[2])

if 3 == len(sys.argv):
    prefix = os.path.basename(indir)
else:
    prefix = 'Set' + sys.argv(3)
    
Parser.generateMoveScript(indir,
                           outdir,
                           prefix)
Parser.generateHDRScript(indir,
                          outdir,
                          prefix)