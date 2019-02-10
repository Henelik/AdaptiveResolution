from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.graphics import Rectangle
from renderer import RealtimeQuadRenderer, FullRenderer

class MyWidget(Widget):
	def __init__(self):
		super().__init__()
		self.texture = Texture.create(size=(512, 512), colorfmt='rgb')
		with self.canvas:
			Rectangle(texture=self.texture, pos=(0, 0), size=(512, 512))
		#self.renderer = FullRenderer()
		#self.texture.blit_buffer(self.renderer.render().tostring(), bufferfmt="ubyte", colorfmt="rgb")
		self.renderer = RealtimeQuadRenderer(AA = 3)
		self.renderer.begin()
		Clock.schedule_interval(self.tick, 1 / 30.)

	def tick(self, dt):
		self.texture.blit_buffer(self.renderer.image.tostring(), bufferfmt="ubyte", colorfmt="rgb")
		for i in range(10):
			self.renderer.tick()
		self.renderer.updateImage()
		self.canvas.ask_update()


class WidgetsApp(App):
	def build(self):
		return MyWidget()


if __name__=="__main__":
	WidgetsApp().run()