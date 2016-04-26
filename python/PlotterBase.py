import os
import sys
import logging
import math
from array import array
from collections import OrderedDict
import tempfile

import ROOT

from DevTools.Plotter.utilities import python_mkdir, getLumi
from DevTools.Plotter.style import getStyle
import DevTools.Plotter.CMS_lumi as CMS_lumi
import DevTools.Plotter.tdrstyle as tdrstyle

ROOT.gROOT.SetBatch(ROOT.kTRUE)
ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = 1001;")
tdrstyle.setTDRStyle()
ROOT.gStyle.SetPalette(1)

class PlotterBase(object):
    '''Basic plotter utilities'''

    def __init__(self,analysis,**kwargs):
        '''Initialize the plotter'''
        # plot directory
        self.analysis = analysis
        self.outputDirectory = kwargs.pop('outputDirectory','plots/{0}'.format(self.analysis))
        # initialize stuff

    def _getLegend(self,**kwargs):
        '''Get the legend'''
        entryArgs = kwargs.pop('entries',[])
        position = kwargs.pop('position',33)
        numcol = kwargs.pop('numcol',1)
        # programatically decide position
        # ----------------
        # | 14 | 24 | 34 |
        # ----------------
        # | 13 | 23 | 33 |
        # ----------------
        # | 12 | 22 | 32 |
        # ----------------
        # | 11 | 21 | 31 |
        # ----------------
        width = 0.15*numcol+0.1
        numentries = len(entryArgs)
        height = math.ceil(float(numentries)/numcol)*0.06+0.02
        if position % 10 == 1:   # bottom
            ystart = 0.16
            yend = ystart+height
        elif position % 10 == 2: # middle
            yend = 0.54+height/2
            ystart = 0.54-height/2
        elif position % 10 == 3: # top
            yend = 0.84
            ystart = yend-height
        else:                    # verytop
            yend = 0.92
            ystart = yend-height
        if position / 10 == 1:   # left
            xstart = 0.19
            xend = xstart+width
        elif position / 10 == 2: # middle
            xstart = 0.57-width/2
            xend = 0.57+width/2
        else:                    # right
            xend = 0.95
            xstart = xend-width
        legend = ROOT.TLegend(xstart,ystart,xend,yend,'','NDC')
        if numcol>1: legend.SetNColumns(int(numcol))
        legend.SetTextFont(42)
        legend.SetBorderSize(0)
        legend.SetFillColor(0)
        for entryArg in entryArgs:
            legend.AddEntry(*entryArg)
        return legend

    def _setStyle(self,pad,position=11,preliminary=True):
        '''Set style for plots based on the CMS TDR style guidelines.
           https://twiki.cern.ch/twiki/bin/view/CMS/Internal/PubGuidelines#Figures_and_tables
           https://ghm.web.cern.ch/ghm/plots/'''
        # set period (used in CMS_lumi)
        # period : sqrts
        # 1 : 7, 2 : 8, 3 : 7+8, 4 : 13, ... 7 : 7+8+13
        period_int = 4
        # set position
        # 11: upper left, 33 upper right
        CMS_lumi.wrtieExtraText = preliminary
        CMS_lumi.extraText = "Preliminary"
        CMS_lumi.lumi_13TeV = "%0.1f fb^{-1}" % (float(getLumi())/1000.)
        if getLumi < 1000:
            CMS_lumi.lumi_13TeV = "%0.1f pb^{-1}" % (float(getLumi))
        CMS_lumi.CMS_lumi(pad,period_int,position)

    def _save(self, canvas, savename):
        '''Save the canvas in multiple formats.'''
        canvas.SetName(savename)
        for type in ['pdf','root','png']:
            name = '{0}/{1}/{2}.{1}'.format(self.outputDirectory, type, savename)
            python_mkdir(os.path.dirname(name))
            canvas.Print(name)

    def _saveTemp(self, canvas):
        '''Save the canvas in multiple formats.'''
        temp = tempfile.NamedTemporaryFile(suffix=".png",delete=False)
        canvas.Print(temp.name)
        return temp.name

