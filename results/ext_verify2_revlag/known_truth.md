# Known-truth check of tolerant_v4L (hand-built 4-node SEM)

truth: C[1,0]=1.615, peak lag 0->1 = 0, C[2,0]=1.359 peak 0

- (1) v4L C/lo/hi bit-identical to v4 under same rng: 48/48
- (2) cumulative(theta_v4L) == C in reversed cell: 24/24
- (3) none cell theta identical: 24/24
- (4) peak-lag hit on reversed pair 0->1 (truth peak 0): v4 0.000, v4L 0.708 (n=24)
- (4b) peak-lag hit on downstream pair 0->2: v4 0.000, v4L 0.500
- (5) coverage of C[1,0] by v4 interval in reversed cell: 0.792 (v4L identical: 0.792)
