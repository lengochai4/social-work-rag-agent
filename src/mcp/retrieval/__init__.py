def __init__(
    self,
    model_name: str = "intfloat/multilingual-e5-base",
):
    self.model_name = model_name
    self.model = SentenceTransformer(model_name)