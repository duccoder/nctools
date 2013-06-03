#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Optimizes lines and arcs from a DXF file for cutting on a Gerber cutter,
# output another DXF file.
#
# Copyright © 2011,2012 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
# $Date$
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

import sys
import datetime
import os.path
import dxftools.dxfgeom as dxfgeom


__proginfo__ = ('dxfgerber [ver. ' + '$Revision$'[11:-2] +
                '] (' + '$Date$'[7:-2] + ')')


def dxf_header(progname, loc, loe):
    """Create the comments for at the beginning of a DXF file.

    :progname: name of the program
    :loc: list of Contours
    :loe: list of Entities
    :returns: a string containing the beginning of a DXF file
    """
    a = 'This conversion was started on {}'
    b = 'This file contains {} contours, {} remaining entities.'
    u = '#{} bounding box ({:.3f}, {:.3f}, {:.3f}, {:.3f})'
    dt = datetime.datetime.now()
    lines = ['999', 'DXF file generated by {}'.format(progname), '999',
            a.format(dt.strftime("%A, %B %d %H:%M")), '999', 
            b.format(len(loc), len(loe))]
    for n, c in enumerate(loc):
        lines += ['999', u.format(n+1, *c.getbb())]
    lines.append('')
    return '\n'.join(lines)


def start_entities():
    """Create the beginning of an entities section.

    :returns: a string to begin the ENTITIES section
    """
    return "  0\nSECTION\n  2\nENTITIES\n"


def end_entities():
    """Create the end of an entities section.
    
    :returns: a string to end the ENTITIES section
     """
    s = "  0\nENDSEC\n  0\nEOF"
    return s


def newname(oldname):
    """Create an output filename based on the input filename.

    :oldname: name of the input file
    :returns: name of the output file
    """
    oldbase = os.path.splitext(os.path.basename(oldname))[0]
    if oldbase.startswith('.') or oldbase.isspace():
        raise ValueError("Invalid file name!")
    rv = oldbase + '_mod.dxf'
    return rv


def main(argv):
    """Main program for the dxfgerber utility.

    :argv: command line arguments
    """
    if len(argv) == 1:
        print __proginfo__
        print "Usage: {} [file.dxf ...]".format(argv[0])
        exit(1)
    del argv[0]
    for f in argv:
        if not f.endswith(('.dxf', '.DXF')):
            h = 'Probably not a DXF file. Skipping file "{}".'
            print h.format(f)
        try:
            outname = newname(f)
            # Find entities
            entities = dxfgeom.fromfile(f)
        except ValueError as e:
            print e
            h = "Cannot construct output filename. Skipping file '{}'."
            print h.format(f)
            print "A valid filename _must_ have a '.dxf' extension."
            print "And it must be more than just the extension."
            continue
        except IOError:
            print "Cannot open the file '{}'. Skipping it.".format(f)
            continue
        # Find contours
        (contours, rement) = dxfgeom.find_contours(entities)
        # Sort in y1, then in x1.
        entities = contours + rement
        entities.sort()
        # Output
        outf = open(outname, 'w')
        outf.write(dxf_header(__proginfo__, contours, rement))
        outf.write(start_entities())
        for e in entities:
            outf.write(e.dxfdata())
        outf.write(end_entities())
        outf.close()


if __name__ == '__main__':
    main(sys.argv)
