import sys
import CompositeImage
import os.path
from optparse import OptionParser


def setup_config_parser():
    usage = "usage: %prog [options] raw_files_dir img_sequence_dir"
    config_parser = OptionParser(usage=usage)
    config_parser.add_option('-t', '--sequence_type', dest='seq_type', default='HDR', help="Type of the sequences to identify. Valid values: HDR, TIME, PANO. (Default: %default)")
    config_parser.add_option('-r', '--raw_ext', dest='raw_ext', default='.CR2', help="Extension of input files. (Default: %default)")
    config_parser.add_option('-i', '--img_ext', dest='img_ext', default='.TIF', help="Extension of the image sequence output (Default: %default)")
    config_parser.add_option('-p', '--prefix', dest='img_prefix', default='${dir}', help='Prefix of the img sequences identified. (Default: directory name of the input file')
    config_parser.add_option('-R', '--recursive', action='store_true', dest='recursive', default=False, help='Traverses subdirs to find sequences. (Default: %default)')
    config_parser.add_option('-m', '--maxdiff', type="int", dest='maxdiff', default=7, help="Maximum time difference of two images in a sequence. (Default: %default)")
    return config_parser


def process_seq_type(config_parser, config, outdir):
    confs ={'HDR':(CompositeImage.HDRConfig, CompositeImage.HDRGenerator),
            'TIME':(CompositeImage.Config, None), # To generate error as it is not implemented
            'weakpano':(CompositeImage.PanoWeakConfig, CompositeImage.PanoGenerator),
            'strongpano':(CompositeImage.PanoStrongConfig, CompositeImage.PanoGenerator)}

    if config.seq_type in confs.keys():
        seq_conf = confs[config.seq_type][0](outdir,
                                             config.maxdiff,
                                             config.raw_ext,
                                             config.img_ext,
                                             config.img_prefix)
        seq_gen = confs[config.seq_type][1]
        return seq_conf, seq_gen
    else:
        config_parser.error("Unknown sequence type %s" % config.seq_type) #Process stops here due to error


def process_dirs(config_parser, pos_args):
    if len(pos_args) != 2:
        config_parser.error("Both 'raw_files_dir' and 'img_sequence_dir' has to be specified")
    outdir = pos_args[1]
    indir = pos_args[0]
    return outdir, indir


config_parser = setup_config_parser()
(config, pos_args) = config_parser.parse_args()

outdir, indir = process_dirs(config_parser, pos_args)

seq_parser_config, seq_generator = process_seq_type(config_parser, config, outdir)

collect_seq_strategy = CompositeImage.CollectSeqStrategy()

if config.recursive:
    print '-R is not implemented yet'
    pass
    # walk through
else:
    img_seqs, single_imgs = collect_seq_strategy.parseDir(indir, seq_parser_config)
    symlink_generator = CompositeImage.SymlinkGenerator()
    for cimg in img_seqs:
        symlink_generator(cimg, seq_parser_config)
        seq_generator(cimg, seq_parser_config)
    

