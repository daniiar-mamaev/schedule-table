import os

from fastapi.templating import Jinja2Templates

current_dir = os.path.dirname(os.path.realpath(__file__))
template_dir = os.path.join(current_dir, ".", "templates")
templates = Jinja2Templates(directory=template_dir)
