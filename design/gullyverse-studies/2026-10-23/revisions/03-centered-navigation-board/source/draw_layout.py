import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
from pathlib import Path
import json
O=Path(__file__).resolve().parents[1];out=O/'review';out.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'svg.fonttype':'none'})
fig,ax=plt.subplots(figsize=(11,15));fig.patch.set_facecolor('#f1ede1');ax.set_facecolor('#e9e4d5')
for x in [-11.2,4]:
 for y in [-25,-16,-7,2]:ax.add_patch(Rectangle((x,y-4.25),7.2,8.5,facecolor='#a8a08b',edgecolor='#62655c',lw=.8))
ax.add_patch(Rectangle((-3.6,-30),7.2,35,facecolor='#c7c3b6',edgecolor='#777e73'))
ax.add_patch(Rectangle((-8,5),16,9,facecolor='#c7c3b6',edgecolor='#777e73'))
ax.add_patch(Rectangle((-16,14),32,34,facecolor='#d4d3c5',edgecolor='#5b766c',lw=2))
# Reveal block removed: leave roof opening unobstructed.
ax.text(1,14.4,'OPEN CONNECTION\nNo reveal column',ha='center',va='center',fontsize=8,color='#2f584e')
ax.add_patch(Rectangle((-3.2,20.6),6.4,.8,facecolor='#35534b'));ax.text(5.3,20.3,'NAVIGATION BOARD\nCentered in approach',va='center',fontsize=8)
ax.add_patch(Rectangle((14.5,23),.6,12,facecolor='#b56b46'));ax.text(18,29,'D · TEAM\nRIGHT\nPortrait paste-ups',va='center',fontsize=10)
ax.add_patch(Rectangle((-15.1,23),.6,12,facecolor='#c6a851'));ax.text(-18,29,'E · EVENTS\nLEFT\nProxy event art',ha='right',va='center',fontsize=10)
ax.add_patch(Rectangle((-7.28,45.6),14.56,.5,facecolor='#295c74'));ax.text(0,49,'G · EXISTING DIGITAL SCREEN / NO PHYSICAL STAGE',ha='center',fontsize=9)
for y in [28.7,31.6,34.5,37.4,40.3,42.3]:
 for x in [-10,-7.6,-5.2,-2.8,2.8,5.2,7.6,10]:ax.plot(x,y,'o',ms=4,color='#59615d')
ax.text(0,34,'F\nCROWD\nCAMERA\nAISLE',ha='center',va='center',fontsize=8,color='#2f584e')
ax.text(-6,24.5,'CYPHER\nCIRCLE',ha='center',va='center',fontsize=8);ax.add_patch(plt.Circle((-6,25),4.3,fill=False,color='#99977e',linestyle='--'))
for name,p,color in [('Visitor entry',[(0,-27),(0,4),(-1.8,7.8),(-6.1,10.9),(-6.1,18),(0,22)],'#24685a'),('Screen',[(0,22),(0,25.2),(-.7,30.7),(.45,33.3),(0,36.5)],'#386c92'),('Team',[(0,22),(12.8,22),(13.3,28)],'#a64e35'),('Events',[(0,22),(-12.8,20.4),(-13.3,28)],'#a78726')]:
 for a,b in zip(p,p[1:]):ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=12,color=color,lw=2))
ax.plot(0,22,'o',color='#24685a',ms=9);ax.text(-.5,20,'C · HUB',ha='right',fontsize=10,weight='bold')
ax.text(0,-33,'A · LANDING / SHOPS BOTH SIDES',ha='center',fontsize=10,weight='bold');ax.text(0,-8,'6.8m lane\nRamp rises 1.2m / 24m\n1:20; no stairs',ha='center',fontsize=9);ax.text(-9,8,'B · HAZE /\nCROWD GLIMPSE',ha='right',fontsize=9)
ax.annotate('',(-16,52),(16,52),arrowprops=dict(arrowstyle='<->'));ax.text(0,53,'32m rooftop width',ha='center',fontsize=9)
ax.plot([-14,-4],[-30,-30],color='#333d37',lw=3);ax.text(-9,-29,'10m',ha='center',fontsize=8);ax.set_xlim(-26,26);ax.set_ylim(-36,57);ax.set_aspect('equal');ax.set_xlabel('X / metres · LEFT ←   → RIGHT');ax.set_ylabel('Y / metres · FORWARD ↑');ax.grid(alpha=.15)
fig.suptitle('GULLYVERSE / ONE SHARED SITE LAYOUT\nBlender concept study · A/B/C share architecture, routes and cameras',fontsize=15,weight='bold',y=.97);fig.text(.05,.03,'Concept coordinates only. Existing website registry and WIP remain unchanged.\nRaised market podium + gentle ramp → rooftop. Structural loading and real-site feasibility are not certified.',fontsize=9)
fig.savefig(out/'master-layout.png',dpi=160,bbox_inches='tight');fig.savefig(out/'master-layout.svg',bbox_inches='tight');plt.close(fig)
fig,ax=plt.subplots(figsize=(13,5));fig.patch.set_facecolor('#f1ede1');ax.set_facecolor('#f1ede1');ax.fill_between([-30,-10,14,48],[6,6,7.2,7.2],[5.6,5.6,6.84,6.84],color='#8d978b');ax.plot([-30,-10,14,48],[6,6,7.2,7.2],lw=3,color='#2e6758');ax.plot([-35,52],[0,0],color='#605e54',lw=2)
for y in [15,28,44]:ax.add_patch(Rectangle((y-.3,0),.6,6.84,color='#8d978b'))
ax.text(18,10,'Open connection / no reveal column',ha='center',fontsize=9)
ax.text(-23,6.8,'Elevated lane / deck +6.0m',ha='center');ax.text(2,8,'1.2m rise over 24m\n1:20 continuous ramp',ha='center');ax.text(33,8,'Rooftop / +7.2m',ha='center');ax.text(-25,1.4,'Lower street / podium base',ha='center');ax.set_xlim(-34,52);ax.set_ylim(-1,14);ax.set_xlabel('Y / metres');ax.set_ylabel('Z / metres');ax.grid(alpha=.15);ax.set_title('ACCESS SECTION / NO STAIR OR ELEVATOR REQUIREMENT\nA speculative supported podium, not a real construction specification',fontsize=12);fig.savefig(out/'access-section.png',dpi=160,bbox_inches='tight');fig.savefig(out/'access-section.svg',bbox_inches='tight');plt.close(fig)
print('LAYOUT_AND_SECTION_SAVED')
