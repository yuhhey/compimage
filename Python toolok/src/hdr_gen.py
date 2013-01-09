import CompositeImage as CI
import glob

HDRworkdir = '/home/smb/HDR'

HDRCollector = CI.CollectHDRStrategy()

fl = glob.glob('/home/smb/git/fotoworkflow/Python toolok/src/test_images/*.CR2')
hdrs,sic = HDRCollector.parseFileList(fl)

symlink_gen = CI.SymlinkGenerator()
symlink_gen.setTargetDir(HDRworkdir)
for hdr in hdrs:
    symlink_gen(hdr.getCompImage())

hdr_gen = CI.HDRGenerator()
hdr_gen.setParams(HDRworkdir, '.tiff', 'test')

#for i, hdr in enumerate(hdrs):
#    hdr_gen._prefix = 'test_%d' % i
#    hdr_gen(hdr.getCompImage())

hdr_gen(hdrs[0].getCompImage())
