# Enhancements

## Monitoring

First of all, I think that the __indicators__ system could be enhanced greatly.
As it is, to add an indicator you would need to create the indicator computer method in the monitor class,
map its displayer to its actual name (ex: MAX for maxTime) in the indicatorsType dictionary, add the field in the data dictionnaries ({'website': website, 'frame': timeframe,'time': currentTime, 'indicators': {'maxTime': maxTime, 'avgTime': avgTime, 'availability': availability, 'status': status}})
and manage its display color in the display system. Thus only someone familiar with the application can add and remove indicators, 
and I find this problematic as it makes the application rigid, and personalization difficult

Then, (see todo n2 in the monitor class), I think that __logs__ management can be enhanced. For now, at each check interval,
the monitoring subprocess for a website creates a log of the request and stores it in the website instance, in a dictionary called
log. The thing is that the application doesn't need logs of requests that happened more than one hour ago. Thus, to improve memory management 
it should be useful to delete logs that happened more than one hour ago. 

Finally, (see todo n2), I think that it could be useful to let the user decide if they want to define a specific __timeout__
for the website requests. For now, the timeout is the check interval. This is problematic, if the timeout is reached, then checkInterval-(endSubProcess-startSubProcess)
(line 143 monitor.py) becomes negative and raises a ValueError exception. Allowing the user to set a new timeout would thus require a compatibility 
check with the check interval value.


## Display

Concerning the display management, I would like to allow navigation inside the display using the keyboard. I would like to allow for 
example to go trough the list of websites using the arrow keys if the window is too small to display all the websites. I would also allow 
to scroll through the alerts if the window is too small to display them all. 

This wouldn't be too difficult to add. I already have a script that allow to move the cursor (see display_curses line 139) and it could be 
adapted to modify the list of websites, stats and alerts displayed.


## User Management

On the other side, from the user management perspective, I think that allowing the user to choose whether he wants to 
receive mail alerts would improve user friendliness. He would also be able to specify the mail address which will receive the alerts.

Finally, integrating the user management interface in the curses display would improve the application usability. Only one command would
open the whole application and ask first to the user if he wants to access the user management part or the display. This would need a substantial 
work as it would require to re-design most of the display and user classes. 
