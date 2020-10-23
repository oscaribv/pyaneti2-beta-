### Pyaneti 2.0 (beta)


<p align="center">
  <img width = "500" src="./src/images/logo_pyaneti.png"/>
</p>

<a href="https://academic.oup.com/mnras/advance-article/doi/10.1093/mnras/sty2472/5094600"><img src="https://img.shields.io/badge/MNRAS-2019,482,1017-blueviolet.svg" alt="MNRAS" /></a>
<a href="https://arxiv.org/abs/1809.04609"><img src="https://img.shields.io/badge/arXiv-1809.04609-green.svg" alt="arXiv:1809.04609" /></a>
<a href="http://ascl.net/1707.003"><img src="https://img.shields.io/badge/ascl-1707.003-green.svg" alt="ascl:1707.003" /></a>
<a href="https://github.com/oscaribv/pyaneti/wiki"><img src="https://img.shields.io/badge/wiki-building-yellow.svg" alt="pyaneti wiki" /></a>

### Written by Barragán O.
#### email: oscar.barragan@physics.ox.ac.uk
#### Updated October, 2020


This is pyaneti 2.0 (beta), an upgraded version of the old pyaneti.

This code works in simililar way to [pyaneti](https://github.com/oscaribv/pyaneti), and you should be able to compile it and run it following
this [tutorial](https://github.com/oscaribv/pyaneti/wiki). But, *this new version uses
the lapack and blas libraries, be sure you have them, if no, the code may not compile*.

You should be able to re-run all your scripts of the old pyaneti in this one (But not all the
input files for this new pyaneti will run in the old one!). 

New in this version:

* Now the code runs in python 3.
* Changes in plots.
* It runs transit fits for single transits.
* It runs GPs and multi-GPs approaches (no tutorials provided by now).
* It runs multi-band fits (even if each band has a different cadence).

If you want to see the cool stuff that this new pyaneti can do, check 
[Barragán et al., 2019](https://academic.oup.com/mnras/article-abstract/490/1/698/5569669?redirectedFrom=fulltext).

### Notes

In the (I hope) nearly future, this will be the official version of pyaneti, by now,
use it with caution. 

I have not created tutorials for running single transits, GPs, and multi-bands fits yet. 
If you want to try one of these, feel free to contact me. 