class Costings:
    def __init__(self) -> None:
        self.gpt_price_in = (3, 1000_000)
        self.gpt_price_out = (15, 1000_000)
        self.embedding_price = (0.0001, 1000)  

    def price_in(self, num_token):
        return self.gpt_price_in[0] * (num_token / self.gpt_price_in[1])
    
    def price_out(self, num_token):
        return self.gpt_price_out[0] * (num_token / self.gpt_price_out[1])
    
    def price_embeds(self, num_token):
        return self.embedding_price[0] * (num_token / self.embedding_price[1])