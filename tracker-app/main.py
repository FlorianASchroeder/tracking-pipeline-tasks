from mangum import Mangum

from tracker_app.main import app

handler = Mangum(app)
