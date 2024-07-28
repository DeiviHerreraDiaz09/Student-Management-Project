class Payment:
    def __init__(
        self,
        payment_date="",
        payment_paid="",
        payment_method="",
        invoice_id_fk="",
    ):
        self.payment_date = payment_date
        self.payment_paid = payment_paid
        self.payment_method = payment_method
        self.invoice_id_fk = invoice_id_fk