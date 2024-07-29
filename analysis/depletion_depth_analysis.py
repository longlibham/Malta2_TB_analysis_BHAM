# this is a python script

#=======================================================================
#   Copyright (C) 2024 Univ. of Bham  All rights reserved.
#   
#   		FileName：		depletion_depth_analysis.py
#   	 	Author：		LongLI <long.l@cern.ch>
#   		Time：			2024.05.14
#   		Description：
#
#======================================================================

import os 
import sys
import argparse
from ROOT import *
from array import array
import math


gStyle.SetOptStat(0000)
gStyle.SetOptFit(000000)

plot_style = ["W12R7",
                {6: kBlue, 9: kRed, 15: kCyan + 1, 20: kMagenta, 25: kGreen, 30: kOrange,
                35: kCyan, 40: kSpring, 45: kPink},
                {6: 21, 9: 22, 15: 23, 20: 33, 25: 29, 30: 28, 35: 29, 40: 30,
                45: 20},
                {6: 1, 9: 1, 15: 1, 20: 1, 25: 1, 30: 1, 35: 1, 40: 1, 45: 1},
                {'015': 180, '020': 200, '040':260, '080':350, '120':405}]



class Linfit:
    def __call__(self, arr, par):
        rev = par[0]*arr[0] + par[1]
        return rev

def clear_array(array):
    while(len(array)):
        a = array.pop()
    return array


def prepare_data(data_path):
    configures = []
    data = {}
    data_err = {}
    for currentPath, dirs, files in os.walk(data_path):
        if len(dirs) == 0:
            continue
        # select the data with deg00.0
        for item in dirs:
            if 'deg00' in item or 'deg00.0' in item:
                #config [ITHR, SUB]
                config = (item.split('ITHR')[-1].split('_')[0], item.split('SUB')[-1].split('_')[0])
                configures.append(config)

        configures = sorted(configures)
        print(configures)

        for config in configures:
            dict_size = {}
            dict_size_err = {}
            for item in dirs:
                #print(config[0], config[1])
                ithr, sub = f'ITHR{config[0]}', f'SUB{config[1]}'
                if ithr in item and sub in item:
                    deg = float(item.split('deg')[-1])
                    tarpath = os.path.join(currentPath,item)
                    tarfile = os.path.join(tarpath,item)
                    tarfile += '.root'
                    if not os.path.exists(tarfile):
                        print(f'{tarfile} does not exist')
                        continue

                    dict_size[deg] = tarfile
            
            data[config] = dict_size

    return data


def DrawPlot(mg, title, ithr, chip):
    c1 = TCanvas("c1", "clsize vs degs", 1200, 800)
    c1.SetRightMargin(0.1)
    c1.SetLeftMargin(0.1)

    latex_hpos = 0.15
    latex_vpos = 0.8
    latex_space = 0.06
    
    lgd_lpos = 0.45
    lgd_rpos = 0.85
    lgd_tpos = 0.9
    lgd_bpos = 0.6

    mg.GetXaxis().SetTitleFont(42)
    mg.GetXaxis().SetLabelFont(42)
    if title == 'Depletion_depth_vs_degs':
        mg.GetXaxis().SetTitle('Inclined angle [deg]')
        mg.GetYaxis().SetTitle('Depletion depth [#mum]')
        mg.GetYaxis().SetRangeUser(-10, 70)
    elif title == "delta_cluster_size_vs_tanalpha":
        mg.GetXaxis().SetTitle('tan(#alpha)')
        mg.GetYaxis().SetTitle('Clsize(#alpha) - Clsize(0)')
        mg.GetYaxis().SetRangeUser(-1.5, 4)
    elif title == "Estimated_depletion_depth_vs_vsub":
        mg.GetXaxis().SetTitle('VSUB [-V]')
        mg.GetYaxis().SetTitle('Estimated depletion depth [#mum]')
        mg.GetYaxis().SetRangeUser(0, 100)
    mg.GetYaxis().SetTitleFont(42)
    mg.GetYaxis().SetLabelFont(42)
    
   
    mg.Draw('AP')

    lgd = c1.BuildLegend(lgd_lpos, lgd_bpos, lgd_rpos, lgd_tpos)
    lgd.SetNColumns(1)
    lgd.SetTextFont(42)
    lgd.SetFillColorAlpha(0, 0)
    lgd.SetBorderSize(0)

    logo_tex = TLatex()
    logo_tex.SetNDC(True)
    logo_tex.SetTextSize(0.05)
    logo_tex.SetTextFont(62)
    logo_tex.DrawLatex(latex_hpos, latex_vpos, "MALTA2")
    logo_tex.SetTextFont(42)
    logo_tex.DrawLatex(latex_hpos, latex_vpos - latex_space, "Cz, 100 #mum, H-dop")
    if chip == 'W12R7':
        logo_tex.DrawLatex(latex_hpos, latex_vpos - 2*latex_space, "back-metal, XDPW")
        logo_tex.DrawLatex(latex_hpos, latex_vpos - 3*latex_space, "1x10^{15} 1 MeV n_{eq}/cm^{2}")

    # logo_tex.DrawLatex(0.69, 0.55, "Threshold: %d e^{-}" % plot_style[4][ithr])
    if ithr != 'all':
        logo_tex.DrawLatex(latex_hpos, latex_vpos - 4*latex_space, "Threshold: %s e^{-}" % plot_style[4][ithr])

    c1.Print(f"plots/Depletion_depth/{chip}/{title}_ITHR{ithr}.pdf")
    c1.Close()
    

def plotting(ithr, plot_data, chip):
    lwidth = 2
    msize = 1.5
    pitch = 36.4
   # plot_style = ["W12R7" ,{'06.0':kBlue, '09.0':kRed, '15.0':kCyan+1, '20.0':kMagenta, '25.0':kGreen, '30.0':kOrange, '35.0':kCyan, '40.0':kSpring, '45.0':kPink},
    #              {'06.0':21, '09.0':22, '15.0':23, '20.0':33, '25.0':29, '30.0':28, '35.0':29, '40.0':30, '45.0':20},
    #               {'06.0':1, '09.0':1, '15.0':1, '20.0':1, '25.0':1, '30.0':1, '35.0':1, '40.0':1, '45.0':1}, {'040':260, '080':350}]
    
    degs = array('d')
    clsizes = array('d')
    clsizes_err = array('d')
    depletion_depth = array('d')
    clresd = array('d')
    clrese = array('d')
    tanalpha = array('d')

    subs = array('d')
    depth_mean = array('d')
    depth_err = array('d')


    mg = TMultiGraph()
    mg_linear = TMultiGraph()

    linfit = Linfit()
    func = TF1("linFunc", linfit, 0, 2, 2)
    func.SetParameter(0, 1)
    func.SetParName(0, 'a')
    func.SetParLimits(0, -1, 5)    
    func.SetParameter(1, 0)
    func.SetParName(1, 'b')
    func.SetParLimits(1, -5, 5)


    for key, value in plot_data.items():

        for deg, clsize in value.items():
            degs.append(deg)
            
            if not os.path.exists(clsize):
                        print(f'{clsize} does not exist')
                        continue
            
            rootfile = TFile(clsize, 'r')
            hist = rootfile.Get('ClSize_matchx')

            clsizes.append(hist.GetMean())
            clsizes_err.append(hist.GetRMS())
        
        deg0 = degs.pop(0)
        clsize0 = clsizes.pop(0)
        clerr0 = clsizes_err.pop(0)



        for i in range(len(clsizes)):

            depth = pitch*(clsizes[i] - clsize0)/math.tan(math.pi*degs[i]/180.)
            depletion_depth.append(depth)

            tanalpha.append(math.tan(math.pi*degs[i]/180.))
            clresd.append(clsizes[i] - clsize0)
            clrese.append(math.sqrt(clsizes_err[i]**2 + clerr0**2))


        graph = TGraph(len(degs), degs, depletion_depth)
        title = 'V_{sub} = -' + f'{float(key)} V'
        graph.SetTitle(title)
        graph.SetLineWidth(lwidth)
        graph.SetLineColor(plot_style[1][int(float(key))])
        graph.SetLineStyle(plot_style[3][int(float(key))])
        graph.SetMarkerSize(msize)
        graph.SetMarkerStyle(plot_style[2][int(float(key))])
        graph.SetMarkerColor(plot_style[1][int(float(key))])
        mg.Add(graph, 'AP')

        # graph = TGraphErrors(len(degs), tanalpha, clresd, 0, clrese)
        graph = TGraph(len(degs), tanalpha, clresd)
        graph.SetTitle(title)
        graph.SetLineWidth(lwidth)
        graph.SetLineColor(plot_style[1][int(float(key))])
        graph.SetLineStyle(plot_style[3][int(float(key))])
        graph.SetMarkerSize(msize)
        graph.SetMarkerStyle(plot_style[2][int(float(key))])
        graph.SetMarkerColor(plot_style[1][int(float(key))])
        # fitting
        # linfit = Linfit()
        func = TF1("linFunc", "[0]*x+[1]", 0, 2, 2)
        func.SetLineStyle(2)
        func.SetLineColor(plot_style[1][int(float(key))])
        # func.SetParameter(0, 1)
        # func.SetParName(0, 'a')
        # func.SetParLimits(0, -1, 5)    
        # func.SetParameter(1, 0)
        # func.SetParName(1, 'b')
        # func.SetParLimits(1, -5, 5)
        frp = graph.Fit(func, 'S', '', 0.3, 1.8)

        subs.append(float(key))
        depth_mean.append(frp.Parameter(0)*pitch)
        depth_err.append(frp.ParError(0)*pitch)

        mg_linear.Add(graph, 'AP')


        degs = clear_array(degs)
        clsizes = clear_array(clsizes)
        clsizes_err = clear_array(clsizes_err)
        depletion_depth = clear_array(depletion_depth)
        tanalpha = clear_array(tanalpha)
        clresd = clear_array(clresd)
        clrese = clear_array(clrese)

    gedepth = TGraphErrors(len(subs), subs, depth_mean, 0, depth_err)
    title = f"ITHR: {ithr}"
    gedepth.SetTitle(title)
    gedepth.SetLineWidth(lwidth)
    gedepth.SetLineStyle(1)
    gedepth.SetMarkerSize(msize)
    gedepth.SetMarkerStyle(21)
    gedepth.SetMarkerColor(4)
    gedepth.GetXaxis().SetTitle("V_{sub} [-V]")
    gedepth.GetYaxis().SetTitle("Depletion depth [#mum]")    

    DrawPlot(mg, "Depletion_depth_vs_degs", ithr, chip)
    DrawPlot(mg_linear, "delta_cluster_size_vs_tanalpha", ithr, chip)
    
    return gedepth
    # DrawPlot(gedepth, "Estimated_depletion_depth_vs_vsub", ithr, chip)






def process_data(args):
    data = prepare_data(args.data_path)
    ithr_set = set()
    chip = args.data_path.split('/')[-1]
    #classify the data by ITHR value
    for key in data.keys():
        ithr_set.add(key[0])

    ithr_set = sorted(ithr_set)

    cvs = TCanvas("cvs")
    mg = TMultiGraph()
    for i, ithr in enumerate(ithr_set):
        plot_data = {}
        for key in data.keys():
            if ithr != key[0]: continue
            sub = key[1]
            sub_data = dict(sorted(data[key].items()))
            plot_data[sub] = sub_data
        depth = plotting(ithr, plot_data, chip)
        depth.SetLineColor(i+1)
        depth.SetMarkerColor(i+1)
        depth.SetTitle("Threshold: %s e^{-}" % plot_style[4][ithr])
        
        mg.Add(depth, "ALP")
        mg.GetXaxis().SetTitle("V_{sub} [-V]")
        mg.GetYaxis().SetTitle("Depletion Depth [#mum]")


    DrawPlot(mg, "Estimated_depletion_depth_vs_vsub", 'all', chip)








if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='depletion depth study of Malta2 with grazing angle')
    parser.add_argument('--data_path', type=str, default='../Data/W12R7', help='Data path for analysis')

    args = parser.parse_args()
    process_data(args)
