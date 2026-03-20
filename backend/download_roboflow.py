from roboflow import Roboflow
rf = Roboflow(api_key="M03WnVAoVTfYz6IZL4WA")
project = rf.workspace("aman-chaudhary-t2ivt").project("license-plate-detection-n9ped")
version = project.version(2)
dataset = version.download("yolov8")
