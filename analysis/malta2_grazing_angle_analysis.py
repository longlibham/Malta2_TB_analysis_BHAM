# this is a python script

#=======================================================================
#   Copyright (C) 2024 Univ. of Bham  All rights reserved.
#   
#   		FileName：		malta2_grazing_angle_analysis.py
#   	 	Author：		LongLI <long.l@cern.ch>
#   		Time：			2024.05.26
#   		Description：
#
#======================================================================

import os
import sys
import numpy as np
import pandas as pd
from ROOT import *
from array import array
import argparse
import math

plot_style = ["W12R7",
              {6: kBlue, 9: kRed, 15: kCyan + 1, 20: kMagenta, 25: kGreen, 30: kOrange,
               35: kCyan, 40: kSpring, 45: kPink},
              {6: 21, 9: 22, 15: 23, 20: 33, 25: 29, 30: 28, 35: 29, 40: 30,
               45: 20},
              {6: 1, 9: 1, 15: 1, 20: 1, 25: 1, 30: 1, 35: 1, 40: 1, 45: 1},
              {40: 260, 80: 350}]

def prepare_data(data_path):
    ithrs = {15:0, 20:1, 40:2, 80:3, 120:4} # 15, 20, 40, 80, 120
    subs = {6:0, 9:1, 15:2, 20:3, 25:4, 30:5} # 6, 9, 15, 20, 25, 30
    angles = {0:0, 5:1, 10:2, 15:3, 20:4, 25:5, 30:6, 35:7, 40:8, 45:9, 50:10, 55:11, 60:12} # 0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60
    eff_data = np.zeros((len(ithrs.keys()), len(subs.keys()), len(angles.keys())))
    eff_err = np.zeros((len(ithrs.keys()), len(subs.keys()), len(angles.keys())))
    clsizex_data = np.zeros((len(ithrs.keys()), len(subs.keys()), len(angles.keys())))
    clsizey_data = np.zeros((len(ithrs.keys()), len(subs.keys()), len(angles.keys())))
    resx_data = np.zeros((len(ithrs.keys()), len(subs.keys()), len(angles.keys())))
    resy_data = np.zeros((len(ithrs.keys()), len(subs.keys()), len(angles.keys())))

    for currentPath, dirs, files in os.walk(data_path):
        if len(dirs) == 0:
            continue

        for dir in dirs:
            ithr = int(dir.split('ITHR')[-1].split('_')[0])
            sub = int(float(dir.split('SUB')[-1].split('_')[0]))
            angle = int(float(dir.split('deg')[-1]))
            tarpath = os.path.join(currentPath, dir)
            tarfile = os.path.join(tarpath,'Eff.txt')
            if not os.path.exists(tarfile):
                print(f'{tarfile} not found!')
                continue

            with open(tarfile, 'r') as f:
                for line in f.readlines():
                    if 'TOT:' in line:
                        line = line.strip()
                        eff_data[ithrs[ithr], subs[sub], angles[angle]] = float(line.split(':')[-1].split('  ')[0])
                        eff_err[ithrs[ithr], subs[sub], angles[angle]] = float(line.split(':')[-1].split('  ')[-1])
                    if 'Clsize_x:' in line:
                        clsizex_data[ithrs[ithr], subs[sub], angles[angle]] = float(line.split(' ')[-1])
                    if 'Clsize_y:' in line:
                        clsizey_data[ithrs[ithr], subs[sub], angles[angle]] = float(line.split(' ')[-1])

            tarfile = os.path.join(tarpath, 'Noise.txt')
            if not os.path.exists(tarfile):
                print(f'{tarfile} not found!')
                continue

            with open(tarfile, 'r') as f:
                for line in f.readlines():
                    if 'ResX:' in line:
                        resx_data[ithrs[ithr], subs[sub], angles[angle]] = math.sqrt(float(line.split(':')[-1])**2 - 4.2**2)
                    if 'ResY:' in line:
                        resy_data[ithrs[ithr], subs[sub], angles[angle]] = math.sqrt(float(line.split(':')[-1])**2 - 4.2**2)


    return eff_data, eff_err, clsizex_data, clsizey_data, resx_data, resy_data


def graph_setting(graph, sub, lwidth, lcolor, lstyle, msize, mstyle, mcolor):
    graph.SetTitle('V_{sub} = - %i V' % sub)
    graph.SetLineWidth(lwidth)
    graph.SetLineColor(lcolor)#(plot_style[1][subs[i]])
    graph.SetLineStyle(lstyle)#(plot_style[3][subs[i]])
    graph.SetMarkerSize(msize)
    graph.SetMarkerStyle(mstyle)#(plot_style[2][subs[i]])
    graph.SetMarkerColor(mcolor)#(plot_style[1][subs[i]])


def DrawPlots(graph, chip, compare, ytitle, ymin, ymax, ithr):
    c1 = TCanvas("c1", "clsize vs degs", 1200, 800)
    c1.SetRightMargin(0.1)
    c1.SetLeftMargin(0.1)

    graph.GetXaxis().SetTitleFont(42)
    graph.GetXaxis().SetLabelFont(42)
    graph.GetXaxis().SetTitle('Angle [deg]')
    graph.GetYaxis().SetTitleFont(42)
    graph.GetYaxis().SetLabelFont(42)
    graph.GetYaxis().SetTitle(ytitle)
    graph.GetYaxis().SetRangeUser(ymin, ymax)
    graph.Draw('ALP')

    latex_hpos = 0.14
    latex_vpos = 0.65
    latex_space = 0.06
    lgd_lpos = 0
    lgd_rpos = 0
    lgd_tpos = 0
    lgd_bpos = 0
    if compare == 'Eff':
        lgd_lpos = 0.6
        lgd_rpos = 0.9
        lgd_tpos = 0.55
        lgd_bpos = 0.15
        
    elif 'ClSize' in compare:
        latex_vpos = 0.7
        lgd_lpos = 0.54
        lgd_rpos = 0.84
        lgd_tpos = 0.85
        lgd_bpos = 0.55

    else:
        latex_vpos = 0.7
        lgd_lpos = 0.44
        lgd_rpos = 0.74
        lgd_tpos = 0.85
        lgd_bpos = 0.55
        


    lgd = c1.BuildLegend(lgd_lpos, lgd_bpos, lgd_rpos, lgd_tpos)
    lgd.SetTextFont(42)
    lgd.SetFillColorAlpha(0, 0)
    lgd.SetBorderSize(0)

    logo_tex = TLatex()
    logo_tex.SetNDC(True)
    logo_tex.SetTextSize(0.05)
    logo_tex.SetTextFont(62)
    logo_tex.DrawLatex(latex_hpos, latex_vpos, "MALTA2")
    logo_tex.SetTextFont(42)
    logo_tex.DrawLatex(latex_hpos, latex_vpos - latex_space, "Cz, 100 \mum, H-dop")
    if chip == 'W12R7':
        logo_tex.DrawLatex(latex_hpos, latex_vpos -2*latex_space, "back-metal, XDPW")
        logo_tex.DrawLatex(latex_hpos, latex_vpos-3*latex_space, "1x10^{15} 1 MeV n_{eq}/cm^{2}")

    elif chip == 'W11R0':
        logo_tex.DrawLatex(latex_hpos, latex_vpos-2*latex_space, 'XDPW')

   # logo_tex.DrawLatex(0.69, 0.55, "ITHR: %i DAC" % ithr)
    
    save_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), f'plots/Grazing_angle/{chip}')
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    
    save_file = os.path.join(save_path, f'{compare}_vs_angle_ITHR{ithr}.pdf')

    c1.Print(save_file)

    c1.Clear()

def plotting(chip, ithr, eff, eff_err, clsizex, clsizey, resx, resy):
    mg_eff = TMultiGraph()
    mg_clsizex = TMultiGraph()
    mg_clsizey = TMultiGraph()
    mg_resx = TMultiGraph()
    mg_resy = TMultiGraph()
    lwidth = 2
    msize = 2
    ithrs = [15, 20, 40, 80, 120]
    subs = [6, 9, 15, 20, 25, 30]
    angles = np.array([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60])

    (nsub, _) = np.shape(eff)
    for i in range(nsub):
        nonzero = np.count_nonzero(eff[i,:])
        if not nonzero:
            print(f'No such data at -{subs[i]} V, continue...')
            continue
        eff_np, eff_err_np = eff[i,:], eff_err[i,:]
        selected = eff_np != 0
        eff_a = array('d', eff_np[selected])
        eff_err_a = array('d', eff_err_np[selected])
        angle_a = array('d', angles[selected])

        # cluster size
        clx, cly = clsizex[i,:], clsizey[i,:]
        clsizex_a = array('d', clx[selected])
        clsizey_a = array('d', cly[selected])

        # residual distribution
        res_x, res_y = resx[i, :], resy[i, :]
        resx_a = array('d', res_x[selected])
        resy_a = array('d', res_y[selected])

        # eff vs angle
        ge_eff = TGraphErrors(len(angle_a), angle_a, eff_a, 0, eff_err_a)
        graph_setting(ge_eff, subs[i], lwidth, plot_style[1][subs[i]], plot_style[3][subs[i]], msize, plot_style[2][subs[i]], plot_style[1][subs[i]])
        mg_eff.Add(ge_eff, 'ALP')

        #residual RMS vs. angle

        g_resx = TGraph(len(angle_a), angle_a, resx_a)
        graph_setting(g_resx, subs[i], lwidth, plot_style[1][subs[i]], plot_style[3][subs[i]], msize, plot_style[2][subs[i]], plot_style[1][subs[i]])
        mg_resx.Add(g_resx, 'ALP')

        g_resy = TGraph(len(angle_a), angle_a, resy_a)
        graph_setting(g_resy, subs[i], lwidth, plot_style[1][subs[i]], plot_style[3][subs[i]], msize, plot_style[2][subs[i]], plot_style[1][subs[i]])
        mg_resy.Add(g_resy, 'ALP')

        # cluster size vs angle
        g_clx = TGraph(len(angle_a), angle_a, clsizex_a)
        graph_setting(g_clx, subs[i], lwidth, plot_style[1][subs[i]], plot_style[3][subs[i]], msize, plot_style[2][subs[i]], plot_style[1][subs[i]])
        mg_clsizex.Add(g_clx, 'ALP')

        g_cly = TGraph(len(angle_a), angle_a, clsizey_a)
        graph_setting(g_cly, subs[i], lwidth, plot_style[1][subs[i]], plot_style[3][subs[i]], msize, plot_style[2][subs[i]], plot_style[1][subs[i]])
        mg_clsizey.Add(g_cly, 'ALP')

    # Drawing
    DrawPlots(mg_eff, chip, 'Eff', 'Eff. [%]', 60, 105, ithrs[ithr])
    DrawPlots(mg_clsizex, chip, 'ClsizeX', 'Cluster size', 0, 5, ithrs[ithr])
    DrawPlots(mg_clsizey, chip, 'ClsizeY', 'Cluster size', 0.8, 2., ithrs[ithr])
    DrawPlots(mg_resx, chip, 'ResX', 'RMS_{residual}', 5, 20, ithrs[ithr])
    DrawPlots(mg_resy, chip, 'ResY', 'RMS_{residual}', 5, 20, ithrs[ithr])



def process_main(args):

    eff_data, eff_err, clsizex_data, clsizey_data, resx_data, resy_data = prepare_data(args.data_path)

    chip = args.data_path.split('/')[-1]
  
    (ithrs, _, _) = np.shape(eff_data)
    for i in range(ithrs):
        plotting(chip, i, eff_data[i,:,:], eff_err[i,:,:], clsizex_data[i,:,:], clsizey_data[i,:,:], resx_data[i,:,:], resy_data[i,:,:])











if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='depletion depth study of Malta2 with grazing angle')
    parser.add_argument('--data_path', type=str, default='../Data/W12R7', help='Data path for analysis')

    args = parser.parse_args()
    process_main(args)

