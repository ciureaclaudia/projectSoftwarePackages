/*-	crearea unui set de date SAS din fișiere externe, OK
-	crearea și folosirea de formate definite de utilizator, OK
-	procesarea iterativă și condițională a datelor, OK (for loop)
-	crearea de subseturi de date, OK
-	utilizarea de funcții SAS, OK
-	combinarea seturilor de date prin proceduri specifice SAS și SQL, OK
-	utilizarea de masive, OK (mcu array)
-	utilizarea de proceduri pentru raportare,  OK(print)
-	folosirea de proceduri statistice, OK(freq,sort,rank)
-	generarea de grafice.
*/

/* 1. CREARE SET DATE - citire fisier csv*/
filename mycsv '/home/u63368544/proiect/mcu_box_office.csv';

proc import datafile=mycsv 
    out=movies 
    dbms=csv 
    replace;
    getnames=yes;
run;


/* 2.	FORMAT afisare mcu_phase */
proc format;
  value mcu_phase_format
    1 = '1st phase'
    2 = '2nd phase'
    3 = '3rd phase'
    other = 'crt phase';
run;
data movies;
	set movies;
    format mcu_phase mcu_phase.;
	mcu_phase_formatted = put(mcu_phase, mcu_phase_format.);
run;
title "MCU Phase Formatted";
proc print data=movies;
var movie_title mcu_phase_formatted release_date ;
run;


/* 3. FUNCTII - creare coloane */
data movies;
	set movies;
	
	length production_budget_num 8; /*verifica lung max*/
	production_budget_num = input(compress(production_budget, ","), 12.); 
	length worldwide_box_office_num 8;
	worldwide_box_office_num = input(compress(worldwide_box_office, ","), 12.); /*PT TOATE CELE $ SUME*/
	  
	profit=worldwide_box_office_num-production_budget_num;
	  
	mean_score= (audience_score+tomato_meter)/2;
	
	audience_score_proc=put(audience_score, percent7.); /*are 2 cifre extra*/
	tomato_meter_proc=put(tomato_meter, percent7.); 
	release_day = day(release_date);
run;
title "Added and formatted columns";
proc print data=movies;
format worldwide_box_office_numeric dollar12. 
production_budget_num dollar12.
profit dollar12.
format release_date MONYY.;
run;


/* 4. SUBSET - fazele trecute - preferat de public vs critic*/
data movie_phases_critics movie_phases_audience;
	set movies;
	where mcu_phase in (1,2,3);
	if audience_score lt tomato_meter then output movie_phases_critics;
	else if audience_score gt tomato_meter then output movie_phases_audience;
run;
title "Past MCU Phases movies preffered by critics";
proc print data=movie_phases_critics;
	var movie_title mcu_phase tomato_meter audience_score;
run;
title "Past MCU Phases movies preffered by audience";
proc print data=movie_phases_audience;
	var movie_title mcu_phase tomato_meter audience_score;
run;


/* 5. CONDITIONAL - categorii in functie de scor si profit */
data movie_categories;
	set movies;
	length category $15.;
	if mean_score ge 85 and profit ge mean(profit) then
		category="high quality";
	else if mean_score ge 75 and mean_score lt 85 and profit ge mean(profit) then
    	category="medium quality";
	else if mean_score lt 75 or profit lt mean(profit) then
		category="low quality";
run;
title "Movie categories based on profit and scores means";
proc print data=movie_categories;
	var movie_title mean_score profit category;
	format profit dollar12. mean_score percent7.2;
run;

/* 6. COMBINARE SAS - pe baza bugetului*/
proc sort data=movie_phases_critics;
    by production_budget_num;
run;
proc sort data=movie_phases_audience;
    by production_budget_num;
run;
data movies_merged;
	merge  movie_phases_audience (drop=tomato_meter audience_score in=mpa) 
			movie_phases_critics (drop=tomato_meter audience_score in=mpc) ;
	by production_budget_num;
	if mpc and mpa;
RUN;
title "Movies merged based on budget";
proc print DATA = movies_merged;
	var movie_title production_budget_num tomato_meter_proc audience_score_proc;
	format production_budget_num dollar12.;
run;

/* 7.COMBINARE SQL (right) - pe baza profitului*/
PROC SQL;
CREATE TABLE movies_left as
SELECT m1.movie_title, m1.mcu_phase, m1.category, m2.mean_score, m2.profit
FROM movie_categories m1 
RIGHT JOIN movies_merged m2
ON m1.profit = m2.profit
ORDER BY profit;
QUIT;
title "Movies right joined based on profit";
proc print DATA = movies_left;
	var movie_title mcu_phase category mean_score profit;
	format profit dollar12.;
run;
	
/* 8.SORTARE - dupa medie scoruri*/ 
proc sort data=movies;
    by descending mean_score;
run;
proc rank data=movies out=movies_ranked ties=low reverse;
    var mean_score;
    ranks rank;
run;
title "Movies ranked based on scores";
proc print data=movies_ranked;
    var movie_title mean_score rank;
run;


/* 9. MASIVE + ITERATIV - procente profit*/
proc freq data=movies;
    tables mcu_phase /nocum nopercent;
run;
proc sql;
    create table movies_agg_sum as
    select mcu_phase, sum(profit) as sum_profit
    from movies
    group by mcu_phase;
quit;
proc print data=movies_agg;
    var mcu_phase sum_profit;
run;
data movies_with_percent;
    merge movies movies_agg_sum;
    by mcu_phase;
run;
DATA movies_array;
SET movies_with_percent;
ARRAY phase {*} mcu_phase; 
    DO i = 1 TO dim (phase);
      IF phase(i) NOT IN (1,2,3) then
      call missing(phase(i)); 
 	  ELSE profit_phase_proc= round(100*profit/sum_profit, 3);
    END;
DROP i;
RUN;
title "Profit percents for each MCU phase";
proc print data=movies_array;
    var movie_title mcu_phase profit profit_phase_proc;
    format profit_phase_proc percent7.2;
run;
