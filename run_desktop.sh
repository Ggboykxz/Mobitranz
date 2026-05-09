#!/bin/bash
# MobiTranz Desktop Admin - Launcher with Virtual Display

cd /workspaces/Mobitranz

# Check if xvfb is available
if command -v Xvfb &> /dev/null; then
    echo "🚀 Launching MobiTranz Admin with virtual display..."
    
    python3 -c "
from pyvirtualdisplay import Display
import os
import sys

# Start virtual display
display = Display(visible=0, size=(1280, 720))
display.start()
os.environ['DISPLAY'] = f':{display.display}'

sys.path.insert(0, '.')

from desktop_admin.main import MobiTranzAdminApp
app = MobiTranzAdminApp()
app.mainloop()

display.stop()
"
else
    echo "⚠️  Xvfb not found. Install with: sudo apt-get install xvfb"
    echo "Falling back to web interface..."
    cd /workspaces/Mobitranz/php_admin
    php -S 0.0.0.0:8003 -t .
fi