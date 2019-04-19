mkdir C:\Users\%USERNAME%\Documents\QuadtreeRendererDeploy
cd C:\Users\%USERNAME%\Documents\QuadtreeRendererDeploy
python -m PyInstaller --name quadrenderer C:\Users\%USERNAME%\Documents\QuadtreeRenderer\application.py
copy C:\Users\%USERNAME%\Documents\QuadtreeRenderer\dist\quadrenderer\quadrenderer.kv quadrenderer.kv
robocopy C:\Users\%USERNAME%\Documents\QuadtreeRenderer\dist\quadrenderer\color_profiles\ \\color_profiles\
PAUSE