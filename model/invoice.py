class Invoice:
    def __init__(
        self,
        description="",
        total_amount="",
        remaining_amount="",
        due_date="",
        created_at="",
        status="",
    ):
        self.description = description
        self.total_amount = total_amount
        self.remaining_amount = remaining_amount
        self.due_date = due_date
        self.created_at = created_at
        self.status = status