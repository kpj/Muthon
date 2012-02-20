import tkFileDialog

import scipy
from scipy.io.wavfile import read
from scipy.signal import hann
from scipy.fftpack import rfft

import matplotlib.pyplot as plt

import time, wave, pymedia.audio.sound as sound
import pygame.mixer

import os, sys, random, pickle

class analyzer(object):
	def __init__(self):
		pygame.init()

		self.f = tkFileDialog.askopenfilename(initialdir="/home/kpj/Musik")
		#self.f = "/home/kpj/Musik/Hydrogen/test1.wav"
		#self.f = "/tmp/Cumfiesta - SexyGuy (DJ Solovey Electro remix)www.livingelectro.com.mp3.wav"
		self.path = u"/".join(self.f.split(u"/")[:-1])
		self.name = self.f.split(u"/")[-1]
		
		self.f = self.check_wav(self.f)

		self.accuracy = 1000 # Get average of every 'sampleRate / x' samples // outputSamples = accuracy * seconds
		self.save_dir = u"saves"

		self.sample_file_ending = u"[%i].sample" % self.accuracy

		if not self.check_save_dir():
			print 'No saves directory found, created one in "%s"' % self.save_dir

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
	
	def check_save_dir(self):
		try:
			os.listdir(self.save_dir)
			return True
		except OSError:
			os.mkdir(self.save_dir)
			return False

	def proc_ampl(self):
		self.start_msg()
		if not self.set_exists():
			print "Generating new file..."
			self.sampled_audio = []
			tmp = []
			prever = ""
			prev = ""
			for i, s in enumerate(self.audio):
				if i % 50000 == 0:
					prever = "[%s / %s]" % ('{:,}'.format(i), '{:,}'.format(self.l))
					prev = self.gen_bar(i, self.l, 30)
					outer = prev + " " + prever
					print outer + "\r" * len(outer) +" ",

				# CALC
				if i % (self.sample_rate / self.accuracy) != 0:
					tmp.append(s[1])
				else:
					l = 0
					for a in tmp:
						l += abs(a)
					if len(tmp) != 0:
						self.sampled_audio.append((( float(i) / self.sample_rate ), l / len(tmp)))
						del tmp[:]
					else:
						self.sampled_audio.append((( float(i) / self.sample_rate ), abs(s[1])))
# --> self.sampled_time.append(i / self.sample_rate)

				# CALC
			fd = open(os.path.join(self.save_dir, self.name + self.sample_file_ending), "wb")
			pickle.dump(self.sampled_audio, fd)
			fd.close()
			print prev
		else:
			print "Just using old file..."
			fd = open(os.path.join(self.save_dir, self.name + self.sample_file_ending), "rb")
			self.sampled_audio = pickle.load(fd)
			fd.close()

		# Can I haz milliseconds?
#		for audit in range(len(self.sampled_audio)):
#			self.sampled_audio[audit] = (self.sampled_audio[audit][0] * 1000, self.sampled_audio[audit][1])

		self.play_file(self.f)
#		plt.plot(self.sampled_audio)
#		plt.xlabel("Time")
#		plt.ylabel("Amplitude")
#		plt.title(self.name)
#		plt.show()

	def play_file(self, song):
		sd = open(self.f, "rb")
		pygame.mixer.music.load(sd)
		pygame.mixer.music.play()

		self.create_window()
		self.circle_num = random.randint(40,60)

		self.gen_window_vars()

		while True:
			self.counter += 1
			cur_pos = pygame.mixer.music.get_pos()

			self.visualize(self.sampled_audio[cur_pos][1])
			self.draw_window(self.sampled_audio[cur_pos][1])

			time.sleep(0.01)

	def gen_window_vars(self):
		self.mixer = []
		self.coords = []
		self.velo = []
		self.diff_size = []
		for i in range(self.circle_num):
			self.mixer.append([random.randint(0,1000), random.randint(0,1000), random.randint(0,1000)])
			self.coords.append((random.randint(0,self.screen_bound[0]), random.randint(0,self.screen_bound[1])))
			self.velo.append((random.randint(-3,3), random.randint(-3,3)))
			self.diff_size.append(random.randint(1,15))

		self.sizer = 1
		self.counter = 0

	def visualize(self, cur):
		l = int(cur / 1000)
		sys.stdout.write( " " + "|" * l + " " * 40 + "\r" * (l+40))
		sys.stdout.flush()

	def set_exists(self):
		if self.name + self.sample_file_ending in os.listdir(self.save_dir):
			return True
		return False

	def gen_bar(self, current, maximum, length = 10):
		current = float(current)
		maximum = float(maximum)
		length = float(length)
		perc = ( 100 / maximum ) * current
		if perc < 100:
			tile = length * ( perc / 100 )
			no = length - tile
		else:
			tile = length
			no = 0
		return "[" + "#" * int(tile) + "-" * int(no) + "]"

	def show_ampl(self):
		plt.plot([s for i,s in enumerate(self.audio) if i % self.sample_rate == 0])
		plt.xlabel("Time")
		plt.ylabel("Amplitude")
		plt.title(self.name)
		plt.show()

	def show_freq(self):
		inp = read(self.f)
		audio = inp[1]
		w = hann(self.ls)
		audio = self.audio[0:self.ls] #* w
		mags = abs(rfft(audio))
		#mags = 20 * scipy.log10(mags)
		#mags -= max(mags)
		plt.plot(mags)
		plt.ylabel("Magnitude")
		plt.xlabel("Frequency")
		plt.title(self.name)
		plt.show()
		
	def create_window(self):
		self.screen_bound = (1440, 900)
		self.screen = pygame.display.set_mode(self.screen_bound, pygame.DOUBLEBUF|pygame.HWSURFACE)
		self.screen.fill((0,0,0,0))

	def draw_window(self, cur):
		self.sizer += abs(cur)
		self.sizer *= 0.8
		if self.sizer <= 0: self.sizer = 0

		for event in pygame.event.get():
			if event.type == pygame.QUIT: sys.exit()
		self.screen.fill((0,0,0,0))

		# DRAW
		for i in range(self.circle_num):
			self.draw_figure(self.coords[i][0], self.coords[i][1], int(self.sizer / 100) / self.diff_size[i], (self.mixer[i][0] % 255, self.mixer[i][1] % 255, self.mixer[i][2] % 255, 0), "circle_filled")
		# DRAW

		pygame.display.update()
		self.check_borders()
		if self.counter % 5 == 0:
			self.calc_window()

	def check_borders(self):
		for i in range(self.circle_num):
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
		for i in range(self.circle_num):
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


a = analyzer()
#a.show_ampl()
a.proc_ampl()

#a.show_freq()
