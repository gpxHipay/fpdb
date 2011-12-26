#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    Copyright 2010-2011, Matthew Boss
#    
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#    
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#    
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

########################################################################

import L10n
_ = L10n.get_translation()

# TODO:
#
# -- Assumes that the currency of ring games is USD
# -- Only accepts 'realmoney="true"'
# -- A hand's time-stamp does not record seconds past the minute (a limitation of the history format)
# -- hand.maxseats can only be guessed at
# -- Cannot parse tables that run it twice
# -- Cannot parse hands in which someone is all in in one of the blinds.

import sys
import logging
from HandHistoryConverter import *
from decimal_wrapper import Decimal


class Merge(HandHistoryConverter):
    sitename = "Merge"
    filetype = "text"
    codepage = ("cp1252", "utf8")
    siteId   = 11
    copyGameHeader = True

    limits = { 'No Limit':'nl', 'No Limit ':'nl', 'Limit':'fl', 'Pot Limit':'pl', 'Pot Limit ':'pl', 'Half Pot Limit':'hp'}
    games = {              # base, category
                    'Holdem' : ('hold','holdem'),
         'Holdem Tournament' : ('hold','holdem'),
                    'Omaha'  : ('hold','omahahi'),
         'Omaha Tournament'  : ('hold','omahahi'),
               'Omaha H/L8'  : ('hold','omahahilo'),
              '2-7 Lowball'  : ('draw','27_3draw'),
              'A-5 Lowball'  : ('draw','a5_3draw'),
                   'Badugi'  : ('draw','badugi'),
           '5-Draw w/Joker'  : ('draw','fivedraw'),
                   '5-Draw'  : ('draw','fivedraw'),
                   '7-Stud'  : ('stud','studhi'),
              '7-Stud H/L8'  : ('stud','studhilo'),
                   '5-Stud'  : ('stud','5studhi'),
                     'Razz'  : ('stud','razz'),
            }
    Lim_Blinds = {      '0.04': ('0.01', '0.02'),    '0.10': ('0.02', '0.05'),
                        '0.20': ('0.05', '0.10'),    '0.50': ('0.10', '0.25'),
                        '1.00': ('0.25', '0.50'),       '1': ('0.25', '0.50'),
                        '2.00': ('0.50', '1.00'),       '2': ('0.50', '1.00'),
                        '4.00': ('1.00', '2.00'),       '4': ('1.00', '2.00'),
                        '6.00': ('1.50', '3.00'),       '6': ('1.50', '3.00'),
                        '8.00': ('2.00', '4.00'),       '8': ('2.00', '4.00'),
                       '10.00': ('2.00', '5.00'),      '10': ('2.00', '5.00'),
                       '20.00': ('5.00', '10.00'),     '20': ('5.00', '10.00'),
                       '30.00': ('10.00', '15.00'),    '30': ('10.00', '15.00'),
                       '40.00': ('10.00', '20.00'),    '40': ('10.00', '20.00'),
                       '50.00': ('10.00', '25.00'),    '50': ('10.00', '25.00'),
                       '60.00': ('15.00', '30.00'),    '60': ('15.00', '30.00'),
                      '100.00': ('25.00', '50.00'),   '100': ('25.00', '50.00'),
                  }
    
    MTT_Structures = {
                        'Monthly Charity Event - $50 Added' : {'buyIn': 2.5, 'fee': 2.5, 'currency': 'USD'},
                        'Aussie Millions Grand Final - $15,000 Package Guaranteed' : {'buyIn': 500, 'fee': 50, 'currency': 'USD'},
                        'Slim Stack $10 Tournament - Rake Free' : {'buyIn': 10, 'fee': 0, 'currency': 'USD'},
                        'Fat Stack $10 Tournament - Rake Free' : {'buyIn': 10, 'fee': 0, 'currency': 'USD'},
                        'Slim Stack $5 Tournament - Rake Free' : {'buyIn': 5, 'fee': 0, 'currency': 'USD'},
                        'Fat Stack $5 Tournament - Rake Free' : {'buyIn': 5, 'fee': 0, 'currency': 'USD'},
                        'Slim Stack $2 Tournament - Rake Free' : {'buyIn': 2, 'fee': 0, 'currency': 'USD'},
                        'Fat Stack $2 Tournament - Rake Free' : {'buyIn': 2, 'fee': 0, 'currency': 'USD'},
                        '$22 Seven Card Stud HiLo' : {'buyIn': 20, 'fee': 2, 'currency': 'USD'},
                        'Aussie Millions Satellite - 1 Rebuy' : {'buyIn': 30, 'fee': 3, 'currency': 'USD'},
                        'The Fast Fifty' : {'buyIn': 0.5, 'fee': 0.1, 'currency': 'USD'},
                        'Aussie Millions - Rebuys / Addon - 2 Entries Guaranteed!' : {'buyIn': 1, 'fee': 0.1, 'currency': 'USD'},
                        '$5 Shootout SH' : {'buyIn': 5, 'fee': 0.5, 'currency': 'USD'},
                        '$2 HA Freezeout' : {'buyIn': 2, 'fee': 0.2, 'currency': 'USD'},
                        '$60 Aussie Millions Freezeout Satellite' : {'buyIn': 55, 'fee': 5, 'currency': 'USD'},
                        '$5 Holdem Freezeout SH' : {'buyIn': 5, 'fee': 0.5, 'currency': 'USD'},
                        '$2 Bounty Turbo' : {'buyIn': 1, 'fee': 0.2, 'currency': 'USD'},
                        '$5 Heads Up Turbo' : {'buyIn': 5, 'fee': 0.5, 'currency': 'USD'},
                        '$2,000 Guranteed Freezeout' : {'buyIn': 10, 'fee': 1, 'currency': 'USD'},
                        '$100,000 Satellite - Rebuys / Addon' : {'buyIn': 10, 'fee': 1, 'currency': 'USD'},
                        'The Sixth Cent - 1 Rebuy' : {'buyIn': 0.05, 'fee': 0.01, 'currency': 'USD'},
                        '$5 Holdem SH Freezeout' : {'buyIn': 5, 'fee': 0.5, 'currency': 'USD'},
                        '$15 Bounty SH Freezeout' : {'buyIn': 10, 'fee': 1.5, 'currency': 'USD'},
                        'Daily Badugi Freezeout' : {'buyIn': 2, 'fee': 0.2, 'currency': 'USD'},
                        '$2 Holdem R/A' : {'buyIn': 2, 'fee': 0.2, 'currency': 'USD'},
                        'Dollar Frenzy Turbo! $2750 Guaranteed!' : {'buyIn': 1, 'fee': 0.1, 'currency': 'USD'},
                        '$3 PL H.O. Feezeout' : {'buyIn': 3, 'fee': 0.3, 'currency': 'USD'},
                        '$5 Daily Satellite - 1 Rebuy / 1 Addon' : {'buyIn': 5, 'fee': 0.5, 'currency': 'USD'},
                        '$3.30 NL Holdem Super Turbo - Rebuys # Addons' : {'buyIn': 3, 'fee': 0.3, 'currency': 'USD'},
                        '$5 Shootout' : {'buyIn': 5, 'fee': 0.5, 'currency': 'USD'},
                        '$11 HORSE' : {'buyIn': 10, 'fee': 1, 'currency': 'USD'},
                        'Aussie Millions - Rebuys / Addon - 2 Entries Guaranteed!' : {'buyIn': 1, 'fee': 0.1, 'currency': 'USD'},
                        '$3 PL Omaha' : {'buyIn': 3, 'fee': 0.3, 'currency': 'USD'},
                        '$60 Daily High Roller Satellite - 2 Entries Guaranteed.' : {'buyIn': 55, 'fee': 5, 'currency': 'USD'},
                        '$3 All-in or Fold BOUNTY Tournament' : {'buyIn': 1.5, 'fee': 0.3, 'currency': 'USD'},
                        '$2 Heads Up Turbo' : {'buyIn': 2, 'fee': 0.2, 'currency': 'USD'},
                        'Aussie Millions - Rebuys / Addon - 1 Entry Guaranteed!' : {'buyIn': 5, 'fee': 0.5, 'currency': 'USD'},
                        '$1 Dollar Dazzler - $300 Guaranteed' : {'buyIn': 1, 'fee': 0.1, 'currency': 'USD'},
                        '$1 Turbo Freezeout' : {'buyIn': 1, 'fee': 0.1, 'currency': 'USD'},
                        '$11 PL Omaha Freezeout' : {'buyIn': 10, 'fee': 1, 'currency': 'USD'},
                        '$1.10 NL Holdem Super Turbo - Rebuys # Addons' : {'buyIn': 1, 'fee': 0.1, 'currency': 'USD'},
                        '$100,000 Satellite - Rebuys / Addon' : {'buyIn': 1, 'fee': 0.1, 'currency': 'USD'},
                        '$5 Heads Up Shootout' : {'buyIn': 5, 'fee': 0.5, 'currency': 'USD'},
                        '$100,000 Satellite - Rebuys / Addon' : {'buyIn': 10, 'fee': 1, 'currency': 'USD'},
                        '$11 Seven Card Stud HiLo' : {'buyIn': 10, 'fee': 1, 'currency': 'USD'},
                        '$15 SH Bounty Turbo' : {'buyIn': 10, 'fee': 1.5, 'currency': 'USD'},
                        '$3 All-in or Fold Tournament' : {'buyIn': 3, 'fee': 0.3, 'currency': 'USD'},
                        '$22 PL Omaha HiLo Freezeout' : {'buyIn': 20, 'fee': 2, 'currency': 'USD'},
                        '$5 Satellite - 1R/A' : {'buyIn': 5, 'fee': 0.5, 'currency': 'USD'},
                        '$11 Daily High Roller Satellite - 1 Entry Guaranteed.' : {'buyIn': 10, 'fee': 1, 'currency': 'USD'},
                        '$5 PL Omaha Hi/Lo' : {'buyIn': 5, 'fee': 0.5, 'currency': 'USD'},
                        '$22 Seven Card Stud' : {'buyIn': 20, 'fee': 2, 'currency': 'USD'},
                        '$100,000 Satellite - Rebuys / Addon - 2 Entries Guaranteed!' : {'buyIn': 2, 'fee': 0.2, 'currency': 'USD'},
                        '$100,000 Satellite - Rebuys / Addon' : {'buyIn': 5, 'fee': 0.5, 'currency': 'USD'},
                        '$11 PL Omaha HiLo Freezeout' : {'buyIn': 10, 'fee': 1, 'currency': 'USD'},
                        'Fast Fifty Freezeout' : {'buyIn': 0.5, 'fee': 0.1, 'currency': 'USD'},
                        '$5 Heads Up Turbo' : {'buyIn': 5, 'fee': 0.5, 'currency': 'USD'},
                        '$6.60 Seven Card Stud' : {'buyIn': 6, 'fee': 0.6, 'currency': 'USD'},
                        '$2 H.A. Freezeout' : {'buyIn': 2, 'fee': 0.2, 'currency': 'USD'},
                        '$10 Bounty Turbo' : {'buyIn': 5, 'fee': 1, 'currency': 'USD'},
                        'Aussie Millions - Rebuys / Addon - 1 Entries Guaranteed!' : {'buyIn': 1, 'fee': 0.1, 'currency': 'USD'},
                        '$3 Daily High Roller Satellite - Unlimited Rebuys and Addon' : {'buyIn': 3, 'fee': 0.3, 'currency': 'USD'},
                        '$3 Holdem Freezeout' : {'buyIn': 3, 'fee': 0.3, 'currency': 'USD'},
                        '$22 PL Omaha Freezeout' : {'buyIn': 20, 'fee': 2, 'currency': 'USD'},
                        '$1 Dollar Dazzler - $350 Guaranteed' : {'buyIn': 1, 'fee': 0.1, 'currency': 'USD'},
                        '$11 Daily High Roller Satellite - R/A' : {'buyIn': 10, 'fee': 1, 'currency': 'USD'},
                        '$1.10 Seven Card Stud HiLo' : {'buyIn': 1, 'fee': 0.1, 'currency': 'USD'},
                        '$2 PL Omaha Hi/Lo' : {'buyIn': 2, 'fee': 0.2, 'currency': 'USD'},
                        '$33 Coupon Satellite - Rebuys/Addon - 2 x Entries Guaranteed' : {'buyIn': 1, 'fee': 0.1, 'currency': 'USD'},
                        '$100,000 Satellite - Rebuys / Addon' : {'buyIn': 10, 'fee': 1, 'currency': 'USD'},
                        '$11 Seven Card Stud' : {'buyIn': 10, 'fee': 1, 'currency': 'USD'},
                        '$5 Holdem SH Turbo' : {'buyIn': 5, 'fee': 0.5, 'currency': 'USD'},
                        '$2 Holdem Freezeout' : {'buyIn': 2, 'fee': 0.2, 'currency': 'USD'},
                        '$5 Daily Satellite - 1 Rebuy / 1 Addon' : {'buyIn': 5, 'fee': 0.5, 'currency': 'USD'},
                        '$3.30 Deuce to Seven Low Triple Draw' : {'buyIn': 3, 'fee': 0.3, 'currency': 'USD'},
                        '$5 Bounty Turbo' : {'buyIn': 3, 'fee': 0.5, 'currency': 'USD'},
                        'Daily Badugi Freezeout' : {'buyIn': 2, 'fee': 0.2, 'currency': 'USD'},
                        '$100,000 Satellite - 50 Cent Unlimited Rebuy Frenzy' : {'buyIn': 0.5, 'fee': 0.05, 'currency': 'USD'},
                        '$10 Freezeout SH' : {'buyIn': 10, 'fee': 1, 'currency': 'USD'},
                        '$3 Shootout SH' : {'buyIn': 3, 'fee': 0.3, 'currency': 'USD'},
                        '$2 Sunday $100,000 Satellte - R/A' : {'buyIn': 2, 'fee': 0.2, 'currency': 'USD'},
                        '$2 Holdem Freezeout' : {'buyIn': 2, 'fee': 0.2, 'currency': 'USD'},
                        '$3 H.A. Freezeout' : {'buyIn': 3, 'fee': 0.3, 'currency': 'USD'},
                        '$1 Dollar Dazzler - $400 Guaranteed' : {'buyIn': 1, 'fee': 0.1, 'currency': 'USD'},
                        '$3.30 Seven Card Stud HiLo' : {'buyIn': 3, 'fee': 0.3, 'currency': 'USD'},
                        '$1 Establishing' : {'buyIn': 1, 'fee': 0.1, 'currency': 'USD'},
                        '$100,000 Satellite - Rebuys / Addon' : {'buyIn': 10, 'fee': 1, 'currency': 'USD'},
                        '$5 Holdem Turbo SH' : {'buyIn': 5, 'fee': 0.5, 'currency': 'USD'},
                        'Fast Fifty Freezeout' : {'buyIn': 0.5, 'fee': 0.1, 'currency': 'USD'},
                        '$4 PL Omaha' : {'buyIn': 4, 'fee': 0.4, 'currency': 'USD'},
                        '$100,000 Satellite - Rebuys / Addon' : {'buyIn': 10, 'fee': 1, 'currency': 'USD'},
                        '$5 Daily Satellite - 1 Rebuy / 1 Addon' : {'buyIn': 5, 'fee': 0.5, 'currency': 'USD'},
                        '$3 All-in or Fold Tournament' : {'buyIn': 3, 'fee': 0.3, 'currency': 'USD'},
                        '$1 Limit Badugi' : {'buyIn': 1, 'fee': 0.1, 'currency': 'USD'},
                        '$5 Shootout (10 Handed)' : {'buyIn': 5, 'fee': 0.5, 'currency': 'USD'},
                        '$5 Holdem Turbo' : {'buyIn': 5, 'fee': 0.5, 'currency': 'USD'},
                        '$3 Holdem (50 Max)' : {'buyIn': 3, 'fee': 0.3, 'currency': 'USD'},
                        '$2 Limit H.O.R.S.E' : {'buyIn': 2, 'fee': 0.2, 'currency': 'USD'},
                        '$100,000 Satellite - Rebuys / Addon - 5 Entries Guaranteed!' : {'buyIn': 1, 'fee': 0.1, 'currency': 'USD'},
                        '$2 Holdem Turbo' : {'buyIn': 2, 'fee': 0.2, 'currency': 'USD'},
                        '$5 Holdem SH Turbo' : {'buyIn': 5, 'fee': 0.5, 'currency': 'USD'},
                        'The Quarter Quicky - $25 Guaranteed' : {'buyIn': 0.25, 'fee': 0.05, 'currency': 'USD'},
                        '$100,000 Satellite - Rebuys / Addon' : {'buyIn': 10, 'fee': 1, 'currency': 'USD'},
                        'Daily Badugi Freezeout' : {'buyIn': 2, 'fee': 0.2, 'currency': 'USD'},
                        '$15 Bounty SH' : {'buyIn': 10, 'fee': 1.5, 'currency': 'USD'},
                        '$1 Heads Up Turbo' : {'buyIn': 1, 'fee': 0.1, 'currency': 'USD'},
                        '$3 PL Omaha' : {'buyIn': 3, 'fee': 0.3, 'currency': 'USD'},
                        '$5 Holdem Turbo SH' : {'buyIn': 5, 'fee': 0.5, 'currency': 'USD'},
                        '$3 Holdem Freezeout' : {'buyIn': 3, 'fee': 0.3, 'currency': 'USD'},
                        'Fast Fifty Freezeout' : {'buyIn': 0.5, 'fee': 0.1, 'currency': 'USD'},
                        '$2 Holdem R/A' : {'buyIn': 2, 'fee': 0.2, 'currency': 'USD'},
                        '$5 Daily Satellite - 1 Rebuy / 1 Addon' : {'buyIn': 5, 'fee': 0.5, 'currency': 'USD'},
                        '$3 Bounty Turbo Freezeout' : {'buyIn': 2, 'fee': 0.3, 'currency': 'USD'},
                        '$5 H.A. Freezeout' : {'buyIn': 5, 'fee': 0.5, 'currency': 'USD'},
                        '$2 Heads Up Freezeout' : {'buyIn': 2, 'fee': 0.2, 'currency': 'USD'},
                        'Daily Badugi Freezeout' : {'buyIn': 2, 'fee': 0.2, 'currency': 'USD'},
                        '$2.20 Daily Satellite - R/A' : {'buyIn': 2, 'fee': 0.2, 'currency': 'USD'},
                        '$5 PL Holdem Turbo' : {'buyIn': 5, 'fee': 0.5, 'currency': 'USD'},
                        '$5 Bounty SH' : {'buyIn': 3, 'fee': 0.5, 'currency': 'USD'},
                        'The Quarter Quicky - $25 Guaranteed' : {'buyIn': 0.25, 'fee': 0.05, 'currency': 'USD'},
                        '$3 PL Omaha Hi/Lo' : {'buyIn': 3, 'fee': 0.3, 'currency': 'USD'},
                        '$2 Satellite - R/A' : {'buyIn': 2, 'fee': 0.2, 'currency': 'USD'},
                        'Ladies Only $250 Guaranteed Turbo with R/A' : {'buyIn': 2, 'fee': 0.2, 'currency': 'USD'},
                        'Ladies Only $100 Guaranteed Freezeout' : {'buyIn': 2, 'fee': 0.2, 'currency': 'USD'},
                        'Sunday $100,000 Guaranteed Freezeout' : {'buyIn': 100, 'fee': 9, 'currency': 'USD'},
                        'Ladies Only $250 Guaranteed Freezeout' : {'buyIn': 3, 'fee': 0.3, 'currency': 'USD'},
                        '$900 Guaranteed - 1 Rebuy / 1 Addon' : {'buyIn': 10, 'fee': 1, 'currency': 'USD'},
                        '$3,750 Guaranteed Turbo - 1 Rebuy / 1 Addon' : {'buyIn': 10, 'fee': 1, 'currency': 'USD'},
                        '$2,250 Guaranteed - 1 Rebuy / 1 Addon' : {'buyIn': 5, 'fee': 0.5, 'currency': 'USD'},
                        '$4,250 Guaranteed NightOwl Freezeout' : {'buyIn': 20, 'fee': 2, 'currency': 'USD'},
                        '$7,000 Guaranteed Turbo - 1 Rebuy / 1 Addon' : {'buyIn': 30, 'fee': 3, 'currency': 'USD'},
                        '$6,500 Guaranteed - 2 Rebuys / 1 Addon' : {'buyIn': 10, 'fee': 1, 'currency': 'USD'},
                        '$3,000 Guaranteed Deepstack Turbo Freezeout' : {'buyIn': 55, 'fee': 5, 'currency': 'USD'},
                        '$1,000 Guaranteed Freezeout' : {'buyIn': 5, 'fee': 0.5, 'currency': 'USD'},
                        '$10,000 Guaranteed Shorthand Turbo - Rebuys / Addon' : {'buyIn': 20, 'fee': 2, 'currency': 'USD'},
                        '$8,000 Guaranteed - Rebuys / Addon' : {'buyIn': 75, 'fee': 7, 'currency': 'USD'},
                        '$3,000 Guaranteed Freezeout' : {'buyIn': 40, 'fee': 4, 'currency': 'USD'},
                        '$4,000 Guaranteed Freezeout' : {'buyIn': 15, 'fee': 1.5, 'currency': 'USD'},
                        '$1,000 PL Omaha HiLo Guaranteed Freezeout' : {'buyIn': 20, 'fee': 2, 'currency': 'USD'},
                        '$8,000 Guaranteed - Rebuys / Addon' : {'buyIn': 30, 'fee': 3, 'currency': 'USD'},
                        '$2,000 Guaranteed Deepstack Turbo Freezeout' : {'buyIn': 10, 'fee': 1, 'currency': 'USD'},
                        '$100 Guaranteed - $2 Bounty Turbo' : {'buyIn': 1, 'fee': 0.2, 'currency': 'USD'},
                        '$2,250 Guaranteed Freezeout - Short Handed' : {'buyIn': 25, 'fee': 2.5, 'currency': 'USD'},
                        '$500 Guaranteed Deepstack Turbo Freezeout' : {'buyIn': 3, 'fee': 0.3, 'currency': 'USD'},
                        '$1,150 PLO HiLo Guaranteed Freezeout Deepstack' : {'buyIn': 10, 'fee': 1, 'currency': 'USD'},
                        '$1,200 Guaranteed PLO - Rebuys / Addon' : {'buyIn': 10, 'fee': 1, 'currency': 'USD'},
                        '$750 Guaranteed Freezeout' : {'buyIn': 5, 'fee': 0.5, 'currency': 'USD'},
                        '$10,000 Daily High Roller Guaranteed Freezeout' : {'buyIn': 200, 'fee': 15, 'currency': 'USD'},
                        '$4,500 Guaranteed - Rebuys / Addon' : {'buyIn': 3, 'fee': 0.3, 'currency': 'USD'},
                        '$3,000 Guaranteed Freezeout' : {'buyIn': 55, 'fee': 5, 'currency': 'USD'},
                        '$2,000 PL Omaha HiLo Guaranteed - Rebuys / Addon' : {'buyIn': 10, 'fee': 1, 'currency': 'USD'},
                        '$300 Stud Guaranteed Freezeout' : {'buyIn': 5, 'fee': 0.5, 'currency': 'USD'},
                        '$5,000 Guaranteed Freezeout' : {'buyIn': 30, 'fee': 3, 'currency': 'USD'},
                        '$2,000 Guaranteed Freezeout' : {'buyIn': 10, 'fee': 1, 'currency': 'USD'},
                        '$100 Guaranteed Deepstack Turbo Freezeout' : {'buyIn': 1, 'fee': 0.1, 'currency': 'USD'},
                        '$2,500 Guaranteed - $11 Unlimited Rebuys and Addon!' : {'buyIn': 10, 'fee': 1, 'currency': 'USD'},
                        '$9,500 Guaranteed Turbo - 1 Rebuy / 1 Addon' : {'buyIn': 40, 'fee': 4, 'currency': 'USD'},
                        '$100 Guaranteed - $2 Bounty Turbo' : {'buyIn': 1, 'fee': 0.2, 'currency': 'USD'},
                        '$4,000 Guaranteed Freezeout' : {'buyIn': 20, 'fee': 2, 'currency': 'USD'},
                        '$750 Guaranteed Deepstack Turbo Freezeout' : {'buyIn': 5, 'fee': 0.5, 'currency': 'USD'},
                        '$2,500 Guaranteed - Rebuys / Addon' : {'buyIn': 3, 'fee': 0.3, 'currency': 'USD'},
                        '$5,500 Guaranteed - 1 Rebuy / 1 Addon' : {'buyIn': 100, 'fee': 9, 'currency': 'USD'},
                        '$4,000 Guaranteed - 1 Rebuy / 1 Addon' : {'buyIn': 10, 'fee': 1, 'currency': 'USD'},
                        '$100 Guaranteed - $3 Holdem SH Turbo' : {'buyIn': 3, 'fee': 0.3, 'currency': 'USD'},
                        '$3,250 Guaranteed Freezeout' : {'buyIn': 10, 'fee': 1, 'currency': 'USD'},
                        '$750 Guaranteed Deepstack Turbo Freezeout' : {'buyIn': 3, 'fee': 0.3, 'currency': 'USD'},
                        '$1,500 Guaranteed Freezeout' : {'buyIn': 20, 'fee': 2, 'currency': 'USD'},
                        '$8,500 Guaranteed - Rebuys / Addon' : {'buyIn': 55, 'fee': 5, 'currency': 'USD'},
                        '$750 Guaranteed Bounty Freezeout' : {'buyIn': 10, 'fee': 1.5, 'currency': 'USD'},
                        '$1,500 Guaranteed Freezeout - Short Handed' : {'buyIn': 55, 'fee': 5, 'currency': 'USD'},
                        '$5,000 Guaranteed Turbo - Rebuys / Addon' : {'buyIn': 5, 'fee': 0.5, 'currency': 'USD'},
                        '$1,500 Guaranteed Freezeout' : {'buyIn': 15, 'fee': 1.5, 'currency': 'USD'},
                        '$6,000 Guaranteed - 2 Rebuys / 1 Addon' : {'buyIn': 30, 'fee': 3, 'currency': 'USD'},
                        '$1,500 Guaranteed PLO Hi-Lo - Rebuys / Addon' : {'buyIn': 5, 'fee': 0.5, 'currency': 'USD'},
                        '$300 Guaranteed Bounty Freezeout' : {'buyIn': 3, 'fee': 0.5, 'currency': 'USD'},
                        '$1,750 Guaranteed Freezeout' : {'buyIn': 20, 'fee': 2, 'currency': 'USD'},
                        '$3,000 Guaranteed Turbo - Rebuys / Addon' : {'buyIn': 3, 'fee': 0.3, 'currency': 'USD'},
                        '$3,500 Guaranteed Freezeout' : {'buyIn': 55, 'fee': 5, 'currency': 'USD'},
                        '$1,000 Guaranteed Freezeout' : {'buyIn': 10, 'fee': 1, 'currency': 'USD'},
                        '$400 Guaranteed - PL Omaha HiLo' : {'buyIn': 6, 'fee': 0.6, 'currency': 'USD'},
                        '$3,000 Guaranteed - Rebuys / Addon' : {'buyIn': 5, 'fee': 0.5, 'currency': 'USD'},
                        '$200 Guaranteed Deepstack Turbo Freezeout' : {'buyIn': 1, 'fee': 0.1, 'currency': 'USD'},
                        '$2,500 Guaranteed Freezeout' : {'buyIn': 20, 'fee': 2, 'currency': 'USD'},
                        '$100 Guaranteed - $2 Bounty Turbo' : {'buyIn': 1, 'fee': 0.2, 'currency': 'USD'},
                        'Ladies Only $300 Guaranteed R/A' : {'buyIn': 2, 'fee': 0.2, 'currency': 'USD'},
                        '$2,000 Guaranteed Deepstack Freezeout' : {'buyIn': 10, 'fee': 1, 'currency': 'USD'},
                        '$300 Guaranteed - Bounty Freezeout' : {'buyIn': 5, 'fee': 1, 'currency': 'USD'},
                        '$3,000 Guaranteed - Rebuys / Addon' : {'buyIn': 4, 'fee': 0.4, 'currency': 'USD'},
                        '$1,500 Guaranteed Freezeout' : {'buyIn': 15, 'fee': 1.5, 'currency': 'USD'},
                        '$1,500 Guaranteed - Rebuys / Addon' : {'buyIn': 2, 'fee': 0.2, 'currency': 'USD'},
                        '$700 Guaranteed Freezeout' : {'buyIn': 10, 'fee': 1, 'currency': 'USD'},
                        '$700 Guaranteed Freezeout' : {'buyIn': 10, 'fee': 1, 'currency': 'USD'},
                        '$900 Guaranteed - 1 Rebuy / 1 Addon' : {'buyIn': 5, 'fee': 0.5, 'currency': 'USD'},
                        '$700 Guaranteed Freezeout' : {'buyIn': 10, 'fee': 1, 'currency': 'USD'},
                        '$900 Guaranteed - 1 Rebuy / 1 Addon' : {'buyIn': 10, 'fee': 1, 'currency': 'USD'},
                        '$1,250 Guaranteed - Rebuys / Addon' : {'buyIn': 20, 'fee': 2, 'currency': 'USD'},
                        '$150 Guaranteed - Bounty Freezeout' : {'buyIn': 5, 'fee': 1, 'currency': 'USD'},
                        '$2,250 Guaranteed - 3 Rebuys / 1 Addon' : {'buyIn': 30, 'fee': 3, 'currency': 'USD'},
                        '$300 Guaranteed Pot Limit HO - Unlimited Rebuys/Addon' : {'buyIn': 5, 'fee': 0.5, 'currency': 'USD'},
                        '$500 Guaranteed Deepstack Turbo Freezeout' : {'buyIn': 10, 'fee': 1, 'currency': 'USD'},
                        '$300 Guaranteed - NLH Shorthanded' : {'buyIn': 3, 'fee': 0.3, 'currency': 'USD'},
                        '$750 Guaranteed Freezeout' : {'buyIn': 5, 'fee': 0.5, 'currency': 'USD'},
                        '$3,000 Guaranteed Turbo - 1 Rebuy / 1 Addon' : {'buyIn': 10, 'fee': 1, 'currency': 'USD'},
                        '$2,000 Guaranteed - 1 Rebuy / 1 Addon' : {'buyIn': 5, 'fee': 0.5, 'currency': 'USD'},
                        '$2,000 Guaranteed Deepstack Turbo Freezeout' : {'buyIn': 10, 'fee': 1, 'currency': 'USD'},
                        '$4,000 Guaranteed NightOwl Freezeout' : {'buyIn': 20, 'fee': 2, 'currency': 'USD'},
                        '$7,000 Guaranteed Turbo - 1 Rebuy / 1 Addon' : {'buyIn': 30, 'fee': 3, 'currency': 'USD'},
                        '$2,000 VIP Freeroll' : {'buyIn': 0, 'fee': 0, 'currency': 'USD'},
                        '$1,500 VIP Freeroll' : {'buyIn': 0, 'fee': 0, 'currency': 'USD'},
                        '$3,500 VIP Freeroll' : {'buyIn': 0, 'fee': 0, 'currency': 'USD'},
                        '$750 VIP Freeroll' : {'buyIn': 0, 'fee': 0, 'currency': 'USD'},
                        '$2,500 VIP Freeroll' : {'buyIn': 0, 'fee': 0, 'currency': 'USD'},
                        '$200 Freeroll - NL Holdem - 20:00' : {'buyIn': 0, 'fee': 0, 'currency': 'USD'},
                        '$200 Freeroll - PL Omaha - 18:00' : {'buyIn': 0, 'fee': 0, 'currency': 'USD'},
                        '100 Seats to $100k Freeroll' : {'buyIn': 0, 'fee': 0, 'currency': 'USD'},
                        'Daily First Deposit Freeroll - Saturday' : {'buyIn': 0, 'fee': 0, 'currency': 'USD'},
                        '$200 Freeroll - HORSE - 12:00' : {'buyIn': 0, 'fee': 0, 'currency': 'USD'},
                        '$200 Freeroll - NL Holdem - 06:00' : {'buyIn': 0, 'fee': 0, 'currency': 'USD'},
                        '$200 Freeroll - NL Holdem - 00:00' : {'buyIn': 0, 'fee': 0, 'currency': 'USD'} 
                     }
    
    SnG_Structures = {  '$1 NL Holdem Double Up - 10 Handed'    : {'buyIn': 1,   'fee': 0.08, 'currency': 'USD', 'seats': 10, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (2,2,2,2,2)},
                        '$10 Bounty SnG - 10 Handed'            : {'buyIn': 5,   'fee': 1,    'currency': 'USD', 'seats': 10, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (25, 15, 10)},
                        '$10 NL Holdem Double Up - 10 Handed'   : {'buyIn': 10,  'fee': 0.8,  'currency': 'USD', 'seats': 10, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (20,20,20,20,20)},
                        '$10 PL Omaha Double Up - 10 Handed'    : {'buyIn': 10,  'fee': 0.8,  'currency': 'USD', 'seats': 10, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (20,20,20,20,20)},
                        '$10 Winner Takes All - $60 Coupon'     : {'buyIn': 10,  'fee': 0.8,  'currency': 'USD', 'seats': 6,  'multi': False, 'payoutCurrency': 'USD', 'payouts': (60,)},
                        '$100 Bounty SnG - 6 Handed'            : {'buyIn': 100, 'fee': 9,    'currency': 'USD', 'seats': 6,  'multi': False, 'payoutCurrency': 'USD', 'payouts': (315, 135)},
                        '$100 NL Holdem Double Up - 10 Handed'  : {'buyIn': 100, 'fee': 8,    'currency': 'USD', 'seats': 10, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (200,200,200,200,200)},
                        '$100 PL Omaha Double Up - 10 Handed'   : {'buyIn': 100, 'fee': 8,    'currency': 'USD', 'seats': 10, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (200,200,200,200,200)},
                        '$100,000 Guaranteed - Super Turbo Satellite' : {'buyIn': 38.8, 'fee': 0.8, 'currency': 'USD', 'seats': 6, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (109,109,11,3.8)},
                        '$10 Bounty SnG - 6 Handed'             : {'buyIn': 5, '  fee': 1,    'currency': 'USD', 'seats': 6,  'multi': False, 'payoutCurrency': 'USD', 'payouts': (25, 15, 10)},
                        '$10 Satellite'                         : {'buyIn': 10,  'fee': 1,    'currency': 'USD', 'seats': 6,  'multi': False, 'payoutCurrency': 'USD', 'payouts': (60,)},
                        '$100 Bounty SnG - 6 Handed'            : {'buyIn': 100, 'fee': 9,    'currency': 'USD', 'seats': 6,  'multi': False, 'payoutCurrency': 'USD', 'payouts': (315, 135)},
                        '$2 Bounty SnG - 10 Handed'             : {'buyIn': 2,   'fee': 0.2,  'currency': 'USD', 'seats': 10, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (5, 3, 2)},
                        '$2 Bounty SnG - 6 Handed'              : {'buyIn': 2,   'fee': 0.2,  'currency': 'USD', 'seats': 6,  'multi': False, 'payoutCurrency': 'USD', 'payouts': (5, 3, 2)},
                        '$2 NL Holdem All-In or Fold 10 - Handed' : {'buyIn': 2,   'fee': 0.16, 'currency': 'USD', 'seats': 10, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (10,6,4)},
                        '$2 NL Holdem Double Up - 10 Handed'    : {'buyIn': 2,   'fee': 0.16, 'currency': 'USD', 'seats': 10, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (4,4,4,4,4)},
                        '$2 Satellite'                          : {'buyIn': 2,   'fee': 0.2,  'currency': 'USD', 'seats': 5,  'multi': False, 'payoutCurrency': 'USD', 'payouts': (11,)},
                        '$20 Bounty SnG - 10 Handed'            : {'buyIn': 20,  'fee': 2,    'currency': 'USD', 'seats': 10, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (50, 30, 30)},
                        '$20 Bounty SnG - 6 Handed'             : {'buyIn': 20,  'fee': 2,    'currency': 'USD', 'seats': 6,  'multi': False, 'payoutCurrency': 'USD', 'payouts': (50, 30, 30)},
                        '$20 Daily Deep Stack Satellite'        : {'buyIn': 20,  'fee': 2,    'currency': 'USD', 'seats': 6,  'multi': False, 'payoutCurrency': 'USD', 'payouts': (109, 11)},
                        '$20 NL Holdem Double Up - 10 Handed'   : {'buyIn': 20,  'fee': 1.6,  'currency': 'USD', 'seats': 10, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (40,40,40,40,40)},
                        '$3 NL Holdem Double Up - 10 Handed'    : {'buyIn': 3,   'fee': 0.24, 'currency': 'USD', 'seats': 10, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (6,6,6,6,6)},
                        '$30 Bounty SnG - 6 Handed'             : {'buyIn': 30,  'fee': 3,    'currency': 'USD', 'seats': 6,  'multi': False, 'payoutCurrency': 'USD', 'payouts': (84, 36)},
                        '$5 Bounty SnG - 10 Handed'             : {'buyIn': 5,   'fee': 0.5,  'currency': 'USD', 'seats': 10, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (12.50, 7.50, 5)},
                        '$5 Bounty SnG - 6 Handed'              : {'buyIn': 5,   'fee': 0.5,  'currency': 'USD', 'seats': 6,  'multi': False, 'payoutCurrency': 'USD', 'payouts': (14, 6)},
                        '$5 NL Holdem Double Up - 6 Handed'     : {'buyIn': 5,   'fee': 0.4,  'currency': 'USD', 'seats': 6,  'multi': False, 'payoutCurrency': 'USD', 'payouts': (10,10,10)},
                        '$5 NL Holdem Double Up - 10 Handed'    : {'buyIn': 5,   'fee': 0.4,  'currency': 'USD', 'seats': 10, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (10,10,10,10,10)},
                        '$5 PL Omaha Double Up - 10 Handed'     : {'buyIn': 5,   'fee': 0.4,  'currency': 'USD', 'seats': 10, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (10,10,10,10,10)},
                        '$50 NL Holdem Double Up - 10 Handed'   : {'buyIn': 50,  'fee': 4,    'currency': 'USD', 'seats': 10, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (10,10,10,10,10)},
                        '$50 PL Omaha Double Up - 10 Handed'    : {'buyIn': 50,  'fee': 4,    'currency': 'USD', 'seats': 10, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (10,10,10,10,10)},
                        '$55 Turbo - 6 Max'                     : {'buyIn': 50,  'fee': 4,    'currency': 'USD', 'seats': 6,  'multi': False, 'payoutCurrency': 'USD', 'payouts': (210, 90)},
                        '$60 Daily High Roller SnG Satellite'   : {'buyIn': 55,  'fee': 5,    'currency': 'USD', 'seats': 6,  'multi': False, 'payoutCurrency': 'USD', 'payouts': (215, 115)},
                        '$75 Bounty SnG - 6 Handed'             : {'buyIn': 75,  'fee': 7.5,  'currency': 'USD', 'seats': 6,  'multi': False, 'payoutCurrency': 'USD', 'payouts': (210, 90)},
                        '$82 Turbo - 6 Max'                     : {'buyIn': 75,  'fee': 7,    'currency': 'USD', 'seats': 6,  'multi': False, 'payoutCurrency': 'USD', 'payouts': (315, 135)},
                        '100 VIP Point SnG'                     : {'buyIn': 1,   'fee': 0.05, 'currency': 'USD', 'seats': 6,  'multi': False, 'payoutCurrency': 'USD', 'payouts': (0,0)},
                        '250 VIP Point SnG'                     : {'buyIn': 2.5, 'fee': 0.15, 'currency': 'USD', 'seats': 6,  'multi': False, 'payoutCurrency': 'USD', 'payouts': (0,0)},
                        '500 VIP Point SnG'                     : {'buyIn': 5,   'fee': 0.25, 'currency': 'USD', 'seats': 6,  'multi': False, 'payoutCurrency': 'USD', 'payouts': (0,0)},
                        'Aardvark Room'                         : {'buyIn': 10,  'fee': 1,    'currency': 'USD', 'seats': 9,  'multi': False, 'payoutCurrency': 'USD', 'payouts': (45,27,18)},
                        'Alligator Room - Heads Up'             : {'buyIn': 100, 'fee': 4.5,  'currency': 'USD', 'seats': 2,  'multi': False, 'payoutCurrency': 'USD', 'payouts': (200,)},
                        'Alligator Room - Turbo Heads Up'       : {'buyIn': 110, 'fee': 4.5,  'currency': 'USD', 'seats': 2,  'multi': False, 'payoutCurrency': 'USD', 'payouts': (220,)},
                        'Alpaca Room - Turbo'                   : {'buyIn': 10,  'fee': 1,    'currency': 'USD', 'seats': 6,  'multi': False, 'payoutCurrency': 'USD', 'payouts': (42, 18)},
                        'Anaconda Room - Heads Up'              : {'buyIn': 100, 'fee': 4.5,  'currency': 'USD', 'seats': 2,  'multi': False, 'payoutCurrency': 'USD', 'payouts': (200,)},
                        'Anaconda Room - Turbo Heads Up'        : {'buyIn': 110, 'fee': 4.5,  'currency': 'USD', 'seats': 2,  'multi': False, 'payoutCurrency': 'USD', 'payouts': (220,)},
                        'Anteater Room'                         : {'buyIn': 10,  'fee': 1,    'currency': 'USD', 'seats': 6,  'multi': False, 'payoutCurrency': 'USD', 'payouts': (42, 18)},
                        'Antelope Room'                         : {'buyIn': 5,   'fee': 0.5,  'currency': 'USD', 'seats': 6,  'multi': False, 'payoutCurrency': 'USD', 'payouts': (21, 9)},
                        'Arctic Fox Room - Heads Up'            : {'buyIn': 2,   'fee': 0.1, ' currency': 'USD', 'seats': 2,  'multi': False, 'payoutCurrency': 'USD', 'payouts': (4,)},
                        'Armadillo Room'                        : {'buyIn': 20,  'fee': 2,    'currency': 'USD', 'seats': 10, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (100, 60, 40)},
                        'Aussie Millions - Super Turbo Satelite': {'buyIn': 10,  'fee': 1,    'currency': 'USD', 'seats': 6,  'multi': False, 'payoutCurrency': 'USD', 'payouts': (60,)},
                        'Axolotyl Room - Heads Up'              : {'buyIn': 30,  'fee': 1.5,  'currency': 'USD', 'seats': 2,  'multi': False, 'payoutCurrency': 'USD', 'payouts': (60,)},
                        'Axolotyl Room - Turbo Heads Up'        : {'buyIn': 33,  'fee': 1.5,  'currency': 'USD', 'seats': 2,  'multi': False, 'payoutCurrency': 'USD', 'payouts': (66,)},
                        'Badger Room'                           : {'buyIn': 10,  'fee': 1, 'currency': 'USD', 'seats': 10, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (50, 30, 20)},
                        'Bandicoot Room'                        : {'buyIn': 2,   'fee': 0.2, 'currency': 'USD', 'seats': 6, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (8.40, 3.60)},
                        'Bear Room'                             : {'buyIn': 50,  'fee': 5, 'currency': 'USD', 'seats': 6, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (210, 90)},
                        'Bear Room - Heads Up'                  : {'buyIn': 200, 'fee': 9, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (400,)},
                        'Bear Room - Turbo Heads Up'            : {'buyIn': 220, 'fee': 9, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (440,)},
                        'Beaver Room'                           : {'buyIn': 5, '  fee': 0.5, 'currency': 'USD', 'seats': 6, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (21, 9)},
                        'Beaver Room 12 min levels'             : {'buyIn': 5,   'fee': 0.5, 'currency': 'USD', 'seats': 6, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (21, 9)},
                        'Beaver Room 12 min levels Short Handed' : {'buyIn': 5, 'fee': 0.5, 'currency': 'USD', 'seats': 6, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (21, 9)},
                        'Bilby Room - Heads Up'                 : {'buyIn': 5, 'fee': 0.25, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (10,)},
                        'Bilby Room - Turbo Heads Up'           : {'buyIn': 7, 'fee': 0.25, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (14,)},
                        'Bison Room - Heads Up'                 : {'buyIn': 50, 'fee': 2.5, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (100,)},
                        'Bison Room - Turbo Heads Up'           : {'buyIn': 55, 'fee': 2.5, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (110,)},
                        'Black Bear Room Turbo Heads Up (4 players)' : {'buyIn': 4, 'fee': 0.6, 'currency': 'USD', 'seats': 4, 'multi': True, 'payoutCurrency': 'USD', 'payouts': (48,)},
                        'Black Mamba Room - Super Turbo'        : {'buyIn': 12, 'fee': 52, 'currency': 'USD', 'seats': 2, 'multi': True, 'payoutCurrency': 'USD', 'payouts': (312, 187.2, 124.8)},
                        'Boar Room - Heads Up'                  : {'buyIn': 20, 'fee': 1, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (40,)},
                        'Boar Room - Turbo Heads Up'            : {'buyIn': 22, 'fee': 1, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (44,)},
                        'Bobcat Room'                           : {'buyIn': 20, 'fee': 2, 'currency': 'USD', 'seats': 6, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (84, 36)},
                        'Botfly Room - Super Turbo HU'          : {'buyIn': 8, 'fee': 0.2, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (16,)},
                        'Buffalo Room'                          : {'buyIn': 10, 'fee': 1, 'currency': 'USD', 'seats': 6, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (42, 18)},
                        'Buffalo Room - Heads Up'               : {'buyIn': 300, 'fee': 12, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (600,)},
                        'Buffalo Room - Turbo Heads Up'         : {'buyIn': 330, 'fee': 12, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (660,)},
                        'Bumblebee Room - Super Turbo'          : {'buyIn': 0.1, 'fee': 0.01, 'currency': 'USD', 'seats': 6, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (0.42, 0.18)},
                        'Bunyip Room - Heads Up'                : {'buyIn': 100, 'fee': 4.5, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (200,)},
                        'Bushmaster Room Super Turbo HU'        : {'buyIn': 250, 'fee': 4, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (500,)},
                        'Caiman Room'                           : {'buyIn': 20, 'fee': 2, 'currency': 'USD', 'seats': 6, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (84, 36)},
                        'Camel Room'                            : {'buyIn': 10, 'fee': 1, 'currency': 'USD', 'seats': 6, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (42, 18)},
                        'Cape Hunting Dog Room'                 : {'buyIn': 2, 'fee': 0.2, 'currency': 'USD', 'seats': 45, 'multi': True, 'payoutCurrency': 'USD', 'payouts': (27.90, 19.35, 14.85, 11.25, 8.10, 5.40, 3.15)},
                        'Capra room - Heads Up'                 : {'buyIn': 5, 'fee': 0.25, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (10,)},
                        'Capybara Room'                         : {'buyIn': 5, 'fee': 0.5, 'currency': 'USD', 'seats': 6, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (21, 9)},
                        'Cassowary Room'                        : {'buyIn': 5, 'fee': 0.5, 'currency': 'USD', 'seats': 10, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (25, 15, 10)},
                        'Cobra Room - Heads Up'                 : {'buyIn': 10, 'fee': 0.5, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (20,)},
                        'Cobra Room - Turbo Heads Up'           : {'buyIn': 11, 'fee': 0.5, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (22,)},
                        'Condor Room - Heads Up'                : {'buyIn': 30, 'fee': 1.5, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (60,)},
                        'Condor Room - Turbo Heads Up'          : {'buyIn': 33, 'fee': 1.5, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (66,)},
                        'Conga Eel Room - Super Turbo HU'       : {'buyIn': 120, 'fee': 2.3, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (240,)},
                        'Cougar Room - Heads Up'                : {'buyIn': 20, 'fee': 1, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (40,)},
                        'Cougar Room - Turbo Heads Up'          : {'buyIn': 22, 'fee': 1, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (44,)},
                        'Coyote Room - Super Turbo'             : {'buyIn': 50, 'fee': 2, 'currency': 'USD', 'seats': 6, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (210, 90)},
                        'Cricket Room - Super Turbo 6 Max'      : {'buyIn': 2, 'fee': 0.2, 'currency': 'USD', 'seats': 18, 'multi': True, 'payoutCurrency': 'USD', 'payouts': (14.40, 10.8, 7.2, 3.6)},
                        'Crocodile Room'                        : {'buyIn': 5, 'fee': 0.5, 'currency': 'USD', 'seats': 18, 'multi': True, 'payoutCurrency': 'USD', 'payouts': (36, 27, 18, 9)},
                        'Daily High Roller - Super Turbo Satellite' : {'buyIn': 72, 'fee': 1.3, 'currency': 'USD', 'seats': 6, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (215, 215, 2)},
                        'Dingo Room - Heads Up'                 : {'buyIn': 50, 'fee': 2.5, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (100,)},
                        'Dingo Room - Turbo Heads Up'           : {'buyIn': 55, 'fee': 2.5, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (110,)},
                        'Dollar Dazzler Turbo'                  : {'buyIn': 1, 'fee': 0.1, 'currency': 'USD', 'seats': 10, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (5, 3, 2)},
                        'Dolphin Room'                          : {'buyIn': 2, 'fee': 0.2, 'currency': 'USD', 'seats': 10, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (10, 6, 4)},
                        'Dragon Room'                           : {'buyIn': 100, 'fee': 9, 'currency': 'USD', 'seats': 6, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (420, 180)},
                        'Dragonfly Room - Super Turbo'          : {'buyIn': 2, 'fee': 0.12, 'currency': 'USD', 'seats': 6, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (8.40, 3.60)},
                        'Dugong Room'                           : {'buyIn': 50, 'fee': 5, 'currency': 'USD', 'seats': 9, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (225, 135, 90)},
                        'Eagle Room'                            : {'buyIn': 10, 'fee': 1, 'currency': 'USD', 'seats': 6, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (42, 18)},
                        'Eagle Room 12 min levels'              : {'buyIn': 10, 'fee': 1, 'currency': 'USD', 'seats': 10, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (50, 30, 20)},
                        'Eagle Room 12 min levels Short Handed' : {'buyIn': 10, 'fee': 1, 'currency': 'USD', 'seats': 6, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (42, 18)},
                        'Echidna Room'                          : {'buyIn': 5, 'fee': 0.5, 'currency': 'USD', 'seats': 6, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (21, 9)},
                        'Elephant Room - Heads Up'              : {'buyIn': 100, 'fee': 4.5, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (200,)},
                        'Elephant Room - Turbo Heads Up'        : {'buyIn': 110, 'fee': 4.5, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (220,)},
                        'Elephant Shrew Room'                   : {'buyIn': 2, 'fee': 0.2, 'currency': 'USD', 'seats': 9, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (9, 5.40, 3.60)},
                        'Elk Room'                              : {'buyIn': 50, 'fee': 5, 'currency': 'USD', 'seats': 6, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (210, 90)},
                        'Emu Room - Heads Up'                   : {'buyIn': 10, 'fee': 0.5, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (20,)},
                        'Emu Room - Turbo Heads Up'             : {'buyIn': 11, 'fee': 0.5, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (22,)},
                        'Falcon Room'                           : {'buyIn': 50, 'fee': 5, 'currency': 'USD', 'seats': 10, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (250, 150, 100)},
                        'Falcon Room Turbo'                     : {'buyIn': 50, 'fee': 5, 'currency': 'USD', 'seats': 10, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (250, 150, 100)},
                        'Fast Fifty SnG'                        : {'buyIn': 0.5, 'fee': 0.1, 'currency': 'USD', 'seats': 10, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (2.50, 1.50, 1)},
                        'Fast Fifty Turbo'                      : {'buyIn': 0.5, 'fee': 0.1, 'currency': 'USD', 'seats': 10, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (2.50, 1.50, 1)},
                        'Ferret Room - Turbo'                   : {'buyIn': 10, 'fee': 1, 'currency': 'USD', 'seats': 10, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (50, 30, 20)},
                        'Fox Room - Heads Up'                   : {'buyIn': 10, 'fee': 1, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (20,)},
                        'Fox Room - Turbo Heads Up'             : {'buyIn': 11, 'fee': 0.5, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (22,)},
                        'Frigate Bird Room Super Turbo HU'      : {'buyIn': 2, 'fee': 0.1, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (4,)},
                        'Fruit Fly Room - Super Turbo'          : {'buyIn': 1, 'fee': 0.06, 'currency': 'USD', 'seats': 6, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (4.20, 1.80)},
                        'Fusilier Room Turbo'                   : {'buyIn': 1, 'fee': 0.1, 'currency': 'USD', 'seats': 45, 'multi': True, 'payoutCurrency': 'USD', 'payouts': (13.96, 9.68, 7.42, 5.62, 4.05, 2.70, 1.57)},
                        'Fun Step 1'                            : {'buyIn': 0, 'fee': 0, 'currency': 'USD', 'seats': 10, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (0, 0, 0)},
                        'Fun Step 2'                            : {'buyIn': 0, 'fee': 0, 'currency': 'USD', 'seats': 10, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (0, 0, 0)},
                        'Fun Step 3'                            : {'buyIn': 0, 'fee': 0, 'currency': 'USD', 'seats': 10, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (1, 0, 0)},
                        'Gazelle Room - Super Turbo'            : {'buyIn': 100, 'fee': 3.7, 'currency': 'USD', 'seats': 6, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (420, 180)},
                        'Gecko Room'                            : {'buyIn': 30, 'fee': 3, 'currency': 'USD', 'seats': 10, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (150, 90, 60)},
                        'Gecko Room Turbo'                      : {'buyIn': 30, 'fee': 3, 'currency': 'USD', 'seats': 10, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (150, 90, 60)},
                        'Gibbon Room'                           : {'buyIn': 200, 'fee': 15, 'currency': 'USD', 'seats': 6, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (840, 360)},
                        'Giraffe Room'                          : {'buyIn': 20, 'fee': 2, 'currency': 'USD', 'seats': 6, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (84, 36)},
                        'Goldfish Room'                         : {'buyIn': 2, 'fee': 0.2, 'currency': 'USD', 'seats': 10, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (8.40, 3.60)},
                        'Gopher Room - Turbo'                   : {'buyIn': 2, 'fee': 0.2, 'currency': 'USD', 'seats': 6, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (8.40, 3.60)},
                        'Gorilla Room - Heads Up'               : {'buyIn': 20, 'fee': 1, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (40,)},
                        'Gnat Room - Super Turbo HU'            : {'buyIn': 4, 'fee': 0.15, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (8,)},
                        'Goblin Shark Room'                     : {'buyIn': 150, 'fee': 2.75, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (300,)},
                        'Golden Eagle Turbo HU'                 : {'buyIn': 22, 'fee': 1, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (44,)},
                        'Goldfish Room'                         : {'buyIn': 2, 'fee': 0.2, 'currency': 'USD', 'seats': 6, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (8.40, 3.60)},
                        'Great White Shark Room - Heads Up'     : {'buyIn': 2000, 'fee': 40, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (4000,)},
                        'Great White Shark Room - Turbo Heads Up' : {'buyIn': 2200, 'fee': 40, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (4400,)},
                        'Grey Wolf Room Turbo HU (4 players)'   : {'buyIn': 18, 'fee': 0.9, 'currency': 'USD', 'seats': 4, 'multi': True, 'payoutCurrency': 'USD', 'payouts': (72,)},
                        'Greyhound Room - Super Turbo'          : {'buyIn': 35, 'fee': 1.5, 'currency': 'USD', 'seats': 6, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (147, 63)},
                        'Grizzly Room'                          : {'buyIn': 30, 'fee': 3, 'currency': 'USD', 'seats': 6, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (126, 54)},
                        'Guinea Pig Room - Super Turbo'         : {'buyIn': 5, 'fee': 0.3, 'currency': 'USD', 'seats': 12, 'multi': True, 'payoutCurrency': 'USD', 'payouts': (30, 18, 12)},
                        'Hairy Frog Room - Super Turbo HU'      : {'buyIn': 28, 'fee': 0.7, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (56,)},
                        'Hare Room - Super Turbo'               : {'buyIn': 20, 'fee': 0.9, 'currency': 'USD', 'seats': 6, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (84, 36)},
                        'Hedgehog Room'                         : {'buyIn': 5, 'fee': 0.5, 'currency': 'USD', 'seats': 9, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (22.50, 13.50, 9)},
                        'Heron Room'                            : {'buyIn': 300, 'fee': 20, 'currency': 'USD', 'seats': 6, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (1260, 540)},
                        'Hippo Room - Heads Up'                 : {'buyIn': 50, 'fee': 2.5, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (100,)},
                        'Hippo Room - Turbo Heads Up'           : {'buyIn': 55, 'fee': 2.5, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (110,)},
                        'Honey Badger Room'                     : {'buyIn': 5, 'fee': 5, 'currency': 'USD', 'seats': 6, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (21, 9)},
                        'Howler Monkey Room - Super Turbo'      : {'buyIn': 10, 'fee': 0.5, 'currency': 'USD', 'seats': 12, 'multi': True, 'payoutCurrency': 'USD', 'payouts': (60, 36, 24)},
                        'Hummingbird Room - Super Turbo'        : {'buyIn': 5, 'fee': 0.3, 'currency': 'USD', 'seats': 6, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (21, 9)},
                        'Hyena Room'                            : {'buyIn': 2, 'fee': 0.2, 'currency': 'USD', 'seats': 10, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (10, 6, 4)},
                        'Ibex Room - Super Turbo HU'            : {'buyIn': 180, 'fee': 3.1, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (360,)},
                        'Iguana Room - Heads Up'                : {'buyIn': 20, 'fee': 1, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (40,)},
                        'Iguana Room - Turbo Heads Up'          : {'buyIn': 22, 'fee': 1, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (44,)},
                        'Impala Room'                           : {'buyIn': 30, 'fee': 3, 'currency': 'USD', 'seats': 9, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (135, 81, 54)},
                        'Jaguar Room'                           : {'buyIn': 50, 'fee': 5, 'currency': 'USD', 'seats': 6, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (210, 90)},
                        'Killer Whale Room - Super Turbo'       : {'buyIn': 500, 'fee': 12, 'currency': 'USD', 'seats': 6, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (2100, 900)},
                        'King Cobra Room - Super Turbo HU'      : {'buyIn': 500, 'fee': 7.5, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (1000,)},
                        'Komodo Room'                           : {'buyIn': 50, 'fee': 5, 'currency': 'USD', 'seats': 6, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (210, 90)},
                        'Kookaburra Room - Heads Up'            : {'buyIn': 20, 'fee': 1, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (40,)},
                        'Kookaburra Room - Turbo Heads Up'      : {'buyIn': 22, 'fee': 1, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (44,)},
                        'Lemming Room - Super Turbo HU'         : {'buyIn': 40, 'fee': 0.8, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (80,)},
                        'Lemur Room - Super Turbo HU'           : {'buyIn': 55, 'fee': 1.1, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (110,)},
                        'Leopard Room'                          : {'buyIn': 5, 'fee': 0.5, 'currency': 'USD', 'seats': 6, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (21, 9)},
                        'Leopard Seal Room - Heads Up'          : {'buyIn': 30, 'fee': 1.5, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (60,)},
                        'Lizard Room - Turbo'                   : {'buyIn': 20, 'fee': 2, 'currency': 'USD', 'seats': 6, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (84, 36)},
                        'Lynx Room'                             : {'buyIn': 110, 'fee': 9, 'currency': 'USD', 'seats': 6, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (462, 198)},
                        'Mako Room'                             : {'buyIn': 75, 'fee': 7, 'currency': 'USD', 'seats': 10, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (375, 225, 150)},
                        'Mako Room Turbo'                       : {'buyIn': 75, 'fee': 7, 'currency': 'USD', 'seats': 10, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (375, 225, 150)},
                        'Marlin Room - Super Turbo'             : {'buyIn': 350, 'fee': 10, 'currency': 'USD', 'seats': 6, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (1470, 630)},
                        'Meerkat Room - Turbo'                  : {'buyIn': 2, 'fee': 0.2, 'currency': 'USD', 'seats': 6, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (8.40, 3.60)},
                        'Mink Room - Heads Up'                  : {'buyIn': 5, 'fee': 0.25, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (10,)},
                        'Mink Room - Turbo Heads Up'            : {'buyIn': 7, 'fee': 0.25, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (14,)},
                        'Mountain Goat Room Turbo HU (4 players)' : {'buyIn': 6, 'fee': 0.3, 'currency': 'USD', 'seats': 4, 'multi': True, 'payoutCurrency': 'USD', 'payouts': (24,)},
                        'Mongoose Room'                         : {'buyIn': 2, 'fee': 0.2, 'currency': 'USD', 'seats': 10, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (10, 6, 4)},
                        'Monkey Room'                           : {'buyIn': 10, 'fee': 1, 'currency': 'USD', 'seats': 9, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (90, 54, 36)},
                        'Mountain Lion Turbo HU'                : {'buyIn': 75, 'fee': 3.5, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (150,)},
                        'Mouse Room'                            : {'buyIn': 2, 'fee': 0.2, 'currency': 'USD', 'seats': 10, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (10, 6, 4)},
                        'Musk Rat Room '                        : {'buyIn': 3, 'fee': 0.3, 'currency': 'USD', 'seats': 8, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (16.80, 7.20)},
                        'Ocelot Room'                           : {'buyIn': 10, 'fee': 1, 'currency': 'USD', 'seats': 8, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (56, 24)},
                        'Orangutan Room'                        : {'buyIn': 20, 'fee': 2, 'currency': 'USD', 'seats': 6, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (84, 36)},
                        'Otter Room - Turbo'                    : {'buyIn': 5, 'fee': 0.5, 'currency': 'USD', 'seats': 6, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (21, 9)},
                        'Ox Room - Turbo'                       : {'buyIn': 20, 'fee': 2, 'currency': 'USD', 'seats': 10, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (100, 60, 40)},
                        'Panda Room - Heads Up'                 : {'buyIn': 100, 'fee': 4.5, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (200,)},
                        'Panda Room - Turbo Heads Up'           : {'buyIn': 110, 'fee': 4.5, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (220,)},
                        'Panther Room - Heads Up'               : {'buyIn': 500, 'fee': 20, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (1000,)},
                        'Panther Room - Turbo Heads Up'         : {'buyIn': 550, 'fee': 20, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (1100,)},
                        'Peregrine Room'                        : {'buyIn': 330, 'fee': 20, 'currency': 'USD', 'seats': 6, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (1386, 594)},
                        'Pilchard Room Turbo'                   : {'buyIn': 1, 'fee': 0.1, 'currency': 'USD', 'seats': 18, 'multi': True, 'payoutCurrency': 'USD', 'payouts': (7.20, 5.40, 3.60, 1.80)},
                        'Piranha Room - Heads Up'               : {'buyIn': 50, 'fee': 2.5, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (100,)},
                        'Piranha Room - Turbo Heads Up'         : {'buyIn': 55, 'fee': 2.5, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (110,)},
                        'Pond Skater Room - Super Turbo HU'     : {'buyIn': 15, 'fee': 0.3, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (30,)},
                        'Platypus Room'                         : {'buyIn': 5, 'fee': 0.5, 'currency': 'USD', 'seats': 10, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (25, 15, 10)},
                        'Pronghorn Antelope Room - Super Turbo HU' : {'buyIn': 1000, 'fee': 15, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (2000,)},
                        'Puffin Room - Super Turbo HU'          : {'buyIn': 70, 'fee': 1.5, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (140,)},
                        'Puma Room - Heads Up'                  : {'buyIn': 20, 'fee': 1, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (40,)},
                        'Puma Room - Turbo Heads Up'            : {'buyIn': 22, 'fee': 1, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (44,)},
                        'Rabbit Room - Turbo'                   : {'buyIn': 2, 'fee': 0.2, 'currency': 'USD', 'seats': 10, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (10, 6, 4)},
                        'Racoon Room'                           : {'buyIn': 5, 'fee': 0.5, 'currency': 'USD', 'seats': 10, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (25, 15, 10)},
                        'Rattlesnake Room - Heads Up'           : {'buyIn': 5, 'fee': 0.25, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (10,)},
                        'Raven Room'                            : {'buyIn': 180, 'fee': 14, 'currency': 'USD', 'seats': 6, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (756, 324)},
                        'Razorback Room'                        : {'buyIn': 100, 'fee': 9, 'currency': 'USD', 'seats': 6, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (420, 180)},
                        'Red Kangaroo Room - Heads Up'          : {'buyIn': 20, 'fee': 1, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (40,)},
                        'Rhino Room - Heads Up'                 : {'buyIn': 10, 'fee': 0.5, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (20,)},
                        'Rhino Room - Turbo Heads Up'           : {'buyIn': 11, 'fee': 0.5, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (22,)},
                        'Sailfish Room - Super Turbo'           : {'buyIn': 209, 'fee': 7, 'currency': 'USD', 'seats': 6, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (877.80, 376.20)},
                        'Salmon Room'                           : {'buyIn': 5, 'fee': 0.5, 'currency': 'USD', 'seats': 45, 'multi': True, 'payoutCurrency': 'USD', 'payouts': (69.76, 48.38, 37.12, 28.12, 20.25, 13.50, 7.87)},
                        'Sardine Room Turbo'                    : {'buyIn': 1, 'fee': 0.1, 'currency': 'USD', 'seats': 27, 'multi': True, 'payoutCurrency': 'USD', 'payouts': (10.27, 7.02, 4.59, 2.75, 2.37)},
                        'Sea Eagle Room Turbo HU (4 players)'   : {'buyIn': 24, 'fee': 1.2, 'currency': 'USD', 'seats': 4, 'multi': True, 'payoutCurrency': 'USD', 'payouts': (96,)},
                        'Secretary Bird Room - Super Turbo HU'  : {'buyIn': 90, 'fee': 1.8, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (180,)},
                        'Shrew Room - Heads Up'                 : {'buyIn': 5, 'fee': 0.25, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (10,)},
                        'Shrew Room - Turbo Heads Up'           : {'buyIn': 7, 'fee': 0.25, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (14,)},
                        "Snakes'n'Ladders Step 1"               : {'buyIn': 1, 'fee': 0.1, 'currency': 'USD', 'seats': 10, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (3.30, 3.30, 1.10, 1.10, 1.10, 0.10)},
                        "Snakes'n'Ladders Step 2"               : {'buyIn': 3, 'fee': 0.3, 'currency': 'USD', 'seats': 10, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (11, 11, 3.30, 3.30, 1.10, 0.30)},
                        "Snakes'n'Ladders Step 3"               : {'buyIn': 10, 'fee': 1, 'currency': 'USD', 'seats': 10, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (32.50, 32.50, 11, 11, 3.30, 3.30, 3.30, 1.10, 1.10, 0.90)},
                        "Snakes'n'Ladders Step 4"               : {'buyIn': 30, 'fee': 2.5, 'currency': 'USD', 'seats': 10, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (80, 80, 80, 32.50, 11, 11, 3.30, 1.10, 1.10)},
                        "Snakes'n'Ladders Step 5"               : {'buyIn': 75, 'fee': 5, 'currency': 'USD', 'seats': 10, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (265, 265, 80, 80, 32.50, 11, 11, 3.30, 1.10, 1.10)},
                        "Snakes'n'Ladders Step 6"               : {'buyIn': 255, 'fee': 10, 'currency': 'USD', 'seats': 10, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (530, 530, 530, 265, 265, 265, 80, 80, 3.30, 1.70)},
                        "Snakes'n'Ladders Step 7"               : {'buyIn': 510, 'fee': 20, 'currency': 'USD', 'seats': 10, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (2000, 1250, 750, 499.50, 295, 220, 80, 3.30, 1.10, 1.10)},
                        'Snow Goose Room'                       : {'buyIn': 10, 'fee': 1, 'currency': 'USD', 'seats': 45, 'multi': True, 'payoutCurrency': 'USD', 'payouts': (139.50, 96.75, 74.25, 56.25, 40.50, 27, 15.75)},
                        'Springbok Room - Super Turbo'          : {'buyIn': 20, 'fee': 0.9, 'currency': 'USD', 'seats': 12, 'multi': True, 'payoutCurrency': 'USD', 'payouts': (120, 72, 48)},
                        'Squirrel Room - Turbo'                 : {'buyIn': 2, 'fee': 0.2, 'currency': 'USD', 'seats': 6, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (8.40, 3.60)},
                        'Stag Room Turbo HU (4 players)'        : {'buyIn': 3, 'fee': 0.15, 'currency': 'USD', 'seats': 4, 'multi': True, 'payoutCurrency': 'USD', 'payouts': (12,)},
                        'Starling Room'                         : {'buyIn': 2, 'fee': 0.2, 'currency': 'USD', 'seats': 180, 'multi': True, 'payoutCurrency': 'USD', 'payouts': (108, 72, 36, 28.80, 21.60, 18, 14.40, 10.80, 8.10, 6.30, 3.60, 3.60, 3.60, 3.60, 3.60, 3.60, 3.60, 3.60, 3.60, 3.60) },
                        'STEP 1 AIOF Sng'                       : {'buyIn': 1, 'fee': 0.1, 'currency': 'USD', 'seats': 10, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (5.50, 1.10, 1.10, 1.10, 0.20)},
                        'STEP 10 AIOF Final Sng'                : {'buyIn': 1170, 'fee': 10, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (2250, 90)},
                        'STEP 2 AIOF Sng'                       : {'buyIn': 5.25, 'fee': 0.25, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (10.50,)},
                        'STEP 3 AIOF Sng'                       : {'buyIn': 10, 'fee': 0.5, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (20,)},
                        'STEP 4 AIOF Sng'                       : {'buyIn': 19.5, 'fee': 0.5, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (39,)},
                        'STEP 5 AIOF Sng'                       : {'buyIn': 38.5, 'fee': 0.5, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (77,)},
                        'STEP 6 AIOF Sng'                       : {'buyIn': 76, 'fee': 1, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (152,)},
                        'STEP 7 AIOF Sng'                       : {'buyIn': 150, 'fee': 2, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (300,)},
                        'STEP 8 AIOF Sng'                       : {'buyIn': 297, 'fee': 3, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (594,)},
                        'STEP 9 AIOF Sng'                       : {'buyIn': 590, 'fee': 4, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (1180,)},
                        'Sun Bear Room'                         : {'buyIn': 20, 'fee': 2, 'currency': 'USD', 'seats': 8, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (112, 48)},
                        'Swift Room - Super Turbo'              : {'buyIn': 10, 'fee': 0.5, 'currency': 'USD', 'seats': 6, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (42, 18)},
                        'Swordfish Room'                        : {'buyIn': 220, 'fee': 15, 'currency': 'USD', 'seats': 6, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (924, 396)},
                        'Tapir Room'                            : {'buyIn': 20, 'fee': 2, 'currency': 'USD', 'seats': 8, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (112, 48)},
                        'Termite Room'                          : {'buyIn': 3, 'fee': 0.3, 'currency': 'USD', 'seats': 8, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (16.80, 7.20)},
                        'Tiger Fish Room'                       : {'buyIn': 10, 'fee': 1, 'currency': 'USD', 'seats': 8, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (56, 24,)},
                        'Tiger Room - Heads Up'                 : {'buyIn': 50, 'fee': 2.5, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (100,)},
                        'Tiger Room - Turbo Heads Up'           : {'buyIn': 55, 'fee': 2.5, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (100,)},
                        'Timber Wolf Room'                      : {'buyIn': 400, 'fee': 22, 'currency': 'USD', 'seats': 6, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (1680, 720)},
                        'Toucan Room - Heads Up'                : {'buyIn': 10, 'fee': 0.5, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (20,)},
                        'Toucan Room - Heads Up'                : {'buyIn': 10, 'fee': 0.5, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (20,)},
                        'Toucan Room - Turbo Heads Up'          : {'buyIn': 11, 'fee': 0.5, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (22,)},
                        'Tsetse Fly Room'                       : {'buyIn': 2, 'fee': 0.2, 'currency': 'USD', 'seats': 6, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (8.4,3.6)},
                        'Turkey Room - Heads Up'                : {'buyIn': 10, 'fee': 0.5, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (20,)},
                        'Turkey Room - Turbo Heads Up'          : {'buyIn': 11, 'fee': 0.5, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (22,)},
                        'Viper Room - Heads Up'                 : {'buyIn': 1000, 'fee': 40, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (2000,)},
                        'Vulture Room'                          : {'buyIn': 20, 'fee': 2, 'currency': 'USD', 'seats': 9, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (90,54,36)},
                        'Wallaby Room'                          : {'buyIn': 10, 'fee': 1, 'currency': 'USD', 'seats': 6, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (42, 18)},
                        'Walrus Room'                           : {'buyIn': 50, 'fee': 5, 'currency': 'USD', 'seats': 10, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (250, 150, 100)},
                        'Warthog Room'                          : {'buyIn': 2, 'fee': 0.2, 'currency': 'USD', 'seats': 9, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (18, 10.80, 7.20)},
                        'Waterbuck room - Heads Up'             : {'buyIn': 10, 'fee': 0.5, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (20,)},
                        'Whale Room - Heads Up'                 : {'buyIn': 500, 'fee': 20, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (1000,)},
                        'Wildebeest Room'                       : {'buyIn': 10, 'fee': 1, 'currency': 'USD', 'seats': 6, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (42, 18)},
                        'Wolf Spider Room - Super Turbo HU'     : {'buyIn': 21, 'fee': 0.5, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (42,)},
                        'Wolverine Room'                        : {'buyIn': 50, 'fee': 0.5, 'currency': 'USD', 'seats': 10, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (25, 15, 10)},
                        'Wombat Room'                           : {'buyIn': 20, 'fee': 1, 'currency': 'USD', 'seats': 6, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (84, 36)},
                        'Yak Room - Heads Up'                   : {'buyIn': 50, 'fee': 2.5, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (100,)},
                        'Zebra Room - Heads Up'                 : {'buyIn': 5, 'fee': 0.25, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (10,)},
                        'Zebra Room - Turbo Heads Up'           : {'buyIn': 7, 'fee': 0.25, 'currency': 'USD', 'seats': 2, 'multi': False, 'payoutCurrency': 'USD', 'payouts': (14,)},
                     }

    # Static regexes
    re_SplitHands = re.compile(r'</game>\n+(?=<game)')
    re_TailSplitHands = re.compile(r'(</game>)')
    re_GameInfo = re.compile(r'<description type="(?P<GAME>Holdem|Holdem\sTournament|Omaha|Omaha\sTournament|Omaha\sH/L8|2\-7\sLowball|A\-5\sLowball|Badugi|5\-Draw\sw/Joker|5\-Draw|7\-Stud|7\-Stud\sH/L8|5\-Stud|Razz)" stakes="(?P<LIMIT>[a-zA-Z ]+)(\s\(?\$?(?P<SB>[.0-9]+)?/?\$?(?P<BB>[.0-9]+)?(?P<blah>.*)\)?)?"/>', re.MULTILINE)
    re_HandInfo = re.compile(r'<game id="(?P<HID1>[0-9]+)-(?P<HID2>[0-9]+)" starttime="(?P<DATETIME>[0-9]+)" numholecards="[0-9]+" gametype="[0-9]+" (seats="(?P<SEATS>[0-9]+)" )?realmoney="(?P<REALMONEY>(true|false))" data="[0-9]+\|(?P<TABLE>[^|]+)\|(?P<TOURNO>\d+)?.*>', re.MULTILINE)
    re_Button = re.compile(r'<players dealer="(?P<BUTTON>[0-9]+)">')
    re_PlayerInfo = re.compile(r'<player seat="(?P<SEAT>[0-9]+)" nickname="(?P<PNAME>.+)" balance="\$(?P<CASH>[.0-9]+)" dealtin="(?P<DEALTIN>(true|false))" />', re.MULTILINE)
    re_Board = re.compile(r'<cards type="COMMUNITY" cards="(?P<CARDS>[^"]+)"', re.MULTILINE)
    re_EndOfHand = re.compile(r'<round id="END_OF_GAME"', re.MULTILINE)
    re_Buyin = re.compile(r'\$(?P<BUYIN>[.,0-9]+)\s(?P<FREEROLL>Freeroll)?', re.MULTILINE)

    # The following are also static regexes: there is no need to call
    # compilePlayerRegexes (which does nothing), since players are identified
    # not by name but by seat number
    re_PostSB = re.compile(r'<event sequence="[0-9]+" type="(SMALL_BLIND|RETURN_BLIND)" (?P<TIMESTAMP>timestamp="[0-9]+" )?player="(?P<PSEAT>[0-9])" amount="(?P<SB>[.0-9]+)"/>', re.MULTILINE)
    re_PostBB = re.compile(r'<event sequence="[0-9]+" type="(BIG_BLIND|INITIAL_BLIND)" (?P<TIMESTAMP>timestamp="[0-9]+" )?player="(?P<PSEAT>[0-9])" amount="(?P<BB>[.0-9]+)"/>', re.MULTILINE)
    re_PostBoth = re.compile(r'<event sequence="[0-9]+" type="(RETURN_BLIND)" player="(?P<PSEAT>[0-9])" amount="(?P<SBBB>[.0-9]+)"/>', re.MULTILINE)
    re_Antes = re.compile(r'<event sequence="[0-9]+" type="ANTE" (?P<TIMESTAMP>timestamp="\d+" )?player="(?P<PSEAT>[0-9])" amount="(?P<ANTE>[.0-9]+)"/>', re.MULTILINE)
    re_BringIn = re.compile(r'<event sequence="[0-9]+" type="BRING_IN" (?P<TIMESTAMP>timestamp="\d+" )?player="(?P<PSEAT>[0-9])" amount="(?P<BRINGIN>[.0-9]+)"/>', re.MULTILINE)
    re_HeroCards = re.compile(r'<cards type="(HOLE|DRAW_DRAWN_CARDS)" cards="(?P<CARDS>.+)" player="(?P<PSEAT>[0-9])"', re.MULTILINE)
    re_Action = re.compile(r'<event sequence="[0-9]+" type="(?P<ATYPE>FOLD|CHECK|CALL|BET|RAISE|ALL_IN|SIT_OUT|DRAW|COMPLETE)"( timestamp="(?P<TIMESTAMP>[0-9]+)")? player="(?P<PSEAT>[0-9])"( amount="(?P<BET>[.0-9]+)")?( text="(?P<TXT>.+)")?/>', re.MULTILINE)
    re_ShowdownAction = re.compile(r'<cards type="SHOWN" cards="(?P<CARDS>..,..)" player="(?P<PSEAT>[0-9])"/>', re.MULTILINE)
    re_CollectPot = re.compile(r'<winner amount="(?P<POT>[.0-9]+)" uncalled="false" potnumber="[0-9]+" player="(?P<PSEAT>[0-9])"', re.MULTILINE)
    re_SitsOut = re.compile(r'<event sequence="[0-9]+" type="SIT_OUT" player="(?P<PSEAT>[0-9])"/>', re.MULTILINE)
    re_ShownCards = re.compile(r'<cards type="(SHOWN|MUCKED)" cards="(?P<CARDS>.+)" player="(?P<PSEAT>[0-9])"/>', re.MULTILINE)
    re_Reconnected = re.compile(r'<event sequence="[0-9]+" type="RECONNECTED" timestamp="[0-9]+" player="[0-9]"/>', re.MULTILINE)

    def compilePlayerRegexs(self, hand):
        pass

    def playerNameFromSeatNo(self, seatNo, hand):
        # This special function is required because Merge Poker records
        # actions by seat number, not by the player's name
        for p in hand.players:
            if p[0] == int(seatNo):
                return p[1]

    def readSupportedGames(self):
        return [["ring", "hold", "nl"],
                ["ring", "hold", "pl"],
                ["ring", "hold", "fl"],

                ["ring", "stud", "fl"],
                ["ring", "stud", "pl"],

                ["ring", "draw", "fl"],
                ["ring", "draw", "pl"],
                ["ring", "draw", "nl"],
                ["ring", "draw", "hp"],
                
                ["tour", "hold", "nl"],
                ["tour", "hold", "pl"],
                ["tour", "hold", "fl"]]

    def determineGameType(self, handText):
        """return dict with keys/values:
    'type'       in ('ring', 'tour')
    'limitType'  in ('nl', 'cn', 'pl', 'cp', 'fl')
    'base'       in ('hold', 'stud', 'draw')
    'category'   in ('holdem', 'omahahi', omahahilo', 'razz', 'studhi', 'studhilo', 'fivedraw', '27_1draw', '27_3draw', 'badugi')
    'hilo'       in ('h','l','s')
    'smallBlind' int?
    'bigBlind'   int?
    'smallBet'
    'bigBet'
    'currency'  in ('USD', 'EUR', 'T$', <countrycode>)
or None if we fail to get the info """

        m = self.re_GameInfo.search(handText)
        if not m:
            # Information about the game type appears only at the beginning of
            # a hand history file; hence it is not supplied with the second
            # and subsequent hands. In these cases we use the value previously
            # stored.
            try:
                return self.info
            except AttributeError:
                tmp = handText[0:100]
                log.error(_("Unable to recognise gametype from: '%s'") % tmp)
                log.error("determineGameType: " + _("Raising FpdbParseError"))
                #print _("Unable to recognise gametype from: '%s'") % tmp
                raise FpdbParseError(_("Unable to recognise gametype from: '%s'") % tmp)

        self.info = {}
        mg = m.groupdict()
        #print "DEBUG: mg: %s" % mg

        if 'LIMIT' in mg:
            self.info['limitType'] = self.limits[mg['LIMIT']]
        if 'GAME' in mg:
            (self.info['base'], self.info['category']) = self.games[mg['GAME']]
        if 'SB' in mg:
            self.info['sb'] = mg['SB']
        if 'BB' in mg:
            self.info['bb'] = mg['BB']
        if 'Tournament' in mg['GAME']:
            self.info['type'] = 'tour'
            self.info['currency'] = 'T$'
        else:
            self.info['type'] = 'ring'
            self.info['currency'] = 'USD'

        if self.info['limitType'] == 'fl' and self.info['bb'] is not None and self.info['type'] == 'ring':
            try:
                self.info['sb'] = self.Lim_Blinds[mg['BB']][0]
                self.info['bb'] = self.Lim_Blinds[mg['BB']][1]
            except KeyError:
                log.error(_("Lim_Blinds has no lookup for '%s'") % mg['BB'])
                log.error("determineGameType: " + _("Raising FpdbParseError"))
                raise FpdbParseError(_("Lim_Blinds has no lookup for '%s'") % mg['BB'])

        return self.info

    def readHandInfo(self, hand):
        m = self.re_HandInfo.search(hand.handText)
        if m is None:
            logging.info(_("No match in readHandInfo: '%s'") % hand.handText[0:100])
            logging.info(hand.handText)
            raise FpdbParseError(_("No match in readHandInfo: '%s'") % hand.handText[0:100])
        logging.debug("HID %s-%s, Table %s" % (m.group('HID1'),
                      m.group('HID2'), m.group('TABLE')[:-1]))
        hand.handid = m.group('HID1') + m.group('HID2')
        if hand.gametype['type'] == 'tour':
            hand.tablename = m.group('TABLE').strip()
            hand.tourNo = m.group('TOURNO')
            if hand.tablename in self.SnG_Structures:
                hand.buyin = int(100*self.SnG_Structures[hand.tablename]['buyIn'])
                hand.fee   = int(100*self.SnG_Structures[hand.tablename]['fee'])
                hand.buyinCurrency="USD"
            elif hand.tablename in self.MTT_Structures:
                hand.buyin = int(100*self.MTT_Structures[hand.tablename]['buyIn'])
                hand.fee   = int(100*self.MTT_Structures[hand.tablename]['fee'])
                hand.buyinCurrency="USD"
            else:
                m1 = self.re_Buyin.search(hand.tablename)
                if m1:
                    if m1.group('FREEROLL'):
                        hand.buyin = 0
                        hand.fee = 0
                        hand.buyinCurrency="FREE"
                    else:
                        buyin = self.clearMoneyString(m1.group('BUYIN'))
                        hand.buyin = int(100*Decimal(buyin))
                        hand.fee = int(100*Decimal(buyin)/10)
                        hand.buyinCurrency="USD"
                else:
                    raise FpdbParseError(_("No match in MTT or SnG Structures: '%s' %s") % (hand.tablename, hand.tourNo))
        else:
            hand.tablename = m.group('TABLE')
        if m.group('SEATS'):
            hand.maxseats = int(m.group('SEATS'))
        else:
            hand.maxseats = 2 # This value may be increased as necessary
        hand.startTime = datetime.datetime.strptime(m.group('DATETIME')[:12],'%Y%m%d%H%M')
        # Check that the hand is complete up to the awarding of the pot; if
        # not, the hand is unparseable
        if self.re_EndOfHand.search(hand.handText) is None:
            # Situations found so far where this is triggered:
                # A player leaving the table in a cash game before the last hand they played (or observed) is finished
                # The hand was cancelled
                # Player was disconnected and didn't see the end of the hand (NOTE: this isn't the only place disconnected triggers a partial)
            # We almost certainly don't have full information so throw a Partial.
            # FIXME: We should probably differentiate between them.
                # re_Reconnected already exists
                # re_Cancelled: <event sequence="\d+" type="GAME_CANCELLED" timestamp="\d+"/>
                # re_LeaveTable: <event sequence="\d+" type="LEAVE" timestamp="\d+" player="\d"/>
            raise FpdbHandPartial("readHandInfo: " + _("Partial hand history") + ": '%s-%s' - No 'END_OF_GAME'. Hero left, disconnected or hand cancelled." % (m.group('HID1'), m.group('HID2')))

    def readPlayerStacks(self, hand):
        m = self.re_PlayerInfo.finditer(hand.handText)
        for a in m:
            seatno = int(a.group('SEAT'))
            # It may be necessary to adjust 'hand.maxseats', which is an
            # educated guess, starting with 2 (indicating a heads-up table) and
            # adjusted upwards in steps to 6, then 9, then 10. An adjustment is
            # made whenever a player is discovered whose seat number is
            # currently above the maximum allowable for the table.
            if seatno >= hand.maxseats:
                if seatno > 8:
                    hand.maxseats = 10
                elif seatno > 5:
                    hand.maxseats = 9
                else:
                    hand.maxseats = 6
            if a.group('DEALTIN') == "true":
                hand.addPlayer(seatno, a.group('PNAME'), a.group('CASH'))
        if not hand.players:
            raise FpdbHandPartial("readPlayerStacks: " + _("No one was dealt in"))

    def markStreets(self, hand):
        if hand.gametype['base'] == 'hold':
            m = re.search(r'<round id="PREFLOP" sequence="[0-9]+">(?P<PREFLOP>.+(?=<round id="POSTFLOP")|.+)'
                         r'(<round id="POSTFLOP" sequence="[0-9]+">(?P<FLOP>.+(?=<round id="POSTTURN")|.+))?'
                         r'(<round id="POSTTURN" sequence="[0-9]+">(?P<TURN>.+(?=<round id="POSTRIVER")|.+))?'
                         r'(<round id="POSTRIVER" sequence="[0-9]+">(?P<RIVER>.+))?', hand.handText, re.DOTALL)
        elif hand.gametype['base'] == 'draw':
            if hand.gametype['category'] in ('27_3draw','badugi','a5_3draw'):
                m =  re.search(r'(?P<PREDEAL>.+(?=<round id="PRE_FIRST_DRAW" sequence="[0-9]+">)|.+)'
                           r'(<round id="PRE_FIRST_DRAW" sequence="[0-9]+">(?P<DEAL>.+(?=<round id="FIRST_DRAW" sequence="[0-9]+">)|.+))?'
                           r'(<round id="FIRST_DRAW" sequence="[0-9]+">(?P<DRAWONE>.+(?=<round id="SECOND_DRAW" sequence="[0-9]+">)|.+))?'
                           r'(<round id="SECOND_DRAW" sequence="[0-9]+">(?P<DRAWTWO>.+(?=<round id="THIRD_DRAW" sequence="[0-9]+">)|.+))?'
                           r'(<round id="THIRD_DRAW" sequence="[0-9]+">(?P<DRAWTHREE>.+))?', hand.handText,re.DOTALL)
            else:
                m =  re.search(r'(?P<PREDEAL>.+(?=<round id="PRE_FIRST_DRAW" sequence="[0-9]+">)|.+)'
                           r'(<round id="PRE_FIRST_DRAW" sequence="[0-9]+">(?P<DEAL>.+(?=<round id="FIRST_DRAW" sequence="[0-9]+">)|.+))?'
                           r'(<round id="FIRST_DRAW" sequence="[0-9]+">(?P<DRAWONE>.+(?=<round id="SECOND_DRAW" sequence="[0-9]+">)|.+))?', hand.handText,re.DOTALL)
        elif hand.gametype['base'] == 'stud':
            m =  re.search(r'(?P<ANTES>.+(?=<round id="BRING_IN" sequence="[0-9]+">)|.+)'
                       r'(<round id="BRING_IN" sequence="[0-9]+">(?P<THIRD>.+(?=<round id="FOURTH_STREET" sequence="[0-9]+">)|.+))?'
                       r'(<round id="FOURTH_STREET" sequence="[0-9]+">(?P<FOURTH>.+(?=<round id="FIFTH_STREET" sequence="[0-9]+">)|.+))?'
                       r'(<round id="FIFTH_STREET" sequence="[0-9]+">(?P<FIFTH>.+(?=<round id="SIXTH_STREET" sequence="[0-9]+">)|.+))?'
                       r'(<round id="SIXTH_STREET" sequence="[0-9]+">(?P<SIXTH>.+(?=<round id="SEVENTH_STREET" sequence="[0-9]+">)|.+))?'
                       r'(<round id="SEVENTH_STREET" sequence="[0-9]+">(?P<SEVENTH>.+))?', hand.handText,re.DOTALL)

        hand.addStreets(m)

    def readCommunityCards(self, hand, street):
        m = self.re_Board.search(hand.streets[street])
        if m and street in ('FLOP','TURN','RIVER'):
            if street == 'FLOP':
                hand.setCommunityCards(street, m.group('CARDS').split(','))
            elif street in ('TURN','RIVER'):
                hand.setCommunityCards(street, [m.group('CARDS').split(',')[-1]])
        else:
            m2 = self.re_Reconnected.search(hand.streets[street])
            if m2:
                raise FpdbHandPartial("readCommunityCards: " + _("Partial hand history") + ": '%s' No community cards found on %s due to RECONNECTED" % (hand.handid, street))
            raise FpdbParseError("readCommunityCards: " + _("'%s': No community cards found on %s") % (hand.handid, street))

    def readAntes(self, hand):
        m = self.re_Antes.finditer(hand.handText)
        for player in m:
            pname = self.playerNameFromSeatNo(player.group('PSEAT'), hand)
            #print "DEBUG: hand.addAnte(%s,%s)" %(pname, player.group('ANTE'))
            hand.addAnte(pname, player.group('ANTE'))

    def readBringIn(self, hand):
        m = self.re_BringIn.search(hand.handText)
        if m:
            pname = self.playerNameFromSeatNo(m.group('PSEAT'), hand)
            #print "DEBUG: hand.addBringIn(%s,%s)" %(pname, m.group('BRINGIN'))
            hand.addBringIn(pname, m.group('BRINGIN'))

    def readBlinds(self, hand):
        for a in self.re_PostSB.finditer(hand.handText):
            #print "DEBUG: found sb: '%s' '%s'" %(self.playerNameFromSeatNo(a.group('PSEAT'), hand), a.group('SB'))
            hand.addBlind(self.playerNameFromSeatNo(a.group('PSEAT'), hand),'small blind', a.group('SB'))
            if not hand.gametype['sb']:
                hand.gametype['sb'] = a.group('SB')
        for a in self.re_PostBB.finditer(hand.handText):
            #print "DEBUG: found bb: '%s' '%s'" %(self.playerNameFromSeatNo(a.group('PSEAT'), hand), a.group('BB'))
            hand.addBlind(self.playerNameFromSeatNo(a.group('PSEAT'), hand), 'big blind', a.group('BB'))
            if not hand.gametype['bb']:
                hand.gametype['bb'] = a.group('BB')
        for a in self.re_PostBoth.finditer(hand.handText):
            bb = Decimal(self.info['bb'])
            amount = Decimal(a.group('SBBB'))
            if amount < bb:
                hand.addBlind(self.playerNameFromSeatNo(a.group('PSEAT'), hand), 'small blind', a.group('SBBB'))
            elif amount == bb:
                hand.addBlind(self.playerNameFromSeatNo(a.group('PSEAT'), hand), 'big blind', a.group('SBBB'))
            else:
                hand.addBlind(self.playerNameFromSeatNo(a.group('PSEAT'), hand), 'both', a.group('SBBB'))

        # FIXME
        # The following should only trigger when a small blind is missing in a tournament, or the sb/bb is ALL_IN
        # see http://sourceforge.net/apps/mantisbt/fpdb/view.php?id=115
        if hand.gametype['type'] == 'tour':
            if hand.gametype['sb'] == None and hand.gametype['bb'] == None:
                hand.gametype['sb'] = "1"
                hand.gametype['bb'] = "2"
            elif hand.gametype['sb'] == None:
                hand.gametype['sb'] = str(int(Decimal(hand.gametype['bb']))/2)
            elif hand.gametype['bb'] == None:
                hand.gametype['bb'] = str(int(Decimal(hand.gametype['sb']))*2)
            if int(Decimal(hand.gametype['bb']))/2 != int(Decimal(hand.gametype['sb'])):
                if int(Decimal(hand.gametype['bb']))/2 < int(Decimal(hand.gametype['sb'])):
                    hand.gametype['bb'] = str(int(Decimal(hand.gametype['sb']))*2)
                else:
                    hand.gametype['sb'] = str(int(Decimal(hand.gametype['bb']))/2)


    def readButton(self, hand):
        hand.buttonpos = int(self.re_Button.search(hand.handText).group('BUTTON'))
                    
    def readHeroCards(self, hand):
#    streets PREFLOP, PREDRAW, and THIRD are special cases beacause
#    we need to grab hero's cards
        herocards = []
        for street in ('PREFLOP', 'DEAL'):
            if street in hand.streets.keys():
                m = self.re_HeroCards.finditer(hand.streets[street])
                for found in m:
#                    if m == None:
#                        hand.involved = False
#                    else:
                    hand.hero = self.playerNameFromSeatNo(found.group('PSEAT'), hand)
                    cards = found.group('CARDS').split(',')
                    hand.addHoleCards(street, hand.hero, closed=cards, shown=False, mucked=False, dealt=True)

        for street in hand.holeStreets:
            if hand.streets.has_key(street):
                if not hand.streets[street] or street in ('PREFLOP', 'DEAL') or hand.gametype['base'] == 'hold': continue  # already done these
                m = self.re_HeroCards.finditer(hand.streets[street])
                for found in m:
                    player = self.playerNameFromSeatNo(found.group('PSEAT'), hand)
                    if found.group('CARDS') is None:
                        cards    = []
                        newcards = []
                        oldcards = []
                    else:
                        if hand.gametype['base'] == 'stud':
                            cards = found.group('CARDS').replace('null,', '').replace(',null','').split(',')
                            oldcards = cards[:-1]
                            newcards = [cards[-1]]
                        else:
                            cards = found.group('CARDS').split(',')
                            oldcards = cards
                            newcards = []
                    if street == 'THIRD' and len(cards) == 3: # hero in stud game
                        hand.hero = player
                        herocards = cards
                        hand.dealt.add(hand.hero) # need this for stud??
                        hand.addHoleCards(street, player, closed=oldcards, open=newcards, shown=False, mucked=False, dealt=False)
                    elif (cards != herocards and hand.gametype['base'] == 'stud'):
                        if hand.hero == player:
                            herocards = cards
                            hand.addHoleCards(street, player, closed=oldcards, open=newcards, shown=False, mucked=False, dealt=False)
                        elif (len(cards)<5):
                            if street == 'SEVENTH':
                                oldcards = []
                                newcards = []
                            hand.addHoleCards(street, player, closed=oldcards, open=newcards, shown=False, mucked=False, dealt=False)
                        elif (len(cards)==7):
                            for street in hand.holeStreets:
                                hand.holecards[street][player] = [[], []]
                            hand.addHoleCards(street, player, closed=cards, open=[], shown=False, mucked=False, dealt=False)
                    elif (hand.gametype['base'] == 'draw'):
                        hand.addHoleCards(street, player, closed=oldcards, open=newcards, shown=False, mucked=False, dealt=False)

    def readAction(self, hand, street):
        logging.debug("readAction (%s)" % street)
        m = self.re_Action.finditer(hand.streets[street])
        for action in m:
            logging.debug("%s %s" % (action.group('ATYPE'), action.groupdict()))
            player = self.playerNameFromSeatNo(action.group('PSEAT'), hand)
            if action.group('ATYPE') == 'RAISE':
                hand.addRaiseTo(street, player, action.group('BET'))
            elif action.group('ATYPE') == 'COMPLETE':
                if hand.gametype['base'] != 'stud':
                    hand.addRaiseTo(street, player, action.group('BET'))
                else:
                    hand.addComplete( street, player, action.group('BET') )
            elif action.group('ATYPE') == 'CALL':
                hand.addCall(street, player, action.group('BET'))
            elif action.group('ATYPE') == 'BET':
                hand.addBet(street, player, action.group('BET'))
            elif action.group('ATYPE') in ('FOLD', 'SIT_OUT'):
                hand.addFold(street, player)
            elif action.group('ATYPE') == 'CHECK':
                hand.addCheck(street, player)
            elif action.group('ATYPE') == 'ALL_IN':
                hand.addAllIn(street, player, action.group('BET'))
            elif action.group('ATYPE') == 'DRAW':
                hand.addDiscard(street, player, action.group('TXT'))
            else:
                logging.debug(_("Unimplemented %s: '%s' '%s'") % ("readAction", action.group('PSEAT'), action.group('ATYPE')))

    def readShowdownActions(self, hand):
        for street in ('RIVER', 'SEVENTH', 'DRAWTHREE'):
            if street in hand.streets.keys() and hand.streets[street] != None:
                for shows in self.re_ShowdownAction.finditer(hand.streets[street]):
                    cards = shows.group('CARDS').split(',')
                    hand.addShownCards(cards, self.playerNameFromSeatNo(shows.group('PSEAT'), hand))

    def readCollectPot(self, hand):
        pots = [Decimal(0) for n in range(hand.maxseats)]
        for m in self.re_CollectPot.finditer(hand.handText):
            pname = self.playerNameFromSeatNo(m.group('PSEAT'), hand)
            pot = m.group('POT')
            committed = sorted([ (v,k) for (k,v) in hand.pot.committed.items()])
            lastbet = committed[-1][0] - committed[-2][0]
            if lastbet > 0: # uncalled
                pot = str(Decimal(m.group('POT')) - lastbet)
            #print "DEBUG: addCollectPot(%s, %s)" %(pname, m.group('POT'))
            hand.addCollectPot(player=pname, pot=pot)

    def readShownCards(self, hand):
        for street in ('FLOP', 'TURN', 'RIVER', 'SEVENTH', 'DRAWTHREE'):
            if street in hand.streets.keys() and hand.streets[street] != None:
                for m in self.re_ShownCards.finditer(hand.streets[street]):
                    cards = m.group('CARDS').split(',')
                    hand.addShownCards(cards=cards, player=self.playerNameFromSeatNo(m.group('PSEAT'),hand))
