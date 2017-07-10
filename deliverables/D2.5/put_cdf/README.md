# D2.5

A folder containing data used in SafeCloud's D2.5 document.

## CDF

A CDF plot displaying the impact on request latency of changing the entanglement scheme used in playcloud.

### Experiment
Playcloud is run in with different configurations on the IIUN cluster. Using apache bench, we sent 1000 concurrent requests to store 1MB documents. The requests are launched with a level of concurrency of 4 (4 requests running in parrallel at all time)

The components are deployed as follows over 34 VMs:

* 1 VM (8 cores, 7680MB of RAM) with colocated proxy, encoder and zookeeper containers
* 1 VM (4 cores, 4GB of RAM) with the client
* 32 VMs (2 cores, 1GB of RAM) each running a redis container

The different configurations are described in the table below.
+-------------------------+--------------+----------+
|       Folder            | Entanglement | Replicas |
+-------------------------+--------------+----------+
| step_no_replication     |  STeP(5,2,7) |    1     |
+-------------------------+--------------+----------+
| step                    |  STeP(5,2,7) |    3     |
+-------------------------+--------------+----------+
| dagster_no_replication  | Dagster(5,2) |    1     |
+-------------------------+--------------+----------+
| dagster                 | Dagster(5,2) |    3     |
+-------------------------+--------------+----------+


### Parse data

The data obtained from the experiment can be parsed using `parse.py` script.
```bash
python parse.py > cdf.csv
```

### Plot

```bash
gnuplot cdf.gp
```
This plot relies on the `cdf.csv` file.


### Interpretation
On first read of the plot, the observations from the results are two-fold:

* The difference in performance between STeP(5,2,7) is noticeable compared to Dagster(5,2).
* The storage of extra replicas does not significantly slow down the request latency

However, limiting the interpretation to those two visible features would be unfair to the guarantees that these two entanglement schemes bring to the table.
Indeed, if both systems can provide anti-tampering without any replication, STeP is the only one that actually offers redundancy.
