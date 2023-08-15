# Ideas for research

Idea: Having very good point estimates for E(PF_i) is hard and not worth effort.

Fantasy projections should instead be informed by E(PF_i) and E(PF_hat_i - PF_i)^2. 
Why? 

Rough thesis:
1. Assessing players solely by point estimates (e.g., E(PF above league average starter)) is difficult
   1. To outperform others looking only at this measure requires having better predictions than anyone else
2. We will take for granted moving forward, that no manager can reliably choose a better team by avg(E(PF above league average starter)) than another.
   1. In other words, we assume for all managers, E(E(PF above league average starter)) = 0
      1. Where outer expected value is taken over players on roster
3. However, another important measure is variance - how much does performance vary for a player
   1. Fantasy football is not just getting right set of players on your team, but choosing right set of players to start each week
   2. By having a team with high variance players, you get more "capacity" or "ammunition" than fellow managers
      1. If both managers have a team with E(PF above league average starter) = 0, but one manager has variance 0, the other manager has "more control" over whether he wins the matchup or not
4. In a world where all teams have same total E(PF above leaguge average), league winners are those with higher variance players
   1. VERY IMPORTANT ASSUMPTION: team managers can discriminate and determine which players will score more in a given week

Things to investigate in research:
1. Is E(PF) heteroskedastic?
   1. Namely - variance it is determined by position and average draft position heading into season
   2. If this assumption is not met, there are no "higher variance players," and above study is useless
2. Is there predictable relationship between max that a fantasy team can score and the E(PF) and MSE(PF) of the players on that team
   1. Find it - can this relationship be can modeled by a linear equation?
3. Is there a predictable relationship between actual PF and max PF?
   1. Show actual PF based on real-life fantasy managers' decisions is near max PF
   2. Or above random decisions
   3. Or above some other reasonable baseline

1 above is done.
To do 2:
- Do following steps "enough" times to have sufficient data
  - Simulate or get realistic set of drafted teams for a given season
  - Calculate average weekly max score for all teams over a season
- Regress avg(PF_max) ~ Roster composition
- Determine some expectedPF / maxPF ratio - this is expected PF for a chosen fantasy football team

