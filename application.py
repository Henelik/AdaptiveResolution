from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.scatter import Scatter
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.textinput import TextInput
from kivy.graphics.transformation import Matrix
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.graphics import Rectangle

from quadrenderer.renderer import RealtimeQuadRenderer, RealtimeJuliaQuadRenderer, RealtimeCactusQuadRenderer, RealtimeGradientQuadRenderer, ScanRenderer

import imageio
import time
import os
import re

class RendererWidget(Widget):
	def __init__(self, res = 512, AA = 4, maxIters = 1000, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.res = res
		self.AA = AA
		self.maxIters = maxIters
		self.rampValue = 1
		self.fractal = 'mandelbrot'
		self.texture = Texture.create(size=(self.res, self.res), bufferfmt="ubyte", colorfmt = "bgr")
		self.juliacx = .3
		self.juliacy = .5
		with self.canvas:
			Rectangle(texture=self.texture, pos=(0, 0), size=(self.res, self.res))
		self.renderer = RealtimeQuadRenderer(res = self.res, AA = self.AA, maxIters = self.maxIters)
		self.renderer.begin()
		Clock.schedule_once(self.tick, 0)
		#print(App.get_running_app().path)

	def tick(self, dt):
		for i in range(150):
			if not self.renderer.tick():
				break
		if i != 0:
			self.renderer.updateImage()
			self.texture.blit_buffer(self.renderer.image.tostring(), bufferfmt="ubyte", colorfmt = "bgr")
			self.canvas.ask_update()
		Clock.schedule_once(self.tick, 0)

	def changeFractal(self, fractal):
		color = self.renderer.colorProfile.profileName
		if fractal == 'mandelbrot':
			self.renderer = RealtimeQuadRenderer(res = self.res, AA = self.AA, maxIters = self.maxIters)
		elif fractal == 'julia':
			self.renderer = RealtimeJuliaQuadRenderer(res = self.res, AA = self.AA, maxIters = self.maxIters)
			self.renderer.cx = self.juliacx
			self.renderer.cy = self.juliacy
		elif fractal == 'cactus':
			self.renderer = RealtimeCactusQuadRenderer(res = self.res, AA = self.AA, maxIters = self.maxIters)
		elif fractal == 'gradient':
			self.renderer = RealtimeGradientQuadRenderer(res = self.res, AA = self.AA, maxIters = self.maxIters)
		elif fractal == 'scanline':
			self.renderer = ScanRenderer(res = self.res, AA = self.AA, maxIters = self.maxIters)
		else:
			raise(TypeError)
		self.renderer.colorProfile.loadProfile(color)
		self.renderer.colorProfile.multiple = self.rampValue
		self.renderer.begin()
		self.fractal = fractal

	def changeColor(self, color):
		self.renderer.colorProfile.loadProfile(color)
		self.renderer.fullUpdateImage()
		self.texture.blit_buffer(self.renderer.image.tostring(), bufferfmt="ubyte", colorfmt = "bgr")
		self.canvas.ask_update()

	def changeColorMode(self, mode):
		self.renderer.colorSlice = mode
		self.renderer.fullUpdateImage()
		self.texture.blit_buffer(self.renderer.image.tostring(), bufferfmt="ubyte", colorfmt = "bgr")
		self.canvas.ask_update()

	def changeView(self, x, y, zoom):
		zr = self.renderer.cam.zoom/zoom
		self.renderer.cam.xPos -= x/self.renderer.cam.xRes*zr
		self.renderer.cam.yPos += y/self.renderer.cam.yRes*zr
		self.renderer.cam.zoom /= zoom
		self.renderer.begin()

	def changeRamp(self, value):
		if value != self.rampValue:
			self.rampValue = value
			self.renderer.colorProfile.multiple = value
			self.renderer.fullUpdateImage()

	def changeJuliacx(self, value):
		if value != self.juliacx:
			self.juliacx = value
			if self.fractal == 'julia':
				self.renderer.cx = value
				self.renderer.begin()

	def changeJuliacy(self, value):
		if value != self.juliacy:
			self.juliacy = value
			if self.fractal == 'julia':
				self.renderer.cy = value
				self.renderer.begin()

	def changeMaxIters(self, text):
		value = int(float(text))
		if value != self.maxIters:
			self.maxIters = value
			self.renderer.maxIters = value
			self.renderer.begin()
			self.changeRamp(self.rampValue)
		return str(value)

	def ensurePath(self, path):
		if not os.path.exists(path):
			os.makedirs(path)

	def saveImage(self):
		self.ensurePath(App.get_running_app().path + '/screenshots/')
		i = 0
		while os.path.exists(App.get_running_app().path + '/screenshots/' + self.fractal + str(i) + '.png'):
			i += 1
		imageio.imwrite(App.get_running_app().path + '/screenshots/' + self.fractal + str(i) + '.png', self.renderer.image[::-1, :, ::-1])

	def saveSettings(self):
		self.ensurePath(App.get_running_app().path + '/saves/')
		i = 0
		while os.path.exists(App.get_running_app().path + '/saves/' + self.fractal + str(i) + '.png'):
			i += 1
		file = open(App.get_running_app().path + '/saves/', 'w')
		file.write(str(self.renderer.cam.xPos))
		file.write(str(self.renderer.cam.yPos))
		file.write(str(self.renderer.cam.zoom))
		file.write(str(self.maxIters))
		file.write(str(self.juliacx))
		file.write(str(self.juliacy))
		file.write(str(self.fractal))
		file.write(str(self.colorSlice))
		file.write(str(self.renderer.colorProfile.profileName))
		file.write(str(self.rampValue))
		file.close()

	def loadSettings(self):
		self.ensurePath(App.get_running_app().path + '/saves/')


class RenderScatter(Scatter):
	def __init__(self, **kwargs):
		self.default_bbox = ()
		super().__init__(**kwargs)

	def on_touch_down(self, touch):
		if touch.is_mouse_scrolling:
			p = self.renderer.res*.05
			if touch.button == 'scrolldown':
				self.renderer.changeView(-p, -p, 1.1)
			elif touch.button == 'scrollup':
				self.renderer.changeView(p, p, .9)
		super().on_touch_down(touch)

	def on_touch_up(self, touch):
		if self.scale != 1 or self.transform[12] != 0 or self.transform[13] != 0:
			self.renderer.changeView(self.transform[12], self.transform[13], self.scale)
			self.transform.identity()
		super().on_touch_up(touch)

	def set_renderer(self, renderer):
		self.renderer = renderer
		self.add_widget(renderer)


class FloatInput(TextInput):
    pat = re.compile('[^0-9]')
    def insert_text(self, substring, from_undo=False):
        pat = self.pat
        if '.' in self.text:
            s = re.sub(pat, '', substring)
        else:
            s = '.'.join([re.sub(pat, '', s) for s in substring.split('.', 1)])
        return super(FloatInput, self).insert_text(s, from_undo=from_undo)


class RootWidget(FloatLayout):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.scatter = RenderScatter(auto_bring_to_front = False, do_rotation = False)
		self.renderer = RendererWidget(res = 1024, AA = 8, maxIters = 1000)
		self.scatter.set_renderer(self.renderer)
		self.add_widget(self.scatter, index = 3)


class QuadRendererApp(App):
	def build(self):
		self.title = 'Quadtree Renderer'
		self.path = str(self.user_data_dir)
		return RootWidget()

	def Quit(self):
		self.stop()


if __name__=="__main__":
	QuadRendererApp().run()
