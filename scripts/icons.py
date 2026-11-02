from PIL import Image, ImageDraw
import numpy as np
S=4; N=128*S
W=(255,255,255,255)
def canvas(): 
    im=Image.new('RGBA',(N,N),(0,0,0,0)); return im,ImageDraw.Draw(im)
def fin(im,name): im.resize((128,128),Image.LANCZOS).save(f'assets/{name}')
def p(x): return x*S
# home
im,d=canvas()
d.polygon([(p(64),p(14)),(p(122),p(66)),(p(106),p(66)),(p(106),p(112)),(p(22),p(112)),(p(22),p(66)),(p(6),p(66))],fill=W)
d.rounded_rectangle([p(52),p(76),p(76),p(112)],radius=p(4),fill=(0,0,0,0))
d.rectangle([p(88),p(22),p(100),p(46)],fill=W)
# door cut-out
im2=im.copy(); a=np.array(im2); 
mask=Image.new('L',(N,N),0); md=ImageDraw.Draw(mask); md.rounded_rectangle([p(52),p(78),p(76),p(112)],radius=p(3),fill=255)
alpha=np.array(im.split()[3]); alpha[np.array(mask)>0]=0
im.putalpha(Image.fromarray(alpha)); fin(im,'icon_home.png')
# overview: bar chart
im,d=canvas()
d.rounded_rectangle([p(14),p(14),p(114),p(114)],radius=p(14),outline=W,width=p(7))
for x,h in [(34,28),(58,48),(82,66)]:
    d.rounded_rectangle([p(x),p(100-h),p(x+14),p(100)],radius=p(3),fill=W)
fin(im,'icon_overview.png')
# detail: table
im,d=canvas()
d.rounded_rectangle([p(12),p(18),p(116),p(110)],radius=p(12),outline=W,width=p(7))
d.rectangle([p(12),p(44),p(116),p(52)],fill=W)
d.rectangle([p(54),p(44),p(62),p(110)],fill=W)
d.rectangle([p(12),p(76),p(116),p(82)],fill=W)
fin(im,'icon_detail.png')
# story: speech bubble with lines
im,d=canvas()
d.rounded_rectangle([p(12),p(16),p(116),p(90)],radius=p(14),outline=W,width=p(7))
d.polygon([(p(36),p(88)),(p(36),p(116)),(p(64),p(90))],fill=W)
for y,x2 in [(40,98),(56,98),(72,74)]:
    d.rounded_rectangle([p(30),p(y-3),p(x2),p(y+3)],radius=p(3),fill=W)
fin(im,'icon_story.png')
# logo from cover bg
src=Image.open('/home/claude/in/x_p2/Report/StaticResources/RegisteredResources/Explorar_an_lise_(1)7854686485638407.png').convert('RGB').crop((98,98,332,204))
a=np.array(src).astype(float); lum=a.mean(axis=2)
alpha=np.clip((lum-110)/(235-110),0,1)*255
out=np.dstack([np.full(lum.shape,255),np.full(lum.shape,255),np.full(lum.shape,255),alpha]).astype('uint8')
Image.fromarray(out,'RGBA').save('assets/logo_dio.png')
print('ok')
