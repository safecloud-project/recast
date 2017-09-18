# BW

The goal of this experiment is to evaluate the amount of traffic during reconstruction with STeP.

![Example](./traffic.pdf)

## Requirements
In order to run these experiments, you will need:

* docker
* docker-compose
* bash 4+
* python 2.7
* gnuplot

## Run the experiment

From the `playcloud/exerpiments/bw` directory, start the `run.sh` script
```bash
./run.sh
```

## Parse and plot
Once the experiment has finished running, make sure you have a `data` directory.
```bash
mkdir -p data
```
Then run the parsing script.
```bash
./parse.py results > data/bw.csv
```
Finally, run the plotting script.
```bash
./plot.gp
```
