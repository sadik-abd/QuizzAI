from models import QuizzGenModel
import json

model = QuizzGenModel()

outp = model.generate("./AdaDelta.pdf")
json.dump(outp,open("outp.json","w",encoding="utf-8"),indent=4)
print(outp)