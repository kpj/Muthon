import tkFileDialog

import scipy
from scipy.io.wavfile import read

import time, wave, pymedia.audio.sound as sound
import pygame.mixer

import os, sys, random, pickle

class analyzer(object):
	def __init__(self):
		pygame.init()

		self.f = tkFileDialog.askopenfilename(initialdir="/home/kpj/Musik")
		if self.f == "":
			sys.exit()
		self.path = u"/".join(self.f.split(u"/")[:-1])
		self.name = self.f.split(u"/")[-1]
		
		self.f = self.check_wav(self.f)

		self.sample_rate, inp = read(self.f)
		self.audio = inp
		self.l = len(self.audio)
		self.ls = self.l / 10

	def start_msg(self):
		print 'Parsing: "%s"' % self.name
		print 'Got "%i" samples' % self.l
		print 'Sample rate: "%i"' % self.sample_rate
		print 'Length of wav-file: "%f" (seconds)' % (float(self.l) / int(self.sample_rate))

	def check_wav(self, fi):
		if fi[-3:] != "wav":
			output = "/tmp/%s.wav" % self.name
			print "No wav-file"
			print 'Converting "%s" in "%s"' % (self.name, self.path)
			#os.system('mplayer   -quiet   -vo null   -vc dummy   -ao pcm:waveheader:file="%s" "%s" 1>&2> /dev/null' % (output, fi))
			os.system('ffmpeg -i "%s" "%s"' % (fi.encode("utf-8"), output.encode("utf-8")))
			return output
		return fi
	
	def live_proc(self):
		self.start_msg()
		self.play_file(self.f)

	def play_file(self, song):
		sd = open(self.f, "rb")
		pygame.mixer.music.load(sd)
		pygame.mixer.music.play()

		self.create_window()
		self.obj_num = random.randint(40,60)

		self.gen_window_vars()

		while True:
			self.counter += 1
			cur_pos = pygame.mixer.music.get_pos()

			self.draw_window(self.get_average(cur_pos))

			time.sleep(0.01)

	def get_average(self, pos):
		cur_sample = int(pos * self.sample_rate / 1000)
		al = 0
		r = range(-int(self.sample_rate / 1000) + cur_sample, cur_sample)
		for p in r:
			try:
				al += self.audio[p][0]
			except IndexError:
				pass
		return float(al) / len(r)

	def gen_window_vars(self):
		self.mixer = []
		self.coords = []
		self.velo = []
		self.diff_size = []
		self.obj_type = []
		for i in range(self.obj_num):
			self.mixer.append([random.randint(0,1000), random.randint(0,1000), random.randint(0,1000)])
			self.coords.append((random.randint(0,self.screen_bound[0]), random.randint(0,self.screen_bound[1])))
			self.velo.append((random.randint(-3,3), random.randint(-3,3)))
			self.diff_size.append(random.randint(1,9))
			self.obj_type.append("circle_filled")

		self.sizer = 1
		self.counter = 0

	def create_window(self):
		self.screen_bound = (1440, 900)
		self.screen = pygame.display.set_mode(self.screen_bound, pygame.DOUBLEBUF|pygame.HWSURFACE)
		self.screen.fill((0,0,0,0))

		pygame.mixer.music.set_volume(0.5)

	def draw_window(self, cur):
		self.sizer += abs(cur) * 0.9999**(self.sizer)
		self.sizer *= 0.8
		if self.sizer <= 0: self.sizer = 0

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE:
					self.pausing()
				elif event.key == pygame.K_0:
					self.change_volume(0.1)
				elif event.key == pygame.K_9:
					self.change_volume(-0.1)

		self.screen.fill((0,0,0,0))

		# DRAW
		for i in range(self.obj_num):
			self.draw_figure(self.coords[i][0], self.coords[i][1], int(self.sizer / 100) / self.diff_size[i], (self.mixer[i][0] % 255, self.mixer[i][1] % 255, self.mixer[i][2] % 255, 0), self.obj_type[i])
		# DRAW

		pygame.display.update()
		self.check_borders()
		if self.counter % 5 == 0:
			self.calc_window()

	def change_volume(self, val):
		pygame.mixer.music.set_volume(pygame.mixer.music.get_volume() + val)

	def pausing(self):
		pygame.mixer.music.stop()

	def check_borders(self):
		for i in range(self.obj_num):
			if self.coords[i][0] < 0:
				self.coords[i] = (self.screen_bound[0], self.coords[i][1])
			if self.coords[i][1] < 0:
				self.coords[i] = (self.coords[i][0], self.screen_bound[1])
			if self.coords[i][0] > self.screen_bound[0]:
				self.coords[i] = (0, self.coords[i][1])
			if self.coords[i][1] > self.screen_bound[1]:
				self.coords[i] = (self.coords[i][0], 0)

	def calc_window(self):
		bounds = 1
		for i in range(self.obj_num):
			self.coords[i] = (self.coords[i][0] + self.velo[i][0], self.coords[i][1] + self.velo[i][1])

			self.mixer[i][0] += random.randint(-bounds,bounds+3)
			self.mixer[i][1] += random.randint(-bounds,bounds+3)
			self.mixer[i][2] += random.randint(-bounds,bounds+3)

	def draw_figure(self, x, y, size, col, art):
		if art == "circle_filled":
			pygame.draw.circle(self.screen, col, (x,y), size)
		elif art == "star_filled":
			pygame.draw.polygon(self.screen, col, [(x, y - size), (x + size/4, y - size/2), (x + size/3, y - size/2), (x + size/2, y), (x + size/3, y + size/2), (x + size/4, y +size/2), (x, y + size)])
		elif art == "ellipse_filled":
			pygame.draw.ellipse(self.screen, col, pygame.Rect((x,y),(x+size/4,y+size/8)))


analyzer().live_proc()
