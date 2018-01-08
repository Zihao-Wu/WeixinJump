
import os #命令行模块
import threading #线程模块
import time #
import math
from PIL import Image
from PIL import ImageFilter
from PIL import ImageEnhance

# 微信跳一跳辅助 方式二，通过过滤背景色 最高803分

def shell(command):
	os.popen(command).read()

phoneFile="/sdcard/screencap/1.png"
file="2.png"
divicesName="5PNJVWG6NVNNCYV8"
startX=240
startY=340
resize=1

manTopRgb=(52,53,56)
manBottomRgb = (54,61,99)
def getScreencap():
	while True:
		startTime= time.time()
		shell("adb -s %s shell screencap -p %s" %(divicesName,phoneFile))
		shell("adb -s %s pull %s" %(divicesName,phoneFile+" ./"+file)) #获取屏幕截图

		endTime=time.time()
		# print("screencap ------%s"% (endTime-startTime))
		start=endTime
		im = Image.open(file)
		width,height = im.size

		# print(bgRGB)
		if im.getpixel((350,1620))==(255,255,255,255) and im.getpixel((700,1600))==(255,255,255,255) :
			# im.show()
			print("-------游戏结束--------重新开始")
			shell("adb -s %s shell input tap %d %d" %(divicesName,350,1620))
			time.sleep(2)
			continue

		r,g,b,a = im.split()
		im = Image.merge("RGB", (r,g,b))
		im1 = im.filter(ImageFilter.CONTOUR) # 滤波
		# im = im.filter(ImageFilter.EDGE_ENHANCE_MORE) 

		boxX,boxY,topY=getBoxXy(im1,startX,startY)
		manX,manY=getManXy(im)

		addPoint2(im1,boxX,boxY) #白
		addPoint2(im1,manX,manY) # 黑
		print("BoxXy %s %s ManXy %s %s" %(boxX,boxY,manX,manY))

		xlen = abs(boxX-manX)
		if(xlen<=10): #当前小人在最高点
			print("-----小人在最高点，-----")

			topLeftY=0
			leftX=leftY=0
			xLeftlen=xlen
			leftTopY=topY
			while xLeftlen<=40: # 盒子在人左边
				leftX,leftY,leftTopY=getBoxXy(im1,startX,leftTopY+2)
				xLeftlen = abs(leftX-manX)
			else:
				topLeftY=leftTopY

			topRightY=0
			rightX=rightY=0
			xRightLen=xlen
			rightTopY=topY
			while xRightLen<=40: # 假设盒子在人右边
				rightX,rightY,rightTopY=getBoxXy(im1,manX+40,rightTopY+2)
				xRightLen = abs(rightX-manX)
			else:
				topRightY=rightTopY

			if leftTopY<=rightTopY:
				boxX=leftX
				boxY=leftY
				print("-----盒子在小人左边-----")
			else:
				boxX=rightX
				boxY=rightY
				print("-----盒子在小人右边-----")
			
			print("getBoxXy %s %s" %(boxX,boxY))
			addPoint2(im1,boxX,boxY) #白
			# im1.show()
		elif(xlen<80): # 显示超越xxx
			print("-----超越了xxx,等一会再跳-----")
			continue

		if(boxX==0 or boxY==0 or manX==0 or manY ==0): #不正常
			print("不正常 ")
			im.show()
			im1.show()
			return
		# im1.show()

		distance = math.sqrt(math.pow(boxX-manX,2)+math.pow(boxY-manY,2))
		if(distance<200): #距离最小200
			print("-----距离最小200")
			distance=200
		t=getTime(distance)# 长按时间，根据距离算出
		endTime=time.time()
		print("距离 %d 时间=%d runTime=%f" % (distance,t,endTime-startTime))
		startTime=endTime
		longPress(t)

		# print("the curent thrading %s is running,scrreen %f time" % (threading.current_thread().name,time.time()-startTime))
		endTime=time.time()
		# print("run------%s"% (endTime-startTime))
		time.sleep(1) #单位s
		im.close()
		im1.close()
		# return

def getTime(distance):
	 # 时间=距离/速度
	return (int)(distance/0.7)

def getBoxXy(im,startx,starty):
	width,height = im.size

	def getBoxTop():
		for y in range(starty,height-160,1): #height-160
			for x in range(startx,width-25,2):
				rgb=im.getpixel((x,y))
				if(isLine(rgb)): # 0~127 黑色线条 新目标的最顶点
					addPoint1(im,x,y)
					# print("%d,%d r=%s" %(x,y,rgb))
					return x,y

	topX,topY=getBoxTop()
	for y in range(topY+400,topY,-1): # 从下往上找 盒子高不超过400
		for x in range(topX-2,topX+3):
			rgb=im.getpixel((x,y))
			# print("%d,%d r=%s" %(x,y,rgb))
			if(isLine(rgb)): # 0~127 黑色线条 新目标的最顶点
				addPoint1(im,topX,y)
				boxHeight=y-topY #新盒子的高
				# print("新目标的最顶点（%d,%d）最低点（%d,%d）盒子高=%d rgb=%s" % (topX,topY,topX,y,boxHeight,rgb))
				return topX,topY+(int)(boxHeight/3),topY
	return 0,0,0

def getManXy(im):
	maxy=1575
	maxx=940
	rightX=0
	leftX=0
	width,height = im.size
	isStart=False
	for y in range(maxy,10,-2): #step 为2，运算更快
		for x in range(maxx,10,-2):
			r,g,b= im.getpixel((x,y))
			# print(" X=%s y=%s rgb=%s %s %s" %(x,y,r,g,b))
			if not isStart and isManColor(manBottomRgb[0],r) and isManColor(manBottomRgb[1],g) and isManColor(manBottomRgb[2],b):
				rightX =x
				isStart=True
			elif isStart and not (isManColor(manBottomRgb[0],r) or isManColor(manBottomRgb[1],g) or isManColor(manBottomRgb[2],b)):
				leftX=x
				# print("rightX =%s leftX=%s y=%s" %(rightX,leftX,y))
				return (rightX+leftX)//2,y
	return 0,0

#是否为线条
def isLine(rgb):
	value=rgb[0]+rgb[1]+rgb[2]
	return value<=600

def isColor(color1,color2):
	return abs(color1-color2)<=15

def isManColor(color1,color2):
	return abs(color1-color2)<=5


def addPoint2(im,boxX,boxY):
	rgb=(0,0,0)

	minX=boxX
	if boxX>=5: minX = boxX-5
	minY =boxY
	if boxY>=5:minY=boxY-5
	for x in range(minX,boxX+5):
		im.putpixel((x,boxY),rgb)
	for y in range(minY,boxY+5):
		im.putpixel((boxX,y),rgb)

def addPoint1(im,boxX,boxY):
	rgb=(0,0,0)
	for i in range(boxX-10,boxX+10):
		im.putpixel((i,boxY),rgb)

def addPoint(im,boxX,boxY,rgb):
	minX=boxX
	if boxX>=5: minX = boxX
	minY =boxY
	if boxY>=5:minY=boxY-5
	for x in range(minX,boxX+5):
		for y in range(minY,boxY+5):
			im.putpixel((x,y),rgb)

def longPress(time):
	shell("adb -s %s shell input swipe 100 100 100 100 %d" % (divicesName,time)) #长按点


# print("the curent thrading %s is running" % (threading.current_thread().name))
getScreencap()
screenThread = threading.Thread(target=getScreencap)
# screenThread.start()
