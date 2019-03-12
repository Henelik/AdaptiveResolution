from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.graphics import Rectangle
from renderer import RealtimeQuadRenderer, RealtimeJuliaQuadRenderer, RealtimeCactusQuadRenderer, RealtimeGradientQuadRenderer

class RendererWidget(Widget):
	def __init__(self, *args):
		super().__init__(*args)
		self.res = 512
		self.AA = 8
		self.maxIters = 100
		self.texture = Texture.create(size=(self.res, self.res), bufferfmt="ubyte")#, colorfmt="rgb")
		with self.canvas:
			Rectangle(texture=self.texture, pos=(0, 0), size=(self.res, self.res))
		self.renderer = RealtimeQuadRenderer(res = self.res, AA = self.AA, maxIters = self.maxIters)
		self.renderer.begin()
		Clock.schedule_interval(self.tick, 1 / 30.)

	def tick(self, dt):
		for i in range(10):
			if not self.renderer.tick():
				break
		self.renderer.updateImage()
		self.texture.blit_buffer(self.renderer.image.tostring(), bufferfmt="ubyte")#, colorfmt="rgb")
		self.canvas.ask_update()

	def changeFractal(self, fractal):
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
			return
		self.renderer.begin()


class RootWidget(FloatLayout):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.renderer = RendererWidget()
		self.add_widget(self.renderer)


class RendererApp(App):
	def build(self):
		self.title = 'Quadtree Renderer'
		return RootWidget()

	def Quit(self):
		self.stop()


if __name__=="__main__":
	RendererApp().run()
