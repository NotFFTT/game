# Apple Smash

Apple Smash is an online multiplayer battle game allowing up to four unique player characters. Apple Smash utilizes the Python Arcade game engine and the server is hosted on Digital Ocean.


# Watch the Demo!

Click [here](https://www.youtube.com/watch?v=L9-kgbdOjHE) to view the demo! Please note the time stamps in the description to view introductions, project overview, or the live demo as desired. 

# Resources

- Character sprites: https://chierit.itch.io
- Tiled Map Editor: https://www.mapeditor.org
- Source code: https://github.com/NotFFTT/game
- Python Arcade library: https://api.arcade.academy/en/latest/
- Python Arcade sockets example: https://github.com/Cleptomania/square_game
- Socket programming guide: https://youtu.be/3QiPPX-KeSc
- Python documentation: https://docs.python.org/3/library/
- Server hosting: https://www.digitalocean.com

## How to Play

- Clone this Repo
- Install Dependencies
- Open terminal, cd into root directory of Game
- Execute game with ```python main.py```
- Enjoy!
- Example: git clone [this repo] -> poetry install -> poetry shell -> python main.py

Note: will need to host server (found in sockets/server2.py) somewhere that is able to run a python script and sockets. This can be done locally (switch global ADDRESS constant to 'localhost', for example), but this may be cause a challenge getting clients not on your network to access it. Instead, it might be easiest to open up a droplet on Digital Ocean, open up a console to the droplet, and paste the server2.py file into it (eg: touch a new file -> sudo nano to modify the file -> copy/paste the code and save it -> and then run it using a python3 server2.py command. No dependencies are needed for the server.

## Controls

- A,W,S,D or Arrows for Directions
- E - Attack
- R - Special Attack
- Space, Up, or W to jump
- F to respawn
- 1,2,3,4 to change character in-game
- ESC to close socket

## Team

- Miguel Fierro
- David Hecker
- Chloe Nott
- Brannon Starnes

## Cooperation Plan

Every person on your team is an asset. This is your chance to discover the hidden strengths and areas for growth for each team member.

- What are the key strengths of each person on the team and how can you use them?
  - David - backend, follow direction
  - Chloe - Unique perspectives. Can contribute to creative solutions.
  - Brannon - Keeps teams on track, easily recognizes distractors and realigns focus. Can use these strengths to ensure work flow is conducted efficiently. 
  - Miguel - dependability and reliability
- In which professional competencies do you each want to develop greater strength?
  - David- Collaboration, tool familiarity
  - Chloe - Collaboration, communication
  - Brannon - Technical Craftsmanship and  Handling Ambiguity
  - Miguel -root cause solution (identifying problems, testing/troubleshooting)
- Knowing that every person in your team needs to understand all aspects of the project, how do you plan to approach the day-to-day work?
  - We will meet for morning standups in Remo at 9am PST to discuss goals for the day, update project board, work together in remo/slack as needed, and discuss blockers or   problems etc.

#### NOTE: Undoing, Redoing, Replacing, or otherwise steamrolling the project as an individual is considered to be unacceptable. Account for the inevitable divergence of ideas, execution tasks, and assignments of duties here.

## Conflict Plan

Your team should agree on a process for handing disagreements, should they arise. It is better to have a plan in place ahead of time so you can all refer back to it when necessary.

- What will be your group’s process to resolve conflict, when it arises?
  - Keep resolution at the lowest level possible. Attempt to resolve one on one, but will use a mediator if needed. If unable to reach agreement, the group will contact the  instructor or TA for guidance. 
  - Each member will have available to them a "Veto Card" which can be used once only to override a decision they feel strongly about. Once this "Veto Card" is used, members will respect the decision and cooperate to make it so.
- What will your team do if one person is taking over the project and not letting the other members contribute?
  - Team should discuss this issue at anytime, however, morning meetings are an excellent time to bring these matters to the table. Discussions should lead to an agreeable plan to move forward. 
- How will you approach each other and the challenges of the project knowing that it is impossible for all members to be at the exact same place in understanding and skill level?
  - Team should work together to 1) share knowledge and bring each other up to speed as much as possible and 2) have patience and understanding while working at different skill levels.
  - Members should strive to produce easy-to-understand code.
- How will you raise concerns to members who are not adequately contributing?
  - Each member agrees to take constructive criticisms which can adjust work patterns. 
  - Criticisms can be given, respectfully, at any time. 
- How and when will you escalate the conflict if your resolution attempts are unsuccessful?
  - When an issue arises that cannot be resolved effectively, an attempt to reach an instructor or TA will occur as soon as conveniently possible.

## Communication Plan

Before beginning to tackle the project, determine how your group will communicate with each other. This is not an individual effort. Make sure everyone feels comfortable with the identified methods of speaking up.

- What hours will you be available to communicate?
  - Business hours: 9-5 is expected time to communicate
  - All members have agreed that communication outside business hours is ok.
- What platforms will you use to communicate (ie. Slack, phone …)?
  -Slack is going to be the most effective way to communicate outside of Remo.
- How often will you take breaks?
  - As needed. If member needs a break, take a break. 
  - Every couple hours, at least take a break to update other team members on progress.
- What is your plan if you start to fall behind?
  - Adjust plan to hit target (i.e. slash features)
- How will you communicate after hours and on the weekend?
  - Slack
- What is your strategy for ensuring everyone’s voice is heard?
  - Be respectful, encourage ideas and feedback from others.
- How will you ensure that you are creating a safe environment where everyone feels comfortable speaking up?
  - Be respectful when offering feedback and understanding everyone's ideas have value.

## Work Plan

Explain your work plan to track whether everyone is contributing equally to all parts of the project, and that each person is working on “meaty” problems. This should prevent “lone wolf” efforts and “siloed” efforts.

#### NOTE: While researching and experimentation is always encouraged, writing and/or committing code to the project on your own during non-working hours or over the weekend is never acceptable. This puts the entire project at risk. Be explicit in calling out your work hours and the distribution of tasks.

- How you will identify tasks, assign tasks, know when they are complete, and manage work in general?
  - We will refer to the project management board for assigned tasks and their progress.
- What project management tool will be used?
  - Github Projects

## Git Process

- What components of your project will live on GitHub?
  - Everything
- How will you share the repository with your teammates?
  - We will create an Org and ensure all members are admins.
- What is your Git flow?
  - Each sub team will work in a relative branch, which will be pushed to a 'work-floor' branch. 
- How many people must review a PR?
  -2 Reviewers 
- Who merges PRs?
  -Anyone can merge PRs after review.
- How often will you merge?
  - EOD at minimum
- How will you communicate that it’s time to merge?
  - Talk to each other, ensure all teams are ready for a merge.
