from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from app.models.attendance import Attendance
from app.utils.exception import InternalErrorException
from app.utils.logger import logger

class CalculateSalary:
    def calculate_daily_salary(self, attendance: Attendance, company, late_minutes, daily_salary):
        """Menghitung gaji harian berdasarkan keterlambatan, jam kerja, dan lembur."""
        try:
            # Jam kerja perusahaan
            company_start_time = datetime.combine(attendance.check_in.date(), company.start_time)
            company_end_time = datetime.combine(attendance.check_in.date(), company.end_time)

            # Hitung jam keterlambatan (dibulatkan ke atas per jam)
            late_hours = Decimal(0)
            if late_minutes > company.max_late:
                late_hours = Decimal((late_minutes + 59) // 60)  # Dibulatkan ke atas per jam

            # Hitung jam kerja standar
            standard_hours = Decimal(daily_salary.standard_hours)

            # Gaji dasar (tanpa pengurangan akibat keterlambatan)
            normal_salary = (standard_hours * Decimal(daily_salary.hours_rate)).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )

            # Hitung pengurangan akibat keterlambatan
            late_deduction = (late_hours * Decimal(daily_salary.hours_rate)).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )

            # Hitung jam kerja aktual
            actual_worked_duration = attendance.check_out - attendance.check_in
            actual_hours_worked = Decimal(actual_worked_duration.total_seconds() / 3600).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )

            # Hitung jam kerja yang dapat dibayarkan
            max_payable_hours = max(Decimal(0), standard_hours - late_hours)
            payable_hours = min(max_payable_hours, actual_hours_worked)
            total_salary = (payable_hours * Decimal(daily_salary.hours_rate)).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )

            # Hitung jam lembur
            overtime_hours = Decimal(0)
            if attendance.check_out > company_end_time:
                overtime_duration = attendance.check_out - company_end_time
                overtime_hours = Decimal(overtime_duration.total_seconds() / 3600).quantize(
                    Decimal('0.01'), rounding=ROUND_HALF_UP
                )

            # Logging untuk debugging
            logger.info(f"Actual hours worked: {actual_hours_worked}")
            logger.info(f"Late hours: {late_hours}")
            logger.info(f"Late deduction: {late_deduction}")
            logger.info(f"Payable hours: {payable_hours}")
            logger.info(f"Normal salary (no late): {normal_salary}")
            logger.info(f"Total salary: {total_salary}")
            logger.info(f"Overtime hours: {overtime_hours}")

            return {
                "hours_worked": actual_hours_worked,
                "late_hours": late_hours,
                "late_deduction": late_deduction,
                "payable_hours": payable_hours,
                "overtime_hours": overtime_hours,
                "normal_salary": normal_salary,
                "total_salary": total_salary
            }
        except Exception as e:
            logger.error(f"Error calculating daily salary: {e}")
            raise InternalErrorException("Failed to calculate daily salary.")
