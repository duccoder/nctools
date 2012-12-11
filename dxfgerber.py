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

# System modules
import sys
import datetime

# Local module.
import dxfgeom

__proginfo__ = ('dxfgerber [ver. ' + '$Revision$'[11:-2] + '] (' +
                '$Date$'[7:-2] + ')')

def dxf_header(progname, loc, lol, loa):
    '''Write comments at the beginning of a DXF file.'''
    s = "999\nDXF file generated by {}\n".format(progname)
    dt = datetime.datetime.now()
    s += "999\nThis conversion was started on "
    s += dt.strftime("%A, %B %d %H:%M\n")
    c = "999\nThis file contains {} contours, {}"\
        " loose lines and {} loose arcs.\n"
    s += c.format(len(loc), len(lol), len(loa))
    s += "999\nThe contours are:"
    for n, c in enumerate(contours):
        u = "\n999\n#{} bounding box ({:.3f}, {:.3f}, {:.3f}, {:.3f})"
        s += u.format(n+1, *c.getbb())
    s += "\n"
    return s

def start_entities():
    '''Write the beginning of an entities section.'''
    return "  0\nSECTION\n  2\nENTITIES\n"

def end_entities():
    '''Write the end of an entities section.'''
    s = "  0\nENDSEC\n  0\nEOF"
    return s

def newname(oldname):
    '''Create an output filename based on the input filename.'''
    if not oldname.endswith(('.dxf', '.DXF')):
        raise ValueError('probably not a DXF file!')
    oldbase = oldname[:-4]
    if len(oldbase) == 0:
        raise ValueError("zero-length file name!")
    newbase = oldbase.rstrip('0123456789')    
    L = len(newbase)
    dstr = oldbase[L:]
    if len(dstr) > 0:
        num = int(dstr) +1
    else:
        num = 1
    rv = newbase + str(num) + '.dxf'
    return rv

def main(argv):
    '''Main program for the dxfgerber utility.'''
    if len(argv) == 1:
        print __proginfo__
        print "Usage: {} [file.dxf ...]".format(argv[0])
        exit(1)
    del argv[0]
    for f in argv:
        try:
            outname = newname(f)
            ent = dxfgeom.read_entities(f)
        except ValueError:
            h = "Cannot construct output filename. Skipping file '{}'."
            print h.format(f)
            print "A valid filename _must_ have a '.dxf' extension."
            print "And it must be more than just the extension."
            continue
        except IOError:
            print "Cannot open the file '{}'. Skipping it.".format(f)
            continue
        # Find entities
        lo = dxfgeom.find_entities("LINE", ent)
        lines = []
        if len(lo) > 0:
            lines = [dxfgeom.line_from_elist(ent, nn) for nn in lo]
        ao = dxfgeom.find_entities("ARC", ent)
        arcs = []
        if len(ao) > 0:
            arcs = [dxfgeom.arc_from_elist(ent, m) for m in ao]
        # Find contours
        (contours, remlines, remarcs) = dxfgeom.find_contours(lines, arcs)
        # Sort in y1, then in x1.
        contours.sort()
        remlines.sort()
        remarcs.sort()
        # Output
        outf = open(outname, 'w')
        outf.write(dxf_header(__proginfo__, contours, remlines, remarcs))
        outf.write(start_entities())
        for cn in contours:
            outf.write(cn.dxfdata())
        for l in remlines:
            outf.write(l.dxfdata())
        for a in remarcs:
            outf.write(a.dxfdata())
        outf.write(end_entities())
        outf.close()

if __name__ == '__main__':
    main(sys.argv)
