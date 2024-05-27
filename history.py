import json

class ChatHistory:

    def __init__(self, name="hst1") -> None:
        self.recp_name = name
        self.data = []

    def add(self, usr, outp):

        self.data.append({"role":"user","content":usr})
        self.data.append({"role":"assistant","content":outp})
        self.save()

    def save(self):
        with open(self.recp_name + ".json","w") as fl:
            json.dump(self.data, fl,indent=4)


class User:
    def __init__(self) -> None:
        self.name = ""
        self.uuid = ""
        self.hisotry = ""
        self.docs = []
        self.json_file = []

    def save_docs(self):
        pass

    def save_feedbacks(self):
        pass