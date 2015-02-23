## THIS PROGRAM WILL USE THE PySpecKit PACKAGE TO FIT THE HALPHA LINES
## IN MY NLS1 SAMPLE

import numpy as np 
import pyspeckit as pspec
import time
import datetime

from pyspeckit import spectrum as spec
from matplotlib import pyplot as plt


# Define the file directory where the data are located
pre = '/Users/Kyle/NLS1/spectro/magellan14b/'
post = '_z.fits'

# Define region for H-alpha plotting
xmin = 6200.
xmax = 7000.

# Define the regions for the continuum fitting
ex_regions = [0, 4500, 4780, 5030, 5090, 5131, 5760, 5800, 6207, 6278, 6436, 6750, 7100, 7200]
    
# Define the initial parameters for line
Ha = 6563.
NIIa = 6550.
NIIb = 6586.
SIIa = 6718.
SIIb = 6733.

T, F = True, False

# Define the initial guesses
default_guess = [2e-16, NIIa, 10., \
    3e-16, NIIb, 10., \
    3e-16, Ha, 10., \
    1e-16, Ha, 50., \
    0.5e-16, SIIa, 10., \
    0.5e-16, SIIb, 10.]

# Define which parameters are constrained to each other
tied = ['', '', 'p[17]', \
    '', '', 'p[17]', \
    '', '', 'p[17]', \
    '', '', '', \
    '', '', 'p[17]', \
    '', '', '']

# Define the limits on each parameter
limits = [(0.1 * default_guess[0], 100.), (NIIa - 2., NIIa + 2.), (0.1, 100.), \
    (0.1 * default_guess[3], 100.), (NIIb - 2., NIIb + 2), (0.1, 100.), \
    (0.1 * default_guess[6], 100.), (Ha - 2., Ha + 2.), (0.1, 100.), \
    (0.1 * default_guess[9], 100.), (Ha - 2., Ha + 2.), (10., 100.),
    (0.1 * default_guess[12], 100.), (SIIa - 2., SIIa + 2.), (0.1, 100.), \
    (0.1 * default_guess[15], 100.), (SIIb - 2., SIIb + 2.), (0.1, 100.)]

# State whether the limit should be enforced
limited = [(T, F), (T, T), (F, T), \
    (T, F), (T, T), (F, T), \
    (T, F), (T, T), (F, T), \
    (F, F), (T, T), (T, F), \
    (T, F), (T, T), (F, T), \
    (T, F), (T, T), (F, T)]


# Prompt the user for the object base file name

spec_file = input('Enter the base file name of the spectrum: ')

print '\n Loading file, ', pre + spec_file + post

sp = spec.Spectrum(pre + spec_file + post)

print '\n Spectrum loaded '

sp.plotter()


# Fit and subtract the continuum

new_ex_reg = []

while True:

    if new_ex_reg != []:
        print '\n Using new values entered by you '
        sp.baseline(exclude = new_ex_reg, order = 1, highlight_fitregion = True)
        good = input('\n Is the continuum fit okay? (y/n) ')
    else:
        print '\n Using default wavelengths to fit and subtract the continuum '
        sp.baseline(exclude = ex_regions, order = 1, highlight_fitregion = True)
        good = input('\n Is the continuum fit okay? (y/n) ')
        
    if good == 'y' or good == 'Y':
        break
    else:
        new_ex_reg = input('\n Define regions to exclude, e.g. [4850., 4900., 6550., 6580.] \n')


# Perform the line fitting

sp.plotter(xmin = xmin, xmax = xmax)

print '\n Initialize your guesses '
print 'Format is [Amp, Centroid, Width]'
print 'Can use NIIa, NIIb, Ha, SIIa, and SIIb variables for centroids'
init_guess = input('Enter guess or enter empty list to use defaults ')

if init_guess == []:
    guess = default_guess
    init_guess = default_guess
else:
    guess = init_guess

while True:

    try:
        sp.specfit(fittype = 'gaussian', multifit = True, guesses = guess, \
               tied = tied, limits = limits, limited = limited, fit_plotted_area = True)
    except ValueError:
        print '\n Fit crashed.'
        again = input('\n Try reinitializing initial parameters and running again? (y/n) ')
        if again == 'y' or again == 'Y':
            guess = init_guess
            continue
        else:
            print '\n Quitting for now'
            break        

    good = input('\n Does this fit look good? (y/n) ')

    if good == 'y' or good == 'Y':
        break
    else:
        again = input('\n Try running again without changes? (y/n) ')
        if again == 'y' or again == 'Y':
            continue
        else:
            print '\n Input new parameters to try'
            print 'Format is [Amp, Centroid, Width]'
            print 'Can use NIIa, NIIb, Ha, SIIa, and SIIb variables for centroids'
            init_guess = input()
            
            print '\n Quitting for now'
            break

        
# Measure the lines and output the parameters

sp.measure()

print '\n The measurements on each line are: \n'

for line in sp.measurements.lines.keys():
    print line, sp.measurements.lines[line]['pos'].round(2), \
          sp.measurements.lines[line]['flux'].round(1), \
          sp.measurements.lines[line]['amp'].round(1), \
          sp.measurements.lines[line]['fwhm'].round(1)

# Print the measurements to a file

save_fit = input('\n Save the output parameters? (y/n) ')

if save_fit == 'y' or save_fit == 'Y':
    pre2 = '/Users/Kyle/NLS1/plots/pyspecfits/'
    out_file = input('\n Insert file name to write to: ')

    print '\n Warning! This will overwrite the file!'
    check = input('Are you sure? (y/n) ')

    if check == 'y' or check == 'Y':
        fout = open(pre2 + out_file, 'w')

        # Print header with date and time
        fout.write('Object ' + spec_file + '\n')
        ts = time.time()
        fout.write(datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S') + '\n')

        # Print the data
        for line in sp.measurements.lines.keys():
            fout.write(str(line) + ' ' + str(sp.measurements.lines[line]['pos'].round(2)) + \
                ' ' + str(sp.measurements.lines[line]['flux'].round(1)) + \
                ' ' + str(sp.measurements.lines[line]['amp'].round(1)) + \
                ' ' + str(sp.measurements.lines[line]['fwhm'].round(1)) )
            fout.write('\n')

        fout.close()
        print 'Wrote file ' + pre2 + out_file
        print 'Thanks for fitting! Goodbye.'

else:
    print 'Not writing a file! Goodbye.'
