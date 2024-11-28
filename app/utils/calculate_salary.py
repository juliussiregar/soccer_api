from decimal import Decimal, ROUND_HALF_UP
from app.models.attendance import Attendance
from app.utils.exception import InternalErrorException
from app.utils.logger import logger


class CalculateSalary:
    def calculate_daily_salary(self, attendance: Attendance, daily_salary, late_minutes, overtime_minutes):
        """Menghitung gaji harian berdasarkan keterlambatan, lembur, dan jam kerja."""
        try:
            # Hitung jam kerja
            hours_worked = Decimal(
                (attendance.check_out - attendance.check_in).total_seconds() / 3600
            ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            # hours_worked = Decimal(8)

            # Gaji normal
            normal_salary = (Decimal(daily_salary.standard_hours) * Decimal(daily_salary.hours_rate)).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP)

            # Perhitungan lembur
            overtime_pay = Decimal(0)
            if overtime_minutes > daily_salary.min_overtime:  # Min overtime in minutes
                overtime_pay = Decimal(overtime_minutes / 60) * Decimal(daily_salary.overtime_rate)
                overtime_pay = overtime_pay.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            # Perhitungan pengurangan akibat keterlambatan
            late_deduction = Decimal(0)
            if late_minutes > daily_salary.max_late:  # Deduction applies only if late exceeds max_late
                excess_late_minutes = late_minutes - daily_salary.max_late
                total_excess_hours = Decimal(excess_late_minutes) / Decimal(60)
                late_deduction = (total_excess_hours * Decimal(daily_salary.late_deduction_rate)).quantize(
                    Decimal('0.01'), rounding=ROUND_HALF_UP
                )

            # Logging untuk debugging
            logger.info(f"Hours worked: {hours_worked}")
            logger.info(f"Normal salary: {normal_salary}")
            logger.info(f"Overtime pay: {overtime_pay}")
            logger.info(f"Late deduction: {late_deduction}")

            # Gaji yang disesuaikan
            adjusted_salary = (hours_worked * Decimal(daily_salary.hours_rate)).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP)

            # Total gaji
            total_salary = (adjusted_salary + overtime_pay - late_deduction).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            return {
                "hours_worked": hours_worked,
                "normal_salary": normal_salary,
                "overtime_pay": overtime_pay,
                "late_deduction": late_deduction,
                "total_salary": total_salary
            }
        except Exception as e:
            logger.error(f"Error calculating daily salary: {e}")
            raise InternalErrorException("Failed to calculate daily salary.")
