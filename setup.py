from setuptools import setup

setup(name='quadrenderer',
      version='0.1',
      description='A quadtree based IFF renderer',
      url='https://github.com/Henelik/AdaptiveResolution',
      author='Henelik',
      author_email='kelyn@crandall.me',
      license='MIT',
      packages=['renderer'],
      install_requires=[
          'opencv-python',
          'kivy',
          'scipy',
          'numpy',
          'numba',
      ],
      zip_safe=False)