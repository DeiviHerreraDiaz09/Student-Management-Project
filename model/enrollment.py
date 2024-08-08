class Enrollment:
    def __init__(
        self,
        enrollment_date: str = "",
        status: str = "",
        grade: str = "",
        enrollment_amount: int = 0,
        rate_id_fk: int = 0,
        period_id_fk: int = 0,
        student_id_fk: str = "",
    ):
        self.enrollment_date = (enrollment_date,)
        self.status = (status,)
        self.grade = (grade,)
        self.enrollment_amount = (enrollment_amount,)
        self.rate_id_fk = (rate_id_fk,)
        self.period_id_fk = (period_id_fk,)
        self.student_id_fk = (student_id_fk,)
