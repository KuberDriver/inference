from torchvision import models, transforms
from PIL import Image
import flask
import torch
import torch.nn.functional as F
import json
import io
import urllib
import os

app = flask.Flask(__name__)
model = None


def initalize():
    global model
	global device
	device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = models.resnet18()
    model.load_state_dict(torch.load("model/resnet18-5c106cde.pth"))
    model.eval()
	model.to(device)
	
	global resnet_transform
    normalize = transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )

    resnet_transform = transforms.Compose([transforms.Resize(224),
                                           transforms.CenterCrop(224),
                                           transforms.ToTensor(), 
                                           normalize])     

    global labels
    json_file = open("model/imagenet_class_index.json")
    json_str = json_file.read()
    labels = json.loads(json_str)       

def transform_image(image):
    if image.mode != "RGB":
        image = image.convert("RGB")

    return resnet_transform(image)
      
@app.route("/predict", methods=["POST"])
def predict():
    data = {"success": False}

    if flask.request.method == "POST":
        if 1==1:
            url=flask.request.args.get('url')
            image = Image.open(urllib.request.urlopen(url))            
            image = transform_image(image)
            image = image.view(-1, 3, 224, 224)
            
            prediction = F.softmax(model(image)[0])
            topk_vals, topk_idxs = torch.topk(prediction, 3)
            
            data["predictions"] = []

            for i in range(len(topk_idxs)):
                r = {"label": labels[str(topk_idxs[i].item())][1], 
                     "probability": topk_vals[i].item()}
                data["predictions"].append(r)    

            data["success"] = True

    return flask.jsonify(data)      

if __name__ == "__main__":
    print("Loading infernce server")       
    initalize()
    app.run(host='0.0.0.0')

