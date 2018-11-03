include "globals.mzn";

int: turnos;

array[1..turnos] of var 0..1: G21_RA_1;
constraint sum(G21_RA_1) = 1;

array[1..turnos] of var 0..1: G22_RA_1;
constraint sum(G22_RA_1) = 1;

array[1..turnos] of var 0..1: G23_RA_1;
constraint sum(G23_RA_1) = 1;

array[1..turnos] of var 0..1: G21_RA_2;
constraint sum(G21_RA_2) = 1;

array[1..turnos] of var 0..1: G22_RA_2;
constraint sum(G22_RA_2) = 1;

array[1..turnos] of var 0..1: G23_RA_2;
constraint sum(G23_RA_2) = 1;

array[1..turnos] of var 0..1: G21_RA_3;
constraint sum(G21_RA_3) = 1;

array[1..turnos] of var 0..1: G22_RA_3;
constraint sum(G22_RA_3) = 1;

array[1..turnos] of var 0..1: G23_RA_3;
constraint sum(G23_RA_3) = 1;

constraint forall (i in 1..turnos) (G21_RA_1[i]+G21_RA_2[i]+G21_RA_3[i] <= 1);

constraint forall (i in 1..turnos) (G22_RA_1[i]+G22_RA_2[i]+G22_RA_3[i] <= 1);

constraint forall (i in 1..turnos) (G23_RA_1[i]+G23_RA_2[i]+G23_RA_3[i] <= 1);

predicate join_groups(array[int] of var int: g1, array[int] of var int: g2) = forall (i in 1..turnos) (g1[i] == g2[i]);

constraint join_groups(G21_RA_1, G22_RA_1);

constraint forall(i in 1..turnos) (G22_RA_1[i]+G23_RA_1[i] <= 1);

constraint forall(i in 1..turnos) (G21_RA_2[i]+G22_RA_2[i] <= 1);

constraint forall(i in 1..turnos) (G21_RA_3[i]+G22_RA_3[i]+G23_RA_3[i] <= 1);

function var int: index(array[int] of var int: x) = sum([x[i]*i | i in 1..length(x)]);

predicate diff_day(array[int] of var int: g1, array[int] of var int: g2) = (index(g1) - 1) div 6 != (index(g2) - 1) div 6;

constraint diff_day(G22_RA_1,G22_RA_2);
constraint diff_day(G22_RA_1,G22_RA_3);
constraint diff_day(G22_RA_2,G22_RA_3);
constraint diff_day(G21_RA_1,G21_RA_2);
constraint diff_day(G21_RA_1,G21_RA_3);
constraint diff_day(G21_RA_2,G21_RA_3);
constraint diff_day(G23_RA_1,G23_RA_2);
constraint diff_day(G23_RA_1,G23_RA_3);
constraint diff_day(G23_RA_2,G23_RA_3);

constraint index(G22_RA_1) < index(G22_RA_2);
constraint index(G22_RA_2) < index(G22_RA_3);
constraint index(G21_RA_1) < index(G21_RA_2);
constraint index(G21_RA_2) < index(G21_RA_3);
constraint index(G23_RA_1) < index(G23_RA_2);
constraint index(G23_RA_2) < index(G23_RA_3);

constraint G21_RA_1[1] = 0;
constraint G22_RA_1[1] = 0;
constraint G23_RA_1[1] = 0;
constraint G21_RA_2[1] = 0;
constraint G22_RA_2[1] = 0;
constraint G23_RA_2[1] = 0;
constraint G21_RA_3[1] = 0;
constraint G22_RA_3[1] = 0;
constraint G23_RA_3[1] = 0;
constraint G21_RA_1[2] = 0;
constraint G22_RA_1[2] = 0;
constraint G23_RA_1[2] = 0;
constraint G21_RA_2[2] = 0;
constraint G22_RA_2[2] = 0;
constraint G23_RA_2[2] = 0;
constraint G21_RA_3[2] = 0;
constraint G22_RA_3[2] = 0;
constraint G23_RA_3[2] = 0;
constraint G21_RA_1[3] = 0;
constraint G22_RA_1[3] = 0;
constraint G23_RA_1[3] = 0;
constraint G21_RA_2[3] = 0;
constraint G22_RA_2[3] = 0;
constraint G23_RA_2[3] = 0;
constraint G21_RA_3[3] = 0;
constraint G22_RA_3[3] = 0;
constraint G23_RA_3[3] = 0;

constraint G21_RA_1[7] = 0;
constraint G22_RA_1[7] = 0;
constraint G23_RA_1[7] = 0;
constraint G21_RA_2[7] = 0;
constraint G22_RA_2[7] = 0;
constraint G23_RA_2[7] = 0;
constraint G21_RA_3[7] = 0;
constraint G22_RA_3[7] = 0;
constraint G23_RA_3[7] = 0;
constraint G21_RA_1[8] = 0;
constraint G22_RA_1[8] = 0;
constraint G23_RA_1[8] = 0;
constraint G21_RA_2[8] = 0;
constraint G22_RA_2[8] = 0;
constraint G23_RA_2[8] = 0;
constraint G21_RA_3[8] = 0;
constraint G22_RA_3[8] = 0;
constraint G23_RA_3[8] = 0;
constraint G21_RA_1[9] = 0;
constraint G22_RA_1[9] = 0;
constraint G23_RA_1[9] = 0;
constraint G21_RA_2[9] = 0;
constraint G22_RA_2[9] = 0;
constraint G23_RA_2[9] = 0;
constraint G21_RA_3[9] = 0;
constraint G22_RA_3[9] = 0;
constraint G23_RA_3[9] = 0;

constraint G21_RA_3[10] = 0;
constraint G22_RA_3[10] = 0;
constraint G23_RA_3[10] = 0;
constraint G21_RA_3[11] = 0;
constraint G22_RA_3[11] = 0;
constraint G23_RA_3[11] = 0;
constraint G21_RA_3[12] = 0;
constraint G22_RA_3[12] = 0;
constraint G23_RA_3[12] = 0;

solve satisfy;