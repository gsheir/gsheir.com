---
title: "Part 1: Assessing and improving Arsenal Women’s attacking corners using data"
description: "Why do Arsenal run so many front post corner routines, and how can we use data to assess how good they are at it?"
pubDate: 2025-10-20
category: Data analysis
tags: [Arsenal, Set pieces, Football]
series:
  name: "Arsenal Women’s attacking corners"
  part: 1
featured: true
---

I was at the Emirates last Saturday when Arsenal just about got the win against Brighton, and one of the more interesting (and mildly infuriating) features of that game were the amount of corners hit low to the front post. The success rate there was pretty low, and it’s been pretty low so far this season, with 1 goal from about 45 corners. I decided to try and figure out why this was the case.

This is a classic two-part piece – my findings and recommendations are in Part 1 (here), and my methodology, including data collection, analysis methods and data science-y things, are in [Part 2: A data driven approach to corner analysis and assessment](/blog/arsenal-corners-part-2/).

## Arsenal’s template corner play provides a triple threat for unpredictability

![Arsenal’s template corner play](https://images.gsheir.com/arsenal_corners/Football%20analysis-Template%20play.drawio.png)

Arsenal tend to run a template play, where there are specific groups that players are assigned to:

- A player presents the short corner option near to the corner taker. The taker for one side becomes the short corner option on the other side. (McCabe, Caldentey)
- Three players stack near the penalty spot, then attack the edge of the 6-yard box, usually threatening both the front and back post (three from Russo, Blackstenius, Catley, Maanum, Wubben-Moy)
- Two players start inside the 6-yard box (Foord, Reid, Kelly, sometimes Smith)
- Several players hang around the edge of the 18-yard box to mop up any loose balls (Little, Smith, Fox)

Therefore there are 3 potential targets (short, front post, back post) at all corners, which means that the play is difficult to predict until the ball is delivered.

The 3-player stack is the core of the template play, and one of these players is usually the intended target for taking the shot (I call her the *shot target*). The way this template gets modified is in how the rest of the players act to give the shot target the best chance of connecting with the delivery.

## Blocking works well when deployed thoughtfully to create space for the shot target

A key feature of Arsenal’s corners is the use of blockers, similar to screening in basketball or linemen in American football. This isn't a new concept (Arsenal Men deploy it with great effect) but it is worth highlighting here as it is often instrumental in creating space for the shot target.

Particularly impressive is the use of blocking against multiple defenders at a time. Watch how smart initial positioning from Catley (number 7) and Reid (26) allow them to hold off two defenders each, giving Russo (23) a clear area at the front of the 6-yard box to attack.

![Arsenal’s corner blocking example front post](https://images.gsheir.com/arsenal_corners/Football%20analysis-Blocking%20front%20post.drawio.png)

 

![Arsenal’s corner blocking example 1](https://images.gsheir.com/arsenal_corners/gifs/blocking_brighton.gif)
*View this clip on [YouTube](https://www.youtube.com/live/ybQDwsrwIfg?t=2986s)*

In this example, Wubben-Moy (3) manages to deny 3 defenders the opportunity to get close to Russo. Notice how she barely makes an attempt to win the ball, and her cheeky drag of the defender’s arm to pull her across to block the path to Russo (23). You could also probably argue that Catley (7) was also pushing her defender away from Russo, giving her an uncontested header at goal.

![Arsenal’s corner blocking example back post](https://images.gsheir.com/arsenal_corners/Football%20analysis-Blocking%20back%20post.drawio.png)

 

![Arsenal’s corner blocking example 2](https://images.gsheir.com/arsenal_corners/gifs/blocking_city.gif)

 

![Arsenal’s corner blocking example 2 zoomed](https://images.gsheir.com/arsenal_corners/gifs/blocking_city_zoomed.gif)
*View this clip on [YouTube](https://www.youtube.com/live/riU2fTHdt2w?t=4621s)*

## Front post corners are set up well but the delivery needs to be further away from the touchline

To assess the quality of a play, I defined a play quality metric. In short, it is the "shot creation probability" that players provide at a corner, based on their role and how free they managed to get from their marker. An unmarked player whose role is to take a shot (as opposed to be a blocker or decoy) gets a score of 1, and the number goes down if they have a less dangerous role or if they are marked tightly. A full explanation is in Part 2.

Using this play quality metric, we see slightly better performance at front post plays. However, even though the shot targets are making the lead to the edge of the 6-yard box, the deliveries are often too close to the touchline. This probably explains a lot of the frustration felt at the Brighton game last week.

![Arsenal’s front post delivery locations](https://images.gsheir.com/arsenal_corners/left_front_post_delivery_vs_run_heatmap.png)

The relatively high play quality suggests that the corner routines are set up well, and the individual players are getting into good positions, relative to their markers, to attack the ball. Delivering the ball more consistently to the edge of the 6-yard box should improve the threat from those corners, like this one here:

![Arsenal’s corner delivery example](https://images.gsheir.com/arsenal_corners/gifs/good_front_post.gif)
*View this clip on [YouTube](https://www.youtube.com/live/ybQDwsrwIfg?si=adkyMMFpczf71nGg&t=4858)*

|  | Mean play quality |
| --- | --- |
| Front post, multiple shot targets | 1.856 |
| Front post, single shot target | 1.407 |
| Back post | 0.968 |
| Short lead | 1.495 |

*A note on this play quality metric: of the corners recorded, the lowest score was 0.58 (Brighton 63rd minute) and the highest score was 2.95 (Brighton 8th minute), to give a sense of scale.*

## Back post corners can benefit from late runs from deep

A key difference for Arsenal’s back post plays compared to their front post ones is how early the shot target arrives at the target zone. While this helps secure a place in that zone amongst the defenders, it becomes harder to generate enough power on the connection to be threatening. Notice how in both of these examples, the shot target arrives while the ball is still halfway through the air, and the contact generated afterwards lacks power as a result.

![Arsenal’s back post corner example 1](https://images.gsheir.com/arsenal_corners/gifs/back_post_early_arrival_1.gif)
*View this clip on [YouTube](https://www.youtube.com/live/aXBJsJDtoEg?t=1837s)*

![Arsenal’s back post corner example 2](https://images.gsheir.com/arsenal_corners/gifs/back_post_early_arrival_2.gif)
*View this clip on [YouTube](https://www.youtube.com/watch?v=bnbw1Ozc_2M&t=2075s)*

Delaying the shot target’s run so that she can attack the ball at pace would be ideal, but there is no guarantee that the space will be free to attack. This leads back to the blocking idea, and using blockers to clear space for the shot target to run into would increase the probability of getting a successful shot off.

## Sacrificing the triple threat to deploy multiple shot targets can be the remedy for variable deliveries

The reasoning goes like this - if the delivery can't be precise all the time, then placing multiple potential receivers in the area increases the chances of one of them connecting. Already we are seeing examples where multiple shot targets arrive all at once, and more often than not, they are all getting in front of their marker to attack the ball.

![Arsenal’s multiple shot targets example](https://images.gsheir.com/arsenal_corners/gifs/multiple_targets.gif)
*View this clip on [YouTube](https://www.youtube.com/live/ybQDwsrwIfg?t=494s)*

The triple threat that the template play provides has the benefit of spreading out the opposition’s zonal defence, but I would be interested to see Arsenal test out plays where the short corner option is removed, and they commit to setting up multiple shot targets in the delivery area. A front post play might look something a bit like this:

![Arsenal’s multiple front post shot targets](https://images.gsheir.com/arsenal_corners/Football%20analysis-Multiple%20front%20post.drawio.png)

And a back post play:

![Arsenal’s multiple back post shot targets](https://images.gsheir.com/arsenal_corners/Football%20analysis-Multiple%20back%20post.drawio.png)

Clearly a lot will depend on the opposition’s defensive setup (which I've not touched on at all in this piece), but hopefully these changes can lead to better outcomes at corners, and give Arsenal a different dimension in attack.

*Read Part 2 here: [Part 2: A data driven approach to corner analysis and assessment](/blog/arsenal-corners-part-2/)*
