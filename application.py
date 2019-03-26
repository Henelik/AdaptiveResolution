from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.scatter import Scatter
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics.transformation import Matrix
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.graphics import Rectangle
from renderer import RealtimeQuadRenderer, RealtimeJuliaQuadRenderer, RealtimeCactusQuadRenderer, RealtimeGradientQuadRenderer

class RendererWidget(Widget):
	def __init__(self, *args):
		super().__init__(*args)
		self.res = 512
		self.AA = 4
		self.maxIters = 1000
		self.texture = Texture.create(size=(self.res, self.res), bufferfmt="ubyte")#, colorfmt="rgb")
		with self.canvas:
			Rectangle(texture=self.texture, pos=(0, 0), size=(self.res, self.res))
		self.renderer = RealtimeQuadRenderer(res = self.res, AA = self.AA, maxIters = self.maxIters)
		self.renderer.begin()
		Clock.schedule_interval(self.tick, 1 / 30.)

	def tick(self, dt):
		for i in range(100):
			if not self.renderer.tick():
				break
		self.renderer.updateImage()
		self.texture.blit_buffer(self.renderer.image.tostring(), bufferfmt="ubyte")#, colorfmt="rgb")
		self.canvas.ask_update()

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
		self.renderer.begin()

	def setZoom(self, x, y, zoom):
		self.renderer.cam.zoom /= zoom
		self.renderer.cam.xPos -= x/self.renderer.cam.xRes*2
		self.renderer.cam.yPos += y/self.renderer.cam.yRes*2
		self.renderer.begin()


class RenderScatter(Scatter):
	def __init__(self, **kwargs):
		#self.default_bbox = self.bbox
		super().__init__(**kwargs)

	def on_touch_up(self, touch):
		print("Touch up")
		self.renderer.setZoom(self.transform[12], self.transform[13], self.scale)
		self.transform.identity()
		super().on_touch_up(touch)
		#self.bbox.set(self.default_bbox)

	def set_renderer(self, renderer):
		self.renderer = renderer
		self.add_widget(renderer)


class RootWidget(FloatLayout):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.scatter = RenderScatter(auto_bring_to_front = False, do_rotation = False)
		self.renderer = RendererWidget()
		self.scatter.set_renderer(self.renderer)
		self.add_widget(self.scatter)
		#self.add_widget(self.renderer)


class RendererApp(App):
	def build(self):
		self.title = 'Quadtree Renderer'
		return RootWidget()

	def Quit(self):
		self.stop()


if __name__=="__main__":
	RendererApp().run()
