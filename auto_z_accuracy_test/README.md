# Auto Z Calibration Accuracy

## Background

[Klipper Z Calibration](http://github.com/protoloft/klipper_z_calibration) is a great way to automatically set the offset between the nozzle, Z probe, and the build plate.  

The only problem to auto Z is that in some machines, the auto Z can be less reliable due to Nozzle Oozing.  When nozzle is heating up, some oozing on the nozzle is inevitable.  This can cause the endstop to trigger earlier, thus making the final offset "higher" and make the nozzle prints further from the build surface.  There are a number of solutions to this, including nozzle brush/pruge bucket, stiffer endstop with spring or magnets, and so on.

This script aims to test out different solutions, and make sure that the auto Z calibration is as repeatable as possible.

## What it does

Basically, the script would:

1. Heat up the nozzle
2. (if desired) run `CLEAN_NOZZLE`
3. run `CALIBRATE_Z`
4. take the z offset result, store it.
5. intentionally do nothing for a few minutes, let the nozzle ooze.
6. repeat 2-5 for N times.

And finally, calculate the standard deviation of all the offset.

## Usage

Clone the repo or grab the python script, put it on your pi, then just:

```
python3 z_calibration_accuracy.py
```

## Credit

Most of the script is a shameless ctrl+c from whoppingpochard's [measure_thermal_behavior](http://github.com/tanaes/measure_thermal_behavior).  Thanks WP for writing reusable & readable code!



