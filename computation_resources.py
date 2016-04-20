import json, os, sys, re
from scipy.stats import binom
from math import *

def bd(k, n, p):
    return binom.logpmf(k, n, p)

def PMI(f1, f2, f12, tf):
    f1 = int(f1)
    f2 = int(f2)
    print(f1, f2, f12, tf)
    return log(f12*tf/f1*f2)

def localMI(f1, f2, f12, tf):
    return f12*log(f12*tf/f1*f2)

def LLR(f1, f2, f12, tf):

    f1 = int(f1)
    f2 = int(f2)

    p  = f2/tf
    p1 = f12/f1
    p2 = (f2-f12)/(tf-f1) 

    bn1 = bd(f12, f1, p)
    bn2 = bd(f2-f12, tf-f1, p)
    bn3 = bd(f12, f1, p1)
    bn4 = bd(f2-f12, tf-f1, p2)
    res = -2*(bn1+bn2-bn3-bn4)
    return res

