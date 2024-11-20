class CallResponse:
    def __init__(self, id: str, title: str, started: str, customer_name: str):
        self.id = id
        self.title = title
        self.started = started
        self.customer_name = customer_name

    def __repr__(self):
        return f"CallResponse(id={self.id}, title={self.title}, started={self.started}, customer_name={self.customer_name})"
