from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.scatter import Scatter
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.stacklayout import StackLayout
from kivy.graphics.transformation import Matrix
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.graphics import Rectangle
from quadrenderer.renderer import RealtimeQuadRenderer, RealtimeJuliaQuadRenderer, RealtimeCactusQuadRenderer, RealtimeGradientQuadRenderer

import time

class RendererWidget(Widget):
	def __init__(self, res = 512, AA = 4, maxIters = 1000, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.res = res
		self.AA = AA
		self.maxIters = maxIters
		self.texture = Texture.create(size=(self.res, self.res), bufferfmt="ubyte", colorfmt = "bgr")
		with self.canvas:
			Rectangle(texture=self.texture, pos=(0, 0), size=(self.res, self.res))
		self.renderer = RealtimeQuadRenderer(res = self.res, AA = self.AA, maxIters = self.maxIters)
		self.renderer.begin()
		Clock.schedule_interval(self.tick, 1 / 30.)

	def tick(self, dt):
		#t = time.time()
		for i in range(150):
			if not self.renderer.tick():
				break
		#print("Total iteration time was " + str(time.time()-t))
		#t = time.time()
		self.renderer.updateImage()
		self.texture.blit_buffer(self.renderer.image.tostring(), bufferfmt="ubyte", colorfmt = "bgr")
		self.canvas.ask_update()
		#print("Total update time was " + str(time.time()-t))

	def changeFractal(self, fractal):
		color = self.renderer.colorProfile.profileName
		if fractal == 'mandelbrot':
			self.renderer = RealtimeQuadRenderer(res = self.res, AA = self.AA, maxIters = self.maxIters)
		elif fractal == 'julia':
			self.renderer = RealtimeJuliaQuadRenderer(res = self.res, AA = self.AA, maxIters = self.maxIters)
		elif fractal == 'cactus':
			self.renderer = RealtimeCactusQuadRenderer(res = self.res, AA = self.AA, maxIters = self.maxIters)
		elif fractal == 'gradient':
			self.renderer = RealtimeGradientQuadRenderer(res = self.res, AA = self.AA, maxIters = self.maxIters)
		else:
			raise(TypeError)
		self.renderer.colorProfile.loadProfile(color)
		self.renderer.begin()

	def changeColor(self, color):
		self.renderer.colorProfile.loadProfile(color)
		self.renderer.fullUpdateImage()

	def changeView(self, x, y, zoom):
		self.renderer.cam.xPos -= x/self.renderer.cam.xRes*self.renderer.cam.zoom/zoom
		self.renderer.cam.yPos += y/self.renderer.cam.yRes*self.renderer.cam.zoom/zoom
		self.renderer.cam.zoom /= zoom
		self.renderer.begin()


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


class RootWidget(FloatLayout):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.scatter = RenderScatter(auto_bring_to_front = False, do_rotation = False)
		self.renderer = RendererWidget(res = 1024, AA = 8)
		self.scatter.set_renderer(self.renderer)
		self.add_widget(self.scatter, index = 2)


class RendererApp(App):
	def build(self):
		self.title = 'Quadtree Renderer'
		return RootWidget()

	def Quit(self):
		self.stop()


if __name__=="__main__":
	RendererApp().run()
