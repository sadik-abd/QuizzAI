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


import tiktoken

def calculate_token_usage(text, model_name='gpt2'):
    # Initialize the encoder for the specified model
    encoder = tiktoken.get_encoding(model_name)
    
    # Encode the text to get the tokens
    tokens = encoder.encode(text)
    
    # Calculate the total number of tokens
    total_tokens = len(tokens)
    
    return total_tokens
