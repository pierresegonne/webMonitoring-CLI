# Enhancements

## Monitoring

First of all, I think that the __indicators__ system could be enhanced greatly.
As it is, to add an indicator you would need to create the indicator computer method in the monitor class,
map its displayer to its actual name (ex: MAX for maxTime) in the indicatorsType dictionary, add the field in the data dictionnaries ({'website': website, 'frame': timeframe,'time': currentTime, 'indicators': {'maxTime': maxTime, 'avgTime': avgTime, 'availability': availability, 'status': status}})
and manage its display color in the display system. Thus only someone familiar with the application can add and remove indicators, 
and I find this problematic as it makes the application rigid, and personalization difficult

Then, (see todo n2 int he monitor class), I think that __logs__ management can be enhanced. For now, at each check interval,
the monitoring subprocess for a website creates a log of the request and stores it in the website instance, in a dictionary called
log. The thing is that the application doesn't need logs of requests that happened more than one hour ago. Thus, to improve memory management 
it should be useful to delete logs that happened more than one hour ago. 

Finally, (see todo n2), I think that it could be useful to let the user decide if they want to define a specific __timeout__
for the website requests. For now, the timeout is the check interval


## Display

Change indicators and stats with cursor

User inside curses

## User Management

On the other side, from the user management perspective, I think that allowing the user to choose whether he wants to 
receive mail alerts would improve user friendliness.

Finally, 