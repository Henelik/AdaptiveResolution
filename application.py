from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.graphics import Rectangle
from renderer import RealtimeQuadRenderer, FullRenderer

class RendererWidget(Widget):
	def __init__(self):
		super().__init__()
		res = 512
		self.texture = Texture.create(size=(res, res), colorfmt='rgb')
		with self.canvas:
			Rectangle(texture=self.texture, pos=(0, 0), size=(res, res))
		self.renderer = RealtimeQuadRenderer(res = res, AA = 3, maxIters = 100)
		self.renderer.begin()
		Clock.schedule_interval(self.tick, 1 / 30.)

	def tick(self, dt):
		self.texture.blit_buffer(self.renderer.image.tostring(), bufferfmt="ubyte", colorfmt="rgb")
		for i in range(10):
			self.renderer.tick()
		self.renderer.updateImage()
		self.canvas.ask_update()


class RendererApp(App):
	def build(self):
		self.title = 'Quadtree Renderer'
		return RendererWidget()


if __name__=="__main__":
	RendererApp().run()