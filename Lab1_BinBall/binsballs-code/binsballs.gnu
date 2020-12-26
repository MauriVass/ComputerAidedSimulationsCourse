set term pdf

set logscale x 10
set style data lines
set style fill transparent solid 0.4 noborder
set yrange [0:*]
set key left top

set ylabel "Max bin occupancy"
set xlabel "Bins/Balls"

set output "binsballs-5runs.pdf"
set title "Simulation with 5 runs"
plot "binsballs-5runs.dat" u 1:3 t "Upper bound",'' u 1:2 t "Lower bound",'' u 1:5 with lp lt 1 pt 7 ps 1 lw 1 t "Simulation", '' using 1:4:6 with filledcurves title '95% confidence'

set output "binsballs-10runs.pdf"
set title "Simulation with 10 runs"
plot "binsballs-10runs.dat" u 1:3 t "Upper bound",'' u 1:2 t "Lower bound",'' u 1:5 with lp lt 1 pt 7 ps 1 lw 1 t "Simulation", '' using 1:4:6 with filledcurves title '95% confidence'

set output "binsballs-40runs.pdf"
set title "Simulation with 40 runs"
plot "binsballs-40runs.dat" u 1:3 t "Upper bound",'' u 1:2 t "Lower bound",'' u 1:5 with lp lt 1 pt 7 ps 1 lw 1 t "Simulation", '' using 1:4:6 with filledcurves title '95% confidence'

set output "binsballs-manyruns.pdf"
set title ""
set ylabel "Relative error %"
set key right top
plot "binsballs-5runs.dat" u 1:($7*100) t "5 runs",\
"binsballs-10runs.dat" u 1:($7*100) t "10 runs",\
"binsballs-40runs.dat" u 1:($7*100) t "40 runs"