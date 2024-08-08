class Student:
    def __init__(
        self,
        student_ident="",
        student_name="",
        date_of_birth="",
        tutor_dni="",
        tutor_name="",
        tutor_email="",
        tutor_phone="",
        address="",
        status="",
    ):
        self.student_ident = student_ident
        self.student_name = student_name
        self.date_of_birth = date_of_birth
        self.tutor_dni = tutor_dni
        self.tutor_name = tutor_name
        self.tutor_email = tutor_email
        self.tutor_phone = tutor_phone
        self.address = address
        self.status = status
