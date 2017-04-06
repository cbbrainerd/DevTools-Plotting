#!/usr/bin/env python
import argparse
import logging
import os
import sys
import itertools
import operator

from NtupleSkimmer import NtupleSkimmer
from DevTools.Utilities.utilities import prod, ZMASS

import ROOT

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


class Hpp4lSkimmer(NtupleSkimmer):
    '''
    Hpp4l skimmer
    '''

    def __init__(self,sample,**kwargs):
        super(Hpp4lSkimmer, self).__init__('Hpp4l',sample,**kwargs)

        # test if we want to run the optimization routine
        self.optimize = True
        self.var = 'dr'

        # setup output files
        self.leps = ['hpp1','hpp2','hmm1','hmm2']
        # setup properties
        self.leps = ['hpp1','hpp2','hmm1','hmm2']
        self.isSignal = 'HPlusPlusHMinus' in self.sample
        self.masses = [200,300,400,500,600,700,800,900,1000,1100,1200,1300,1400,1500]
        if self.isSignal:
            self.masses = [mass for mass in self.masses if 'M-{0}'.format(mass) in self.sample]

        # alternative fakerates
        self.fakekey = '{num}_{denom}'
        self.fakehists = {'electrons': {}, 'muons': {}, 'taus': {},}

        fake_path = '{0}/src/DevTools/Analyzer/data/fakerates_dijet_hpp_13TeV_Run2016BCDEFGH.root'.format(os.environ['CMSSW_BASE'])
        self.fake_hpp_rootfile = ROOT.TFile(fake_path)
        self.fakehists['electrons'][self.fakekey.format(num='HppMedium',denom='HppLoose')] = self.fake_hpp_rootfile.Get('e/medium_loose/fakeratePtEta')
        self.fakehists['electrons'][self.fakekey.format(num='HppTight',denom='HppLoose')] = self.fake_hpp_rootfile.Get('e/tight_loose/fakeratePtEta')
        self.fakehists['electrons'][self.fakekey.format(num='HppTight',denom='HppMedium')] = self.fake_hpp_rootfile.Get('e/tight_medium/fakeratePtEta')
        self.fakehists['muons'][self.fakekey.format(num='HppMedium',denom='HppLoose')] = self.fake_hpp_rootfile.Get('m/medium_loose/fakeratePtEta')
        self.fakehists['muons'][self.fakekey.format(num='HppTight',denom='HppLoose')] = self.fake_hpp_rootfile.Get('m/tight_loose/fakeratePtEta')
        self.fakehists['muons'][self.fakekey.format(num='HppTight',denom='HppMedium')] = self.fake_hpp_rootfile.Get('m/tight_medium/fakeratePtEta')

        fake_path = '{0}/src/DevTools/Analyzer/data/fakerates_w_tau_13TeV_Run2016BCDEFGH.root'.format(os.environ['CMSSW_BASE'])
        self.fake_hpp_rootfile_tau = ROOT.TFile(fake_path)
        self.fakehists['taus'][self.fakekey.format(num='HppMedium',denom='HppLoose')] = self.fake_hpp_rootfile_tau.Get('medium_loose/fakeratePtEta')
        self.fakehists['taus'][self.fakekey.format(num='HppTight',denom='HppLoose')] = self.fake_hpp_rootfile_tau.Get('tight_loose/fakeratePtEta')
        self.fakehists['taus'][self.fakekey.format(num='HppTight',denom='HppMedium')] = self.fake_hpp_rootfile_tau.Get('tight_medium/fakeratePtEta')

        self.scaleMap = {
            'F' : '{0}_looseScale',
            'P' : '{0}_mediumScale',
        }

        self.fakeVal = '{0}_mediumFakeRate'

        self.lepID = '{0}_passMedium'

    def getFakeRate(self,lep,pt,eta,num,denom):
        key = self.fakekey.format(num=num,denom=denom)
        hist = self.fakehists[lep][key]
        if pt > 100.: pt = 99.
        b = hist.FindBin(pt,abs(eta))
        return hist.GetBinContent(b), hist.GetBinError(b)

    def getWeight(self,row,doFake=False):
        passID = [getattr(row,self.lepID.format(l)) for l in self.leps]
        if row.isData:
            weight = 1.
        else:
            # per event weights
            base = ['genWeight','pileupWeight','triggerEfficiency']
            if self.shift=='trigUp': base = ['genWeight','pileupWeight','triggerEfficiencyUp']
            if self.shift=='trigDown': base = ['genWeight','pileupWeight','triggerEfficiencyDown']
            if self.shift=='puUp': base = ['genWeight','pileupWeightUp','triggerEfficiency']
            if self.shift=='puDown': base = ['genWeight','pileupWeightDown','triggerEfficiency']
            for l,lep in enumerate(self.leps):
                shiftString = ''
                if self.shift == 'lepUp': shiftString = 'Up'
                if self.shift == 'lepDown': shiftString = 'Down'
                base += [self.scaleMap['P' if passID[l] else 'F'].format(lep)+shiftString]
            vals = [getattr(row,scale) for scale in base]
            for scale,val in zip(base,vals):
                if val != val: logging.warning('{0}: {1} is NaN'.format(row.channel,scale))
            weight = prod([val for val in vals if val==val])
            # scale to lumi/xsec
            weight *= float(self.intLumi)/self.sampleLumi if self.sampleLumi else 0.
            if hasattr(row,'qqZZkfactor'): weight *= row.qqZZkfactor/1.1 # ZZ variable k factor
        # fake scales
        if doFake:
            chanMap = {'e': 'electrons', 'm': 'muons', 't': 'taus',}
            chan = ''.join([x for x in row.channel if x in 'emt'])
            pts = [getattr(row,'{0}_pt'.format(x)) for x in self.leps]
            etas = [getattr(row,'{0}_eta'.format(x)) for x in self.leps]
            region = ''.join(['P' if x else 'F' for x in passID])
            sign = -1 if region.count('F')%2==0 and region.count('F')>0 else 1
            weight *= sign
            if not row.isData and not all(passID): weight *= -1 # subtract off MC in control
            for l,lep in enumerate(self.leps):
                if not passID[l]:
                    # recalculate
                    fakeEff = self.getFakeRate(chanMap[chan[l]], pts[l], etas[l], 'HppMedium','HppLoose')[0]

                    # read from tree
                    #fake = self.fakeVal.format(lep)
                    #if self.shift=='fakeUp': fake += 'Up'
                    #if self.shift=='fakeDown': fake += 'Down'
                    #fakeEff = getattr(row,fake)

                    weight *= fakeEff/(1-fakeEff)

        return weight

    def perRowAction(self,row):
        isData = row.isData

        # per sample cuts
        keep = True
        if self.sample=='DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'  : keep = row.numGenJets==0 or row.numGenJets>4
        if self.sample=='DY1JetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8' : keep = row.numGenJets==1
        if self.sample=='DY2JetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8' : keep = row.numGenJets==2
        if self.sample=='DY3JetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8' : keep = row.numGenJets==3
        if self.sample=='DY4JetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8' : keep = row.numGenJets==4
        if self.sample=='DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'      : keep = row.numGenJets==0 or row.numGenJets>4
        if self.sample=='DY1JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'     : keep = row.numGenJets==1
        if self.sample=='DY2JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'     : keep = row.numGenJets==2
        if self.sample=='DY3JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'     : keep = row.numGenJets==3
        if self.sample=='DY4JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'     : keep = row.numGenJets==4
        if self.sample=='WJetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'           : keep = row.numGenJets==0 or row.numGenJets>4
        if self.sample=='W1JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'          : keep = row.numGenJets==1
        if self.sample=='W2JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'          : keep = row.numGenJets==2
        if self.sample=='W3JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'          : keep = row.numGenJets==3
        if self.sample=='W4JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'          : keep = row.numGenJets==4
        if not keep: return

        # define weights
        w = self.getWeight(row)
        wf = self.getWeight(row,doFake=True)

        # setup channels
        passID = [getattr(row,self.lepID.format(l)) for l in self.leps]
        region = ''.join(['P' if p else 'F' for p in passID])
        nf = region.count('F')
        fakeChan = '{0}P{1}F'.format(4-nf,nf)
        recoChan = ''.join([x for x in row.channel if x in 'emt'])
        recoChan = ''.join(sorted(recoChan[:2]) + sorted(recoChan[2:4]))
        if isData:
            genChan = 'all'
        else:
            genChan = row.genChannel
            if 'HPlusPlus' in self.sample:
                if 'HPlusPlusHMinusMinus' in self.sample:
                    genChan = ''.join(sorted(genChan[:2]) + sorted(genChan[2:4]))
                else:
                    genChan = ''.join(sorted(genChan[:2]) + sorted(genChan[2:3]))
            else:
                genChan = 'all'

        # define count regions
        default = True
        lowmass = row.hpp_mass<100 or row.hmm_mass<100
        if not isData:
            genCut = all([getattr(row,'{0}_genMatch'.format(lep)) and getattr(row,'{0}_genDeltaR'.format(lep))<0.1 for lep in self.leps])

        # cut map
        v = {
            'st': row.hpp1_pt+row.hpp2_pt+row.hmm1_pt+row.hmm2_pt,
            'zdiff': abs(row.z_mass-ZMASS),
            'drpp': row.hpp_deltaR,
            'drmm': row.hmm_deltaR,
            'hpp': row.hpp_mass,
            'hmm': row.hmm_mass,
        }
        cutRegions = {}
        # comments are: 8TeV, ICHEP, current
        for mass in self.masses:
            cutRegions[mass] = {
                0: {
                    #'st'   : v['st']>1.23*mass+54,
                    'st'   : v['st']>1.69*mass+58 or v['st']>1600,
                    #'zveto': True,
                    'zveto': v['zdiff']>10,
                    'drpp' : True,
                    'drmm' : True,
                    'hpp'  : v['hpp']>0.9*mass and v['hpp']<1.1*mass,
                    'hmm'  : v['hmm']>0.9*mass and v['hmm']<1.1*mass,
                },
                1: {
                    #'st'   : v['st']>0.88*mass+73,
                    'st'   : v['st']>1.6*mass-20 or v['st']>1600,
                    'zveto': v['zdiff']>10,
                    #'drpp' : True,
                    #'drmm' : True,
                    'drpp' : v['drpp']<3.3,
                    'drmm' : v['drmm']<3.3,
                    'hpp'  : v['hpp']>0.4*mass and v['hpp']<1.1*mass,
                    'hmm'  : v['hmm']>0.4*mass and v['hmm']<1.1*mass,
                },
                2: {
                    #'st'   : v['st']>0.46*mass+108,
                    'st'   : v['st']>0.79*mass+141 or v['st']>1600,
                    #'zveto': v['zdiff']>50,
                    #'zveto': v['zdiff']>25,
                    'zveto': v['zdiff']>10,
                    #'drpp' : v['drpp']<mass/1400.+2.43,
                    #'drmm' : v['drmm']<mass/1400.+2.43,
                    'drpp' : v['drpp']<2.5,
                    'drmm' : v['drmm']<2.5,
                    'hpp'  : v['hpp']>0.3*mass and v['hpp']<1.1*mass,
                    'hmm'  : v['hmm']>0.3*mass and v['hmm']<1.1*mass,
                },
            }

        # optimization ranges
        stRange = [x*20 for x in range(100)]
        zvetoRange = [x*5 for x in range(20)]
        drRange = [1.5+x*0.1 for x in range(50)]

        # increment counts
        if default:
            if all(passID): self.increment('default',w,recoChan,genChan)
            if isData or genCut: self.increment(fakeChan,wf,recoChan,genChan)
            self.increment(fakeChan+'_regular',w,recoChan,genChan)

            for pTaus in range(3):
                for mTaus in range(3):
                    nTaus = max(pTaus,mTaus)
                    for mass in self.masses:
                        name = '{0}/hpp{1}hmm{2}'.format(mass,pTaus,mTaus)
                        sides = []
                        windows = []
                        sides += [cutRegions[mass][nTaus]['st']]
                        if nTaus>0: sides += [cutRegions[mass][nTaus]['zveto']]
                        if pTaus>1: sides += [cutRegions[mass][pTaus]['drpp']]
                        if mTaus>1: sides += [cutRegions[mass][mTaus]['drmm']]
                        windows += [cutRegions[mass][pTaus]['hpp']]
                        windows += [cutRegions[mass][mTaus]['hpp']]
                        massWindowOnly = all(windows)
                        sideband = not all(sides) and not all(windows)
                        massWindow = not all(sides) and all(windows)
                        allSideband = all(sides) and not all(windows)
                        allMassWindow = all(sides) and all(windows)
                        if not self.optimize:
                            if sideband:
                                if all(passID): self.increment('new/sideband/'+name,w,recoChan,genChan)
                                if isData or genCut: self.increment(fakeChan+'/new/sideband/'+name,wf,recoChan,genChan)
                            if massWindow:
                                if all(passID): self.increment('new/massWindow/'+name,w,recoChan,genChan)
                                if isData or genCut: self.increment(fakeChan+'/new/massWindow/'+name,wf,recoChan,genChan)
                            if allSideband:
                                if all(passID): self.increment('new/allSideband/'+name,w,recoChan,genChan)
                                if isData or genCut: self.increment(fakeChan+'/new/allSideband/'+name,wf,recoChan,genChan)
                            if allMassWindow:
                                if all(passID): self.increment('new/allMassWindow/'+name,w,recoChan,genChan)
                                if isData or genCut: self.increment(fakeChan+'/new/allMassWindow/'+name,wf,recoChan,genChan)
                        # run the grid of values
                        if self.optimize:
                            # optimize only 0,0 1,1 or 2,2 taus
                            if pTaus!=mTaus: continue
                            if not massWindowOnly: continue
                            # 1D no cuts
                            nMinusOneSt = all([cutRegions[mass][nTaus]['zveto'], cutRegions[mass][pTaus]['drpp'], cutRegions[mass][mTaus]['drmm']])
                            nMinusOneZveto = all([cutRegions[mass][nTaus]['st'], cutRegions[mass][pTaus]['drpp'], cutRegions[mass][mTaus]['drmm']])
                            nMinusOneDR = all([cutRegions[mass][nTaus]['st'], cutRegions[mass][nTaus]['zveto']])
                            if self.var=='st':
                                for stCutVal in stRange:
                                    if v['st']>stCutVal and nMinusOneSt:
                                        if all(passID): self.increment('optimize/st/{0}/{1}'.format(stCutVal,name),w,recoChan,genChan)
                                        if isData or genCut: self.increment(fakeChan+'/optimize/st/{0}/{1}'.format(stCutVal,name),wf,recoChan,genChan)
                            if self.var=='zveto':
                                for zvetoCutVal in zvetoRange:
                                    if v['zdiff']>zvetoCutVal and nMinusOneZveto:
                                        if all(passID): self.increment('optimize/zveto/{0}/{1}'.format(zvetoCutVal,name),w,recoChan,genChan)
                                        if isData or genCut: self.increment(fakeChan+'/optimize/zveto/{0}/{1}'.format(zvetoCutVal,name),wf,recoChan,genChan)
                            if self.var=='dr':
                                for drCutVal in drRange:
                                    if v['drpp']<drCutVal and v['drmm']<drCutVal and nMinusOneDR:
                                        if all(passID): self.increment('optimize/dr/{0}/{1}'.format(drCutVal,name),w,recoChan,genChan)
                                        if isData or genCut: self.increment(fakeChan+'/optimize/dr/{0}/{1}'.format(drCutVal,name),wf,recoChan,genChan)
                            # nD
                            #for stCutVal in stRange:
                            #    if v['st']<stCutVal: continue
                            #    for zvetoCutVal in zvetoRange:
                            #        if v['zdiff']<zvetoCutVal: continue
                            #        for drCutVal in drRange:
                            #            if v['drpp']>drCutVal or v['drmm']>drCutVal: continue
                            #            if all(passID): self.increment('optimize/st{0}/zveto{1}/dr{2}/{3}'.format(stCutVal,zvetoCutVal,drCutVal,name),w,recoChan,genChan)
                            #            if isData or genCut: self.increment(fakeChan+'optimize/st{0}/zveto{1}/dr{2}/{3}'.format(stCutVal,zvetoCutVal,drCutVal,name),wf,recoChan,genChan)

                    

        if lowmass:
            if all(passID): self.increment('lowmass',w,recoChan,genChan)
            if isData or genCut: self.increment(fakeChan+'/lowmass',wf,recoChan,genChan)
            self.increment(fakeChan+'_regular/lowmass',w,recoChan,genChan)



def parse_command_line(argv):
    parser = argparse.ArgumentParser(description='Run skimmer')

    parser.add_argument('sample', type=str, default='HPlusPlusHMinusMinusHTo4L_M-200_TuneCUETP8M1_13TeV_pythia8', nargs='?', help='Sample to skim')
    parser.add_argument('shift', type=str, default='', nargs='?', help='Shift to apply to scale factors')

    return parser.parse_args(argv)

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    args = parse_command_line(argv)

    skimmer = Hpp4lSkimmer(
        args.sample,
        shift=args.shift,
    )

    skimmer.skim()

    return 0

if __name__ == "__main__":
    status = main()
    sys.exit(status)

