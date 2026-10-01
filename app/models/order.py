class Order:
    def __init__(self, customer_name, total_amount=0, status="Pending"):
        self.customer_name = customer_name
        self.total_amount = total_amount
        self.status = status